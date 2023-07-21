#!/bin/bash

# Make a backup of sudoers file
sudo cp /etc/sudoers /etc/sudoers.backup

# Uncomment the specified line used sed
sudo sed -i '/%whell ALL=(ALL:ALL) NOPASSWD: ALL/s/^# //' /etc/sudoers