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
- CTID 101: NextCloud

## 3. Operations & Maintenance Logs
- (AI or user will append historical logs and troubleshooting notes here)
