import logging
from nornir import InitNornir
from nornir.core.filter import F
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result

# Disable internal Nornir logs to keep output clean
logging.getLogger("nornir").setLevel(logging.CRITICAL)

def verify_router(task):
    """
    Checks Interfaces, OSPF, NAT, and VPN status on Routers.
    """
    # 1. Check Interface Status (Are IPs correct? Are they UP?)
    task.run(
        task=netmiko_send_command,
        name="Interface Status",
        command_string="show ip interface brief | exclude unassigned"
    )

    # 2. Check OSPF Neighbors (Are R1/R2 peering with Core?)
    task.run(
        task=netmiko_send_command,
        name="OSPF Neighbors",
        command_string="show ip ospf neighbor"
    )

    # 3. Check NAT Configuration (Only if NAT is enabled for this host)
    if task.host.get("enable_nat"):
        task.run(
            task=netmiko_send_command,
            name="NAT Statistics",
            command_string="show ip nat statistics"
        )

    # 4. Check VPN Crypto Map (Is the map applied to an interface?)
    task.run(
        task=netmiko_send_command,
        name="Crypto Map Status",
        command_string="show crypto map"
    )

def verify_switch(task):
    """
    Checks VLANs and Management SVI on Switches.
    """
    # 1. Check VLAN Database
    task.run(
        task=netmiko_send_command,
        name="VLAN Database",
        command_string="vl"
    )

    # 2. Check Trunk Ports
    task.run(
        task=netmiko_send_command,
        name="Trunk Ports",
        command_string="show interfaces trunk"
    )

def main():
    nr = InitNornir(config_file="config.yaml")

    print("--- Verifying Network Configuration ---")

    # Filter Inventory
    switches = nr.filter(F(type="switch"))
    routers = nr.filter(F(type="router"))

    # Run Router Checks
    if len(routers.inventory.hosts) > 0:
        print(f"\n{'-'*20} ROUTER DIAGNOSTICS {'-'*20}")
        result_routers = routers.run(task=verify_router)
        print_result(result_routers)

    # Run Switch Checks
    if len(switches.inventory.hosts) > 0:
        print(f"\n{'-'*20} SWITCH DIAGNOSTICS {'-'*20}")
        result_switches = switches.run(task=verify_switch)
        print_result(result_switches)

if __name__ == "__main__":
    main()
