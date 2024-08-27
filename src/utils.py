import os
import sys
import json
import subprocess
from colorama import Fore, Style

def load_config(config_path):
    """
    Load configuration from JSON file.
    
    Args:
        config_path (str): Path to the configuration file.
    
    Returns:
        tuple: Tuple containing the `output` (backup path) and `files` (array with paths to backup).
    """
    
    check_file_exists(config_path)
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        sys.exit(f"{Fore.RED}Invalid JSON file format.{Style.RESET_ALL}")
        
    if 'output' not in config or 'paths' not in config:
        sys.exit(f"{Fore.RED}Missing required keys in config file: 'output' and 'paths'{Style.RESET_ALL}")
        
    return os.path.abspath(config['output']), ' '.join(path.replace(' ', '\\ ') for path in config['paths'])

def run_command(command):
    """
    Run android shell command.
    
    Args:
        command (str): The command to run.
    
    Returns:
        tuple: Tuple containing the `output`, `error` and `return code`.
    """
    
    process = subprocess.run(command, capture_output=True, text=True)
    
    return process.stdout.strip(), process.stderr.strip(), process.returncode

def check_adb_connection():
    """Check if Android device is connected and authorized to ADB."""
    
    if run_command(["adb", "get-state"])[2] != 0:
        sys.exit(f"{Fore.RED}No Android device connected or device not authorized.{Style.RESET_ALL}")
        
    print(f"Connected to: {Fore.CYAN}" + '\n'.join(run_command(["adb", "devices"])[0].splitlines()[1:]) + f"{Style.RESET_ALL}")

def check_file_exists(file_path):
    """
    Check if file exists on desktop.
    
    Args:
        file_path (str): Path to the file.
    """
    
    if not os.path.exists(file_path):
        sys.exit(f"{Fore.RED}File {file_path} does not exist.{Style.RESET_ALL}")
        