#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

install_terax_binary() {
    if command -v terax &>/dev/null; then
        echo "Terax is already installed: $(terax --version 2>/dev/null || echo 'installed')"
        return 0
    fi

    echo "Installing Terax..."

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        ARCH=$(uname -m)
        if command -v dpkg &>/dev/null; then
            if [ "$ARCH" = "x86_64" ]; then
                DEB_URL="https://github.com/crynta/terax-ai/releases/latest/download/Terax_0.8.2_amd64.deb"
            elif [ "$ARCH" = "aarch64" ]; then
                DEB_URL="https://github.com/crynta/terax-ai/releases/latest/download/Terax_0.8.2_arm64.deb"
            else
                echo "ERROR: Unsupported architecture: $ARCH" >&2
                return 1
            fi

            TEMP_DIR=$(mktemp -d)
            echo "Downloading Terax deb package..."
            curl -sL "$DEB_URL" -o "$TEMP_DIR/terax.deb"

            if ! file "$TEMP_DIR/terax.deb" | grep -q "Debian"; then
                echo "ERROR: Downloaded file is not a valid deb package" >&2
                rm -rf "$TEMP_DIR"
                return 1
            fi

            sudo dpkg -i "$TEMP_DIR/terax.deb" || sudo apt-get install -f -y
            rm -rf "$TEMP_DIR"
            echo "Terax installed via deb package"
        elif command -v rpm &>/dev/null; then
            if [ "$ARCH" = "x86_64" ]; then
                RPM_URL="https://github.com/crynta/terax-ai/releases/latest/download/Terax_0.8.2_x86_64.rpm"
            elif [ "$ARCH" = "aarch64" ]; then
                RPM_URL="https://github.com/crynta/terax-ai/releases/latest/download/Terax_0.8.2_aarch64.rpm"
            else
                echo "ERROR: Unsupported architecture: $ARCH" >&2
                return 1
            fi

            TEMP_DIR=$(mktemp -d)
            echo "Downloading Terax rpm package..."
            curl -sL "$RPM_URL" -o "$TEMP_DIR/terax.rpm"
            sudo rpm -i "$TEMP_DIR/terax.rpm" || sudo dnf install -y "$TEMP_DIR/terax.rpm" || sudo zypper install -y "$TEMP_DIR/terax.rpm"
            rm -rf "$TEMP_DIR"
            echo "Terax installed via rpm package"
        else
            echo "ERROR: Neither dpkg nor rpm found. Cannot install Terax." >&2
            return 1
        fi

    elif [[ "$OSTYPE" == "darwin"* ]]; then
        ARCH=$(uname -m)
        if [ "$ARCH" = "arm64" ]; then
            DMG_URL="https://github.com/crynta/terax-ai/releases/latest/download/Terax_0.8.2_aarch64.dmg"
        else
            DMG_URL="https://github.com/crynta/terax-ai/releases/latest/download/Terax_0.8.2_x64.dmg"
        fi

        TEMP_DIR=$(mktemp -d)
        echo "Downloading Terax DMG..."
        curl -sL "$DMG_URL" -o "$TEMP_DIR/terax.dmg"

        hdiutil attach "$TEMP_DIR/terax.dmg" -quiet
        cp -R /Volumes/Terax/Terax.app /Applications/ 2>/dev/null || true
        hdiutil detach /Volumes/Terax -quiet 2>/dev/null || true
        rm -rf "$TEMP_DIR"
        echo "Terax installed to /Applications/Terax.app"
    else
        echo "ERROR: Unsupported OS: $OSTYPE" >&2
        return 1
    fi
}

install_terax_config() {
    CONFIG_DIR="$HOME/.config/terax"
    mkdir -p "$CONFIG_DIR"

    if [ -f "$SCRIPT_DIR/config/terax-config.yaml" ]; then
        cp -f "$SCRIPT_DIR/config/terax-config.yaml" "$CONFIG_DIR/config.yaml"
        echo "Terax config installed to ~/.config/terax/config.yaml"
    fi
}

install_terax_memory() {
    WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
    TERAX_MD="$WORKSPACE_ROOT/TERAX.md"

    if [ ! -f "$TERAX_MD" ] && [ -f "$SCRIPT_DIR/config/TERAX.md" ]; then
        cp -f "$SCRIPT_DIR/config/TERAX.md" "$TERAX_MD"
        echo "TERAX.md installed to workspace root"
    fi
}

install_terax_binary
install_terax_config
install_terax_memory

echo ""
echo "Terax installation complete!"
echo ""
echo "Configuration:"
echo "  - Config: ~/.config/terax/config.yaml"
echo "  - Memory: ./TERAX.md (workspace root)"
echo ""
echo "To launch: terax"
echo "To connect to OmniRoute: terax will auto-detect the gateway at http://localhost:20128/v1"
