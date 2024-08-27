import os
import time
import subprocess
from colorama import Fore, Style
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

from src import utils

def restore(output):
    """
    Restore files from tar archive (on desktop) to android device.
    
    Args:
        output (str): The path to the tar archive.
    """
    
    utils.check_adb_connection()
    
    utils.check_file_exists(output)
    
    file_size = os.path.getsize(output)
    adb_command = ["adb", "exec-in", "tar -xpf - -C /sdcard"]

    start_time = time.time()
    print(f"\n{Fore.GREEN}[Restore]{Style.RESET_ALL} {Fore.CYAN}{os.path.abspath(output)}{Style.RESET_ALL}\n")
    
    with open(output, "rb") as f:
        with subprocess.Popen(adb_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
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
            
                task = progress.add_task("", total=file_size / (1000 * 1000))

                chunk_size = 32 * 1024 * 1024 
                
                for chunk in iter(lambda: f.read(chunk_size), b''):
                    process.stdin.write(chunk)
                    process.stdin.flush()
                    
                    process.stdout.flush()
                    process.stderr.flush()
                    progress.update(task, advance=len(chunk) / (1000 * 1000))
                    time.sleep(1)

                _, error = process.communicate()
                process.stdin.close()

    if process.returncode == 0:
        print(f"\nBackup restored successfully in {Fore.CYAN}{time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))}{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.RED}Restoration failed. Error: {error.decode('utf-8')}{Style.RESET_ALL}")