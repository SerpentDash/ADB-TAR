import os
import shlex
import tarfile
import time
import shutil
from colorama import Fore, Style

from src import utils

def get_android_file_size(file):
    """
    Get the size of a file on android device.
    
    Args:
        file (str): The path to the file on the android device.
        
    Returns:
        int: The size of the file in bytes, or None if the file does not exist.
    """
    output, _, return_code  = utils.run_command(['adb', 'shell', f"stat -c '%s' {shlex.quote(file)}"])
    return int(output) if return_code == 0 else None

def check(output, verbose=False):
    """
    Compare files on android device with tar archive content. Set `verbose` to print each file.
    
    Args:
        output (str): The path to the tar archive.
        verbose (bool): If True, print each file.
    """
    
    utils.check_adb_connection()
    
    utils.check_file_exists(output)
    
    passed_count = failed_count = total_count = 0
    
    with tarfile.open(os.path.abspath(output), 'r') as tar:
        items = tar.getmembers()
        total_items = len(items)
    
    print(f"\n{Fore.GREEN}[Check]{Style.RESET_ALL} {Fore.CYAN}{os.path.abspath(output)}{Style.RESET_ALL}\n")
    
    #print(f"Item will {Fore.GREEN}PASS{Style.RESET_ALL} if it exists on the device AND its size matches the size in the archive.")
    #print(f"Item will {Fore.RED}FAIL{Style.RESET_ALL} if it either does not exist on the device OR does not match the size in the archive")
    
    print(f"Total items to check: {Fore.YELLOW}{total_items}{Style.RESET_ALL}\n")
    
    if verbose:
        terminal_width, _ = shutil.get_terminal_size()
        name_width = terminal_width - 32  # Adjust based on other columns and padding
        name_width = max(name_width, 10)  # Ensure a minimum width for the name column
        print(f"{'Test':<4} | {'Type':<4} | {'Name':<{name_width}} | {'Size (bytes)':<12}")
        print("-" * terminal_width)

    start_time = time.time()

    for item in items:
        total_count += 1
        android_path = f"/sdcard/{item.name}"
        android_size = get_android_file_size(android_path)
        
        if android_size is not None and (item.isdir() or item.size == android_size):
            status = f"{Fore.GREEN}{'PASS':<4}{Style.RESET_ALL}"
            passed_count += 1
        else:
            status = f"{Fore.RED}{'FAIL':<4}{Style.RESET_ALL}"
            failed_count += 1
        
        if verbose:
            name_display = (item.name[:name_width - 3] + '...') if len(item.name) > name_width else item.name
            size = '' if item.isdir() else f"{item.size:<12}"
            print(f"{status} | {('dir' if item.isdir() else 'file'):<4} | {name_display:<{name_width}} | {size}")
        else:
            print(f"\rPassed: {Fore.GREEN}{passed_count}{Style.RESET_ALL} | Failed: {Fore.RED if failed_count > 0 else ''}{failed_count}{Style.RESET_ALL}", end='', flush=True)
            
    if verbose:
        print(f"\nPassed: {Fore.GREEN}{passed_count}{Style.RESET_ALL} | Failed: {Fore.RED if failed_count > 0 else ''}{failed_count}{Style.RESET_ALL} | Total: {total_count}", end='')
    
    print(f"\n\nIntegrity checked in {Fore.CYAN}{time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))}{Style.RESET_ALL}\n")