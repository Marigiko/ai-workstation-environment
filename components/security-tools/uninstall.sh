#!/usr/bin/env bash
set -euo pipefail

echo "Uninstalling security tools..."

if command -v apt-get &>/dev/null; then
    sudo apt-get remove -y \
        nmap hashcat john hydra sqlmap nikto \
        aircrack-ng binwalk steghide \
        ffuf gobuster dirb whatweb wpscan \
        burpsuite metasploit-framework \
        bloodhound torbrowser-launcher \
        openvpn masscan fcrackzip seclists exploitdb \
        2>/dev/null || true

elif command -v pacman &>/dev/null; then
    sudo pacman -R --noconfirm \
        nmap hashcat john hydra sqlmap nikto \
        aircrack-ng binwalk steghide \
        ffuf gobuster dirb whatweb wpscan \
        burpsuite metasploit \
        bloodhound torbrowser-launcher \
        openvpn masscan fcrackzip seclists exploitdb \
        2>/dev/null || true

elif command -v dnf &>/dev/null; then
    sudo dnf remove -y \
        nmap hashcat john hydra sqlmap nikto \
        aircrack-ng binwalk steghide \
        ffuf gobuster dirb whatweb wpscan \
        metasploit bloodhound \
        torbrowser-launcher openvpn masscan fcrackzip \
        2>/dev/null || true
fi

pip3 uninstall -y stegseek zsteg 2>/dev/null || true

echo "Security tools uninstalled."
