import logging
from nornir import InitNornir
from nornir.core.filter import F
from nornir_netmiko.tasks import netmiko_send_command
from colorama import Fore, Style, init

# Initialize Colorama for colored output
init(autoreset=True)

# Disable Nornir logs
logging.getLogger("nornir").setLevel(logging.CRITICAL)

def verify_switch_state(task):
    """
    Verifies Layer 2 Switch Configuration: VLANs, Trunking, Access Ports.
    """
    results = {"vlans": False, "trunk": False, "access": False}
    
    # 1. Check VLANs (Using short command 'vl')
    vlan_out = task.run(netmiko_send_command, command_string="vl").result
    
    required_vlans = ["10", "20", "30", "40"]
    missing = [v for v in required_vlans if v not in vlan_out]
    
    if not missing:
        results["vlans"] = True
    else:
        results["vlans_msg"] = f"Missing: {missing}"

    # 2. Check Trunk (Fa4/0)
    trunk_out = task.run(netmiko_send_command, command_string="show interfaces trunk").result
    if "Fa4/0" in trunk_out and "trunking" in trunk_out:
        results["trunk"] = True
    else:
        results["trunk_msg"] = "Fa4/0 is not trunking"

    # 3. Check Access Port (Fa4/1)
    int_out = task.run(netmiko_send_command, command_string="show interfaces FastEthernet4/1 switchport").result
    if "Access Mode VLAN: 10" in int_out:
        results["access"] = True
    else:
        results["access_msg"] = "Fa4/1 not in VLAN 10"

    return results

def verify_router_state(task):
    """
    Verifies Layer 3 Router Configuration based on Role (Hub vs Spoke).
    """
    role = task.host.get("role", "spoke")
    
    results = {
        "role": role, 
        "ospf": False, 
        "wan": False, 
        "nat": "N/A", 
        "vpn": "N/A"
    }

    # --- GLOBAL CHECKS (All Routers) ---

    # 1. Check OSPF Neighbors
    ospf_out = task.run(netmiko_send_command, command_string="show ip ospf neighbor").result
    if "FULL" in ospf_out:
        results["ospf"] = True
    else:
        results["ospf_msg"] = "No FULL neighbors found"

    # 2. Check WAN Interface Status
    ip_out = task.run(netmiko_send_command, command_string="show ip int brief").result
    if ("GigabitEthernet1/0" in ip_out and "up" in ip_out) or \
       ("GigabitEthernet2/0" in ip_out and "up" in ip_out):
         results["wan"] = True
    else:
         results["wan_msg"] = "WAN Interface Down"

    # --- SPOKE ONLY CHECKS ---
    if role == 'spoke':
        # 3. Check NAT
        nat_out = task.run(netmiko_send_command, command_string="show ip nat statistics").result
        if "Total active translations" in nat_out or "Outside interface" in nat_out:
            results["nat"] = True
        else:
            results["nat_msg"] = "NAT not initialized"

        # 4. Check VPN
        crypto_out = task.run(netmiko_send_command, command_string="show crypto map").result
        if "Crypto Map" in crypto_out and "Interfaces using crypto map" in crypto_out:
            results["vpn"] = True
        else:
            results["vpn_msg"] = "No Crypto Map applied"

    return results

def print_report(results, device_type):
    """
    Prints the report and returns a list of failures found.
    """
    print(f"\n{Style.BRIGHT}--- {device_type.upper()} REPORT ---{Style.RESET_ALL}")
    
    failures_found = []

    for host, multi_result in results.items():
        # Handle execution errors (e.g. connection timeout)
        if multi_result.failed:
            error_text = f"{host}: Execution Failed (Connection/Auth Error)"
            print(f"\nDEVICE: {Style.BRIGHT}{host}{Style.RESET_ALL}")
            print(f"  [{Fore.RED}CRITICAL{Style.RESET_ALL}] {error_text}")
            failures_found.append(error_text)
            continue

        data = multi_result[0].result
        print(f"\nDEVICE: {Style.BRIGHT}{host}{Style.RESET_ALL}")

        if device_type == "switch":
            checks = [
                ("VLAN Database", data["vlans"], data.get("vlans_msg")),
                ("Uplink Trunk", data["trunk"], data.get("trunk_msg")),
                ("Access Ports", data["access"], data.get("access_msg"))
            ]
        else:
            checks = [
                ("WAN Interface", data["wan"], data.get("wan_msg")),
                ("OSPF Adjacency", data["ospf"], data.get("ospf_msg")),
            ]
            if data.get("role") == "spoke":
                checks.append(("NAT Configuration", data["nat"], data.get("nat_msg")))
                checks.append(("VPN (Crypto Map)", data["vpn"], data.get("vpn_msg")))

        # Iterate through checks for this device
        for name, status, error_msg in checks:
            if status is True:
                print(f"  [{Fore.GREEN}PASS{Style.RESET_ALL}] {name}")
            else:
                print(f"  [{Fore.RED}FAIL{Style.RESET_ALL}] {name} - {error_msg}")
                # Add failure to the list
                failures_found.append(f"{host}: {name} ({error_msg})")
    
    print("-" * 40)
    return failures_found

def main():
    nr = InitNornir(config_file="config.yaml")
    
    switches = nr.filter(F(type="switch"))
    routers = nr.filter(F(type="router"))

    print("\n🔍 Running Network Verification...\n")

    # Accumulate all failures from both reports
    all_failures = []

    if len(switches.inventory.hosts) > 0:
        switch_fails = print_report(switches.run(task=verify_switch_state), "switch")
        all_failures.extend(switch_fails)

    if len(routers.inventory.hosts) > 0:
        router_fails = print_report(routers.run(task=verify_router_state), "router")
        all_failures.extend(router_fails)

    # --- FINAL CONCLUSION ---
    print("\n" + "="*50)
    if len(all_failures) == 0:
        # SUCCESS MESSAGE
        print(f"{Fore.GREEN}{Style.BRIGHT}✅ VERIFICATION SUCCESSFUL: All checks passed!{Style.RESET_ALL}")
    else:
        # FAILURE SUMMARY
        print(f"{Fore.RED}{Style.BRIGHT}❌ VERIFICATION FAILED: Found {len(all_failures)} issues.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}\nSummary of Failures:{Style.RESET_ALL}")
        for failure in all_failures:
            print(f" - {failure}")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
