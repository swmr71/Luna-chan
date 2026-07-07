# Homelab Infrastructure & Knowledge Base

## 1. Network Configuration
- **Network Topology**: Double router configuration.
  - Outer layer: General client devices.
  - Inner layer: Private server segment.
- **Domain**: `clusters-prj.com`
- **Subnet Rules (10.2.x.x)**:
  - `10.2.0.x`: Physical hardware nodes (Proxmox VE hosts).
  - `10.2.x.y` (1 ≤ x ≤ 255): Virtual machines and LXC containers.
    - `x` represents the first two digits of the Container ID (CTID).
    - `y` represents the last two digits of the Container ID (CTID).
    - *Example*: CTID 102 corresponds to IP `10.2.1.2`.

## 2. Proxmox Container & VM List
- CTID 100: NextCloud-temp
- CTID 101: NextCloud
- CTID 102: Web-Front1
- CTID 103: Github
- CTID 104: Browser
- CTID 105: Web-1
- CTID 106: DNS
- CTID 107: DDNS
- CTID 108: MS-1-SQL
- CTID 109: MS-R2
- CTID 110: MS-2
- CTID 117: Web-SRS
- CTID 118: FFmpeg
- CTID 119: Video
- CTID 301: RAKU-Server
- CTID 302: RAKUWEB-Server

## 3. Operations & Maintenance Logs
- (AI or user will append historical logs and troubleshooting notes here)
