#!/bin/bash

# Update apt-get and install curl and gnupg for security
apt-get update -y
apt-get install -y curl gnupg

# Add NodeSource repository for Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -

# Install Node.js from the new repository
apt-get install -y nodejs 