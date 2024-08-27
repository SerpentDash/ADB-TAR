import argparse
from colorama import init, Fore, Style

from src.backup import backup
from src.restore import restore
from src.check import check

if __name__ == "__main__":
    # Initialize colorama
    init(autoreset=True)
    
    print(f"\n{Fore.GREEN}ADB-TAR{Style.RESET_ALL}\n")
    
    parser = argparse.ArgumentParser()
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-b', dest="backup", metavar='config.json', help='backup paths listed in config file')
    group.add_argument('-r', dest="restore", metavar='backup.tar', help='restore from specified tar file')
    group.add_argument('-c', dest="check", metavar='backup.tar', help='compare content of tar file with device')

    parser.add_argument('-d', dest="delete", action='store_true', help='remove transferred files from device when using (-b)')
    parser.add_argument('-v', dest="verbose", action='store_true', help='print each file when using (-c)')

    args = parser.parse_args()

    if args.backup:
        backup(args.backup, args.delete)
    elif args.restore:
        restore(args.restore)
    elif args.check:
        check(args.check, args.verbose)