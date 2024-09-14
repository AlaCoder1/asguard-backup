#!/bin/bash

# Source the environment file
source /root/.ziti/quickstart/Asguard/Asguard.env

# Introduce a delay using sleep. For example, wait for 5 seconds.
sleep 5

# Check if required environment variables are set and then stop the Ziti controller in background detached mode
if [ -n "$ZITI_BIN_DIR" ] && [ -n "$ZITI_HOME" ] && [ -n "$ZITI_CTRL_NAME" ]; then
    nohup "${ZITI_BIN_DIR-}/ziti" controller stop "${ZITI_HOME}/${ZITI_CTRL_NAME}.yaml" &>/dev/null &
    disown $!
else
    echo "Required environment variables are not set."
fi

"${ZITI_BIN_DIR-}/ziti" edge login Asguard:1280 -u admin -p admin

