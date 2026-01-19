import os
import platform
import subprocess
import yaml
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

def load_inventory(file_path="inventory/hosts.yaml"):
    """Loads the Nornir hosts.yaml file."""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}Error: Could not find {file_path}")
        print(f"{Fore.YELLOW}Make sure you are running this script from the project root directory.")
        exit(1)

def ping_ip(ip_address):
    """
    Pings an IP address. 
    Returns True if reachable, False if not.
    """
    # Determine the OS to use correct ping flags
    # Windows uses -n, Linux/Mac uses -c
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    
    # Ping 1 time, wait max 2 seconds (timeout helps speed up failed checks)
    command = ['ping', param, '1', ip_address]
    
    # Suppress output (stdout and stderr) so the console stays clean
    try:
        response = subprocess.run(
            command, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        return response.returncode == 0
    except Exception as e:
        print(f"Error executing ping: {e}")
        return False

def main():
    print(f"\n{Style.BRIGHT}--- Network Connectivity Check ---{Style.RESET_ALL}\n")
    
    hosts = load_inventory()
    
    success_count = 0
    fail_count = 0
    
    # Iterate through all hosts in the inventory
    for host_name, host_data in hosts.items():
        mgmt_ip = host_data.get('hostname')
        
        if not mgmt_ip:
            print(f"{Fore.YELLOW}[SKIP] {host_name}: No IP configured")
            continue

        print(f"Pinging {host_name} ({mgmt_ip})... ", end='', flush=True)
        
        if ping_ip(mgmt_ip):
            print(f"{Fore.GREEN}SUCCESS")
            success_count += 1
        else:
            print(f"{Fore.RED}FAILED")
            fail_count += 1

    print(f"\n{Style.BRIGHT}--- Summary ---")
    print(f"Total Hosts: {len(hosts)}")
    print(f"{Fore.GREEN}Reachable:   {success_count}")
    print(f"{Fore.RED}Unreachable: {fail_count}")
    
    if fail_count > 0:
        print(f"\n{Fore.RED}CRITICAL: Fix connectivity issues before running Nornir.")
        print(f"1. Check if the devices are powered on.")
        print(f"2. Verify the management IPs are correct in hosts.yaml.")
        print(f"3. Ensure your controller (192.168.1.1) can reach the management network.")
    else:
        print(f"\n{Fore.GREEN}READY: All devices are reachable. You may proceed with deployment.")

if __name__ == "__main__":
    main()
