import os
import sys
import time
import shlex
import subprocess
from datetime import datetime
from colorama import Fore, Style
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

from src import utils

def estimate_size_of_backup(paths):
    """
    Estimate the size of the files on android device.
    
    Since files will be compressed, returned size is not fully accurate,
    
    but it is enough to provide reasonable approximation for progress tracking purposes.
    
    Args:
        paths (str): Paths to the files on android device.
    
    Returns:
        int: Estimated size of the files on the device in bytes.
    """
    output, error, return_code = utils.run_command(["adb", "shell", "cd /sdcard && du -csb", paths])
    if return_code != 0:
        sys.exit(f"\n{Fore.RED}Error estimating size:\n{error}\nOne or more paths do not exist. Please check your config file.")
    return int(output.splitlines()[-1].split()[0]) if output else 0

def remove_files_from_device(paths):
    """
    Remove already backed up files from android device.
    
    Args:
        paths (str): Paths to the files on the device.
    """
    
    print("Removing items from Android device:")
    for path in shlex.split(paths):
        escaped_path = shlex.quote(path).replace(' ', '\\ ')
        _, error, return_code = utils.run_command(["adb", "shell", "rm -rf", f"'/sdcard/{escaped_path}'"])
        if return_code != 0:
            print(f"{Fore.RED}Error removing {path}: {error}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Removed: {path}{Style.RESET_ALL}")    
            

def backup(config, delete=False):
    """
    Backup files listed in the config file. Set `delete` to remove files from android device after backup.
    
    Args:
        config (str): Path to the configuration file.
        delete (bool): If True, remove files from the device after backup.
    """

    utils.check_adb_connection()
    
    output, paths = utils.load_config(config)
    
    # Replace `$date$` and `$time$` placeholders with current date and time
    now = datetime.now()
    output = output.replace("$date$", now.strftime("%Y-%m-%d")).replace("$time$", now.strftime("%H-%M"))
    
    # Create directory structure if it doesn't exist yet
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    estimated_size = estimate_size_of_backup(paths)
    
    adb_command = ["adb", "exec-out", "cd /sdcard && tar -cpf -", paths]

    try:
        print(f"\n{Fore.GREEN}[Backup]{Style.RESET_ALL} {Fore.CYAN}{output}{Style.RESET_ALL}\n")
        start_time = time.time()
        
        with open(output, "wb") as file:
            with subprocess.Popen(adb_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:                  
                with Progress(
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TextColumn("•"),
                    TextColumn("{task.completed:.2f} MB"),
                    TextColumn("of"),
                    TextColumn("{task.total:.2f} MB"),
                    TextColumn("•"),
                    TimeRemainingColumn()) as progress:

                    task = progress.add_task("", total=estimated_size / (1000 * 1000))

                    chunk_size = 32 * 1024 * 1024 
            
                    for chunk in iter(lambda: process.stdout.read(chunk_size), b''):
                        file.write(chunk)
                        progress.update(task, advance=len(chunk) / (1000 * 1000))

                _, error = process.communicate()
                if process.returncode == 0:
                    print(f"\nBackup transferred successfully in {Fore.CYAN}{time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))}{Style.RESET_ALL}\n")
                else:
                    print(f"{Fore.RED}Backup failed. Error: {error.decode('utf-8')}{Style.RESET_ALL}")
                    return False
    except PermissionError:
        print(f"\n{Fore.RED}Permission denied:\nUnable to write to {output}.{Style.RESET_ALL}")
        return False
    
    # After successful backup, remove files from device if requested
    if process.returncode == 0 and delete:
        remove_files_from_device(paths)