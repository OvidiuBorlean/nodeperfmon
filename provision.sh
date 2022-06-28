#!/bin/bash
chmod +x ./cpucheck.sh
chmod +x ./memcheck.sh
echo "Installing Python Libraries"
apt install python3-pip -y
pip3 install azure.storage.blob
python3 ./k8sperf.sh
