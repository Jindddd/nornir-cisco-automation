# debug_vars.py
from nornir import InitNornir
from colorama import init, Fore, Style

init(autoreset=True)

def main():
    print(f"{Style.BRIGHT}--- Nornir Variable Debugger ---")
    
    # 1. Initialize Nornir
    try:
        nr = InitNornir(config_file="config.yaml")
    except Exception as e:
        print(f"{Fore.RED}CRITICAL: Could not load config.yaml")
        print(e)
        return

    # 2. Pick a test device (SW1)
    target_host = "SW1"
    
    if target_host not in nr.inventory.hosts:
        print(f"{Fore.RED}Host {target_host} not found in inventory!")
        return

    host = nr.inventory.hosts[target_host]
    
    # 3. Check for 'vlans' variable
    print(f"Inspecting Host: {Fore.CYAN}{target_host}")
    
    # Check directly in the data dictionary
    if "vlans" in host.data:
        print(f"Variable 'vlans': {Fore.GREEN}FOUND")
        print(f"Value: {host['vlans']}")
    else:
        print(f"Variable 'vlans': {Fore.RED}MISSING")
        print(f"{Fore.YELLOW}Reason: defaults.yaml is likely not linked in config.yaml")

    # 4. Check Config File Settings
    print(f"\n{Style.BRIGHT}--- Config File Check ---")
    inventory_options = nr.config.inventory.options
    print(f"Inventory Options Detected: {inventory_options}")
    
    if 'defaults_file' in inventory_options:
        print(f"Defaults File Setting: {Fore.GREEN}{inventory_options['defaults_file']}")
    else:
        print(f"Defaults File Setting: {Fore.RED}NOT FOUND in config.yaml options!")

if __name__ == "__main__":
    main()
