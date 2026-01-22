import socket
import platform
import subprocess
import yaml
import time
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def load_inventory(file_path="inventory/hosts.yaml"):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def check_ping(ip):
    """
    Returns True if IP is reachable via ICMP Ping.
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    # Sending 2 packets helps with ARP resolution (if 1st drops, 2nd usually works)
    cmd = ['ping', param, '2', ip]
    try:
        return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
    except:
        return False

def check_socket(ip, port, retries=3, delay=1):
    """
    Returns True if TCP port is open. 
    Includes retries to handle ARP resolution or initial NAT delay.
    """
    for attempt in range(retries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3) # Increased timeout slightly
                s.connect((ip, int(port)))
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            # If failed, wait and try again (ARP might be resolving)
            if attempt < retries - 1:
                time.sleep(delay)
                
    return False

def main():
    print(f"\n{Style.BRIGHT}--- Connectivity Check (NAT/Routed) ---{Style.RESET_ALL}\n")
    
    try:
        hosts = load_inventory()
    except FileNotFoundError:
        print(f"{Fore.RED}Error: inventory/hosts.yaml not found!{Style.RESET_ALL}")
        return

    failures = []

    for name, data in hosts.items():
        ip = data.get('hostname')
        port = data.get('port', 22) # Default to 22 if not specified in YAML
        
        print(f"Device: {name:<12} | Target: {ip}:{port:<5} ... ", end='', flush=True)

        if not ip:
            print(f"{Fore.YELLOW}SKIP (No IP){Style.RESET_ALL}")
            failures.append(f"{name} (No IP)")
            continue

        # Logic: If Port 22, use Ping. If Port != 22, use TCP Check.
        success = False
        if port == 22:
            if check_ping(ip):
                print(f"{Fore.GREEN}PING OK{Style.RESET_ALL}")
                success = True
            else:
                print(f"{Fore.RED}FAIL (Unreachable){Style.RESET_ALL}")
        else:
            if check_socket(ip, port):
                print(f"{Fore.GREEN}PORT OK (NAT Works){Style.RESET_ALL}")
                success = True
            else:
                print(f"{Fore.RED}FAIL (Port Closed){Style.RESET_ALL}")
        
        if not success:
            failures.append(name)
    
    # --- SUMMARY SECTION ---
    print("\n" + "="*60)
    if not failures:
        print(f"{Fore.GREEN}✅ SUCCESS: All {len(hosts)} devices are reachable.{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🚀 You can PROCEED with the deployment.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ FAILURE: {len(failures)} device(s) failed connectivity check.{Style.RESET_ALL}")
        print(f"{Fore.RED}   Failed Devices: {', '.join(failures)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️  Please fix connectivity issues before proceeding.{Style.RESET_ALL}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()