#!/bin/bash
# Wrapper to start mock boot with specific params
# We use 10s to verify the manager waits and succeeds. 
# (Real marathon would be ./mock_boot.sh 2100 9090)
cd "$(dirname "$0")"
./mock_boot.sh 10 9090
