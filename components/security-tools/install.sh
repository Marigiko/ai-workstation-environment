#!/usr/bin/env bash
set -euo pipefail

echo "Installing security tools..."

if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y \
        nmap hashcat john hydra sqlmap nikto \
        aircrack-ng binwalk steghide \
        ffuf gobuster dirb whatweb wpscan \
        burpsuite metasploit-framework \
        bloodhound torbrowser-launcher \
        openvpn masscan fcrackzip seclists exploitdb \
        2>/dev/null || echo "WARNING: Some packages failed (may need PPAs or manual install)"

elif command -v pacman &>/dev/null; then
    sudo pacman -Sy --noconfirm \
        nmap hashcat john hydra sqlmap nikto \
        aircrack-ng binwalk steghide \
        ffuf gobuster dirb whatweb wpscan \
        burpsuite metasploit \
        bloodhound torbrowser-launcher \
        openvpn masscan fcrackzip seclists exploitdb \
        2>/dev/null || echo "WARNING: Some packages failed"

elif command -v dnf &>/dev/null; then
    sudo dnf install -y \
        nmap hashcat john hydra sqlmap nikto \
        aircrack-ng binwalk steghide \
        ffuf gobuster dirb whatweb wpscan \
        metasploit bloodhound \
        torbrowser-launcher openvpn masscan fcrackzip \
        2>/dev/null || echo "WARNING: Some packages failed"

else
    echo "ERROR: No supported package manager found" >&2
    exit 1
fi

# Install pip-based security tools (no sudo needed)
export PATH="$HOME/.local/bin:$HOME/.micromamba/bin:$PATH"
pip3 install --user stegseek zsteg 2>/dev/null || true

echo "Security tools installation complete."
echo "NOTE: Some tools may require additional setup (e.g., Metasploit database, Burpsuite license)"