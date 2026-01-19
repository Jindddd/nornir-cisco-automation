# Network Automation with Nornir

Group Assignment for WIC2005 PROGRAMMABLE NETWORK. This project automates the deployment of a Hub-and-Spoke network topology using **Python** and **Nornir**. It configures Layer 2 switching (VLANs, Trunks) and Layer 3 routing (OSPF, NAT, Site-to-Site VPN) on Cisco IOS devices.

## 🚀 Features
* **Automated Configuration**: Pushes config to Switches and Routers simultaneously.
* **Jinja2 Templating**: Uses dynamic templates for modular configuration.
* **Connectivity Check**: Includes a script to verify device reachability before deployment.
* **Visual Feedback**: Uses a loading spinner (`halo`) and progress bars for a professional CLI experience.
* **Logging**: Automatically saves deployment logs with timestamps to a `logs/` directory.

## 🛠️ Project Structure
```text
├── inventory/          # Hosts, Groups, and Defaults definitions
├── templates/          # Jinja2 templates (router_l3.j2, vlan_switch.j2)
├── logs/               # Deployment logs (ignored by git)
├── config.yaml         # Nornir configuration file
├── deploy_network.py   # Main automation script
├── check_connectivity.py # Pre-flight check script
└── requirements.txt    # Python dependencies
```

## 📋 Prerequisites
- Python 3.8+
- GNS3 or EVE-NG with Cisco IOS images (e.g., c7200, iou).
- A topology matching the inventory/hosts.yaml definitions.

## 📡 Topology

![Network Topology](images/topology.png)

## 📦 Installation
Clone the repository:

```Bash
git clone https://github.com/Jindddd/nornir-cisco-automation.git
cd nornir-cisco-automation
```

Create a virtual environment (optional but recommended):
```Bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:
```Bash
pip install -r requirements.txt
```

## ▶️ Usage
### 1. Check Connectivity
Verify that all devices in your topology are reachable.
```Bash
python3 check_connectivity.py
```

### 2. Deploy Configuration
Run the main script to push configurations to all devices.
```
Bash
python3 deploy_network.py
```

## 📝 Configuration Details
**Switches:** Configured with VLANs 10, 20, 30, 40 and Trunks.

**Routers:**
- OSPF Area 0 on WAN, Area 1 on Spoke LANs.
- NAT/PAT configured on Spokes for Direct Internet Access (DIA).
- IPSec VPN established directly between Site 1 and Site 2.

## 🔍 Verification

| Device Name | Connect to Switch Port | Assigned VLAN | Purpose |
|-------------|------------------------|---------------|---------|
| PC1 (Site 1) | `SW1 Fa4/1` | `VLAN 10 (Data)` | Test Data VLAN |
| PC2 (Site 1) | `SW1 Fa4/2` | `VLAN 20 (Voice)` | Test Inter-VLAN Routing |
| PC3 (Site 2) | `SW2 Fa4/1` | `VLAN 10 (Data)` | Test Site-to-Site VPN |
| PC4 (Site 2) | `SW2 Fa4/2` | `VLAN 20 (Voice)` | Test VPN + Inter-VLAN |

### Test 1: Verify Inter-VLAN Routing (ROAS)
- Goal: Prove that different departments (VLANs) at the SAME site can talk to each other.
- Action: From PC1, ping PC2.

```Bash
ping 192.168.21.10
```

*Why it works: Traffic goes from PC1 -> SW1 -> R1 (via Trunk) -> R1 routes between Sub-interfaces -> SW1 -> PC2.*


### Test 2: Verify Internet Access (NAT)
- Goal: Prove that private branches can reach the "Public" internet.
- Action: From PC1, ping the Core-Router's WAN IP (simulating the internet).

```Bash
ping 203.0.113.1
```

*Why it works: R1 translates PC1's private IP (192.168.20.10) to its public WAN IP (203.0.113.2) using NAT. If this fails, the Core Router won't know how to reply to the private IP.*

> Check NAT: On R1, run `show ip nat translations`. You should see an entry for ICMP when you ping the Core.

### Test 3: Verify Site-to-Site VPN
- Goal: Prove that Site 1 can securely talk to Site 2 over the "public" network.
- Action: From PC1 (Site 1), ping PC3 (Site 2).

```Bash
ping 192.168.30.10
```
*Why it works: R1 sees traffic destined for 192.168.30.x. The Crypto Map ACL matches this traffic. R1 encrypts the packet and tunnels it to R2. R2 decrypts it and delivers it to PC3. Note: The first ping might timeout while the VPN tunnel negotiates.*

> Check VPN: On R1, run `show crypto isakmp sa` and `show crypto ipsec sa`