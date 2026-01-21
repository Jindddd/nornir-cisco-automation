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

## 🔌 Day 0 Configuration (Bootstrap)
Before running the automation scripts, every device must have a basic "Day 0" configuration manually applied via the console. This ensures the GNS3/EVE-NG controller can reach the devices via SSH.

Copy and paste the configuration in [zero-day-config.txt](zero-day-config.txt).

### Credentials used in this lab:
- **Username:** admin
- **Password:** cisco
- **Enable Secret:** cisco

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
```Bash
python3 deploy_network.py
```

### 3. Verify Configuration
Run the main script to verify configurations on all devices.
```Bash
python3 verify_network.py
```

## 📝 Configuration Details
**Switches:** Configured with VLANs 10, 20, 30, 40 and Trunks.

**Routers:**
- OSPF Area 0 on WAN, Area 1 on Spoke LANs.
- NAT/PAT configured on Spokes for Direct Internet Access (DIA).
- IPSec VPN established directly between Site 1 and Site 2.

### Network Configuration Overview
This project automates a Hybrid Hub-and-Spoke network topology designed for enterprise connectivity. It integrates local switching, dynamic routing, direct internet access, and secure site-to-site tunneling.

#### 1. Layer 2 Switching (Campus LAN)
- **VLAN Segmentation:** Each branch site is segmented into four distinct VLANs: Data (10), Voice (20), Guest (30), and POS (40).
- **Trunking:** Uplinks from Access Switches to Branch Routers use 802.1Q Encapsulation to carry tagged traffic.
- **Access Layer:** Ports are statically assigned to VLANs, with PortFast enabled to bypass Spanning Tree listening states for end devices.

#### 2. Layer 3 Routing (OSPF)
Area Design:
- **Area 0 (Backbone):** Connects the WAN links between the Core Router and Branch Routers (R1, R2).
- **Area 1 (Stub/Branch):** Contains the local LAN subnets at each branch site.
- **WAN Adjacency:** WAN links are configured as OSPF Point-to-Point networks to eliminate DR/BDR elections and speed up convergence.
- **Inter-VLAN Routing:** Branch Routers perform Router-on-a-Stick (ROAS) using 802.1Q sub-interfaces to route traffic between local VLANs.

#### 3. Internet Edge (NAT/PAT)
- **Direct Internet Access (DIA):** Branches do not backhaul internet traffic to HQ. Instead, they route directly to the ISP (simulated by the Core).
- **NAT Overload (PAT):** Internal private IPs (RFC1918) are translated to the router's single public WAN IP using Port Address Translation, allowing multiple users to share one public identity.
- **Virtual Reassembly:** IP Virtual Fragmentation Reassembly (VFR) is enabled to handle fragmented packets during translation.

#### 4. WAN Security (IPSec VPN)
- **Architecture:** Direct Spoke-to-Spoke VPN. While the physical path goes through the Core, the logical tunnel is established directly between Site 1 and Site 2.
- **Encryption:** Uses AES-256 for encryption and SHA-HMAC for integrity (IKEv1 / ISAKMP Group 14).
- **Traffic Filtering:** Specific Access Control Lists (ACLs) ensure that VPN traffic is excluded from NAT and encapsulated into the tunnel immediately.

## 🔍 Verify Connectivity

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

## 📈 Scaling the Network: How to Add a New Branch

This automation framework is designed to be scalable. Adding a new site (e.g., **Site 3**) does not require changing any Python code or Jinja2 templates. You simply need to update the data files.

Follow this 4-step procedure to add a new branch to the network.

### Step 1: Update Topology (GNS3/EVE-NG)

1. **Add Devices:** Drag in a new Router (**R3**) and Switch (**SW3**).
2. **Connect Uplinks:**
* Connect **R3** to the **Core-Router** (e.g., `GigabitEthernet3/0`).
* Connect **SW3** to **R3**.


3. **Bootstrap:** Apply the "Day 0" configuration manually via console to enable SSH access.
* *Reference:* Copy the config from `zero-day-config.txt`.



### Step 2: Define the New Site in `hosts.yaml`

Open `inventory/hosts.yaml` and add the definitions for the new devices. You must define the **WAN IP**, **VPN Peers**, and **LAN Subnets**.

**Add R3 (Site 3):**

```yaml
R3:
  hostname: 192.168.1.7
  groups:
    - spokes
  data:
    wan_if: "GigabitEthernet1/0"
    wan_ip: "203.0.113.10"
    wan_mask: "255.255.255.252"
    
    # Define VPN Tunnels to existing sites
    vpn_peers:
      - ip: "203.0.113.2"  # Link to Site 1
        id: 10
        subnets: [192.168.20.0 0.0.0.255, 192.168.21.0 0.0.0.255, ...]
      - ip: "203.0.113.6"  # Link to Site 2
        id: 20
        subnets: [192.168.30.0 0.0.0.255, 192.168.31.0 0.0.0.255, ...]

    lan_if: "FastEthernet3/0"
    site_octet: 40  # Generates 192.168.40.x, 41.x...
    ospf_area: 1

```

### Step 3: Update Existing Peers (Full Mesh)

For a Full Mesh VPN, existing sites must know about the new site. Update **R1** and **R2** in `inventory/hosts.yaml` to include R3 as a peer.

**Update R1:**

```yaml
R1:
  data:
    vpn_peers:
      - ip: "203.0.113.6" # Existing Link to R2
        # ... existing config ...
      
      # NEW LINK TO SITE 3
      - ip: "203.0.113.10"
        id: 20
        subnets:
          - 192.168.40.0 0.0.0.255
          - 192.168.41.0 0.0.0.255
          - 192.168.42.0 0.0.0.255
          - 192.168.43.0 0.0.0.255

```

*(Repeat this process for R2).*

### Step 4: Update Global Groups

Open `inventory/groups.yaml` and add the new site's subnets to the global list. This ensures all routers generate the correct NAT exemptions.

```yaml
global_params:
  data:
    spoke_subnets:
      # ... existing subnets ...
      # ADD SITE 3 SUBNETS
      - 192.168.40.0 0.0.0.255
      - 192.168.41.0 0.0.0.255
      - 192.168.42.0 0.0.0.255
      - 192.168.43.0 0.0.0.255

```

### Step 5: Deploy

Run the deployment script. Nornir will configure the new site and automatically update the existing sites to establish the new VPN tunnels.

```bash
python3 deploy_network.py

```