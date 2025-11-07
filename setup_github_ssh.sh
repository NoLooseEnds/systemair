#!/bin/bash
# GitHub SSH Setup Script

echo "=== GitHub SSH Key Setup ==="
echo ""
echo "Step 1: Generate SSH key"
echo "Enter your GitHub email address:"
read -r email

if [ -z "$email" ]; then
    echo "Error: Email is required"
    exit 1
fi

# Generate SSH key
ssh-keygen -t ed25519 -C "$email" -f ~/.ssh/id_ed25519 -N ""

# Start SSH agent
eval "$(ssh-agent -s)"

# Add key to agent
ssh-add ~/.ssh/id_ed25519

echo ""
echo "=== Your Public SSH Key ==="
echo "Copy the key below and add it to GitHub:"
echo "https://github.com/settings/keys"
echo ""
cat ~/.ssh/id_ed25519.pub
echo ""
echo ""
echo "After adding the key to GitHub, test the connection with:"
echo "ssh -T git@github.com"
echo ""
echo "Then configure git remote:"
echo "cd /home/jk/dev/homeassistant/villavent/dev"
echo "git remote set-url origin git@github.com:NoLooseEnds/systemair.git"

