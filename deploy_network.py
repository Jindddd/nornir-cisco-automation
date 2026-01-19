import logging
import os
from datetime import datetime
from halo import Halo  # Replaces tqdm
from nornir import InitNornir
from nornir.core.filter import F
from nornir_netmiko.tasks import netmiko_send_config
from nornir_jinja2.plugins.tasks import template_file

# Disable Nornir logs to keep the terminal clean for the spinner
logging.getLogger("nornir").setLevel(logging.CRITICAL)

# Ensure logs directory exists
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def deploy_switch_config(task):
    """
    Renders and pushes Layer 2 configurations (VLANs, Trunks) to Switches.
    """
    vlan_config = task.run(
        task=template_file,
        template="vlan_switch.j2",
        path="templates"
    )

    task.run(
        task=netmiko_send_config,
        name="Pushing Switch Configuration",
        config_commands=vlan_config.result.splitlines()
    )

def deploy_router_config(task):
    """
    Renders and pushes Layer 3 configurations (OSPF, NAT, VPN) to Routers.
    """
    l3_config = task.run(
        task=template_file,
        template="router_l3.j2",
        path="templates"
    )
    
    task.run(
        task=netmiko_send_config,
        name="Pushing Router Configuration",
        config_commands=l3_config.result.splitlines()
    )

def save_logs_to_file(results, device_type):
    """
    Writes the configuration output to a timestamped file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{LOG_DIR}/deploy_{device_type}_{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write(f"--- DEPLOYMENT LOG FOR {device_type.upper()} ---\n")
        f.write(f"Date: {timestamp}\n")
        f.write("-" * 50 + "\n\n")

        for host, multi_result in results.items():
            f.write(f"*** DEVICE: {host} ***\n")
            if multi_result.failed:
                f.write("STATUS: FAILED ❌\n")
            else:
                f.write("STATUS: SUCCESS ✅\n")
            
            for result in multi_result:
                if result.name in ["Pushing Switch Configuration", "Pushing Router Configuration"]:
                    f.write("\n--- CONFIGURATION PUSHED ---\n")
                    f.write(str(result.result))
                    f.write("\n" + "-" * 30 + "\n")
            
            f.write("\n" + "=" * 50 + "\n\n")

    return filename

def main():
    nr = InitNornir(config_file="config.yaml")

    print("\n🚀 Starting Network Automation Deployment...\n")
    
    switches = nr.filter(F(type="switch"))
    routers = nr.filter(F(type="router"))

    # Initialize the Spinner
    spinner = Halo(spinner='dots', color='cyan')

    # --- PROCESS SWITCHES ---
    if len(switches.inventory.hosts) > 0:
        spinner.start(text="Configuring Switches...")
        
        # Run Automation
        result_switches = switches.run(task=deploy_switch_config)
        
        spinner.succeed(text="Switches Configured Successfully")
        
        # Save logs (silent)
        log_file = save_logs_to_file(result_switches, "switches")
        print(f"   📄 Logs saved to: {log_file}\n")

    # --- PROCESS ROUTERS ---
    if len(routers.inventory.hosts) > 0:
        spinner.start(text="Configuring Routers...")
        
        result_routers = routers.run(task=deploy_router_config)
        
        spinner.succeed(text="Routers Configured Successfully")
        
        log_file = save_logs_to_file(result_routers, "routers")
        print(f"   📄 Logs saved to: {log_file}\n")

    print("✅ Deployment Complete! Check the 'logs' folder for details.\n")

if __name__ == "__main__":
    main()
