<<<<<<< HEAD
# nornir-cisco-automation
Group Assignment for WIC2005 PROGRAMMABLE NETWORK
=======
# Network Automation with Nornir

This project automates the deployment of a Hub-and-Spoke network topology using **Python** and **Nornir**. It configures Layer 2 switching (VLANs, Trunks) and Layer 3 routing (OSPF, NAT, Site-to-Site VPN) on Cisco IOS devices.

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
Python 3.8+

GNS3 or EVE-NG with Cisco IOS images (e.g., c7200, iou).

A topology matching the inventory/hosts.yaml definitions.

## 📦 Installation
Clone the repository:

```Bash
git clone [nornir-cisco-automation](https://github.com/Jindddd/nornir-cisco-automation.git)
cd YOUR_REPO_NAME
```

Create a virtual environment (optional but recommended):
```Bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:
```
Bash
pip install -r requirements.txt
```

## ▶️ Usage
1. Check Connectivity Verify that all devices in your topology are reachable.
```
Bash
python3 check_connectivity.py
```

2. Deploy Configuration Run the main script to push configurations to all devices.
```
Bash
python3 deploy_network.py
```

## 📝 Configuration Details
Switches: Configured with VLANs 10, 20, 30, 40 and Trunks.

Routers:

OSPF Area 0 on WAN, Area 1 on Spoke LANs.

NAT/PAT configured on Spokes for Direct Internet Access (DIA).

IPSec VPN established directly between Site 1 and Site 2.


---

### Step 4: Push to GitHub

1.  **Initialize Git**:
    Open your terminal in the project folder and run:
    ```bash
    git init
    ```

2.  **Add Files**:
    Stage all your files (the `.gitignore` will prevent logs from being added):
    ```bash
    git add .
    ```

3.  **Commit**:
    Save the snapshot of your project:
    ```bash
    git commit -m "Initial commit: Network Automation Project"
    ```

4.  **Create Repository on GitHub**:
    * Go to [GitHub.com](https://github.com) and log in.
    * Click the **+** icon in the top right -> **New repository**.
    * Name it (e.g., `nornir-network-automation`).
    * Click **Create repository**.

5.  **Link and Push**:
    Copy the commands GitHub shows you under "...or push an existing repository from the command line" and run them. They will look like this:
    ```bash
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/nornir-network-automation.git
    git push -u origin main
    ```

Once done, refresh your GitHub page, and you will see your code and the README displayed per
>>>>>>> 6ed5bba (Initial commit)
