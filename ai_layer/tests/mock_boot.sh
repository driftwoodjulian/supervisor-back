#!/bin/bash
# Mock Boot Script for Marathon Simulation
echo "[Mock] Starting Marathon Boot Sequence..."
echo "[Mock] Going to sleep for 35 minutes (simulated)..."
# In reality, for the test we might want to speed this up or actually wait?
# The prompt says "Use a mock script to simulate a 35-minute successful boot."
# If I actually sleep 35m, the user will wait 35m.
# "Pass: The AI layer remains stable (no timeout errors) and marks itself READY at the 35-minute mark."
# I'll implement a sleep 1 and then just hang out?
# Wait, "marks itself READY at the 35-minute mark".
# So it should sleep 2100 seconds then start a dummy server on the port.
# I will use a shorter time for the *dev* test but the script should support the long time.
# Let's make it configurable with an arg, default to 35m.

DURATION=${1:-2100} 
PORT=${2:-8000}

echo "[Mock] Sleeping for $DURATION seconds..."
sleep $DURATION

echo "[Mock] Waking up! Starting dummy HTTP server on port $PORT..."
# We need to respond to /v1/models with 200 OK.
# Using python http.server is easy but it serves files.
# We need a custom response for the manager health check.
# Let's use a tiny python script.

python3 -c "
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/v1/models':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{\"object\":\"list\",\"data\":[]}')
        else:
            self.send_response(404)
            self.end_headers()

print('Starting mock server on port $PORT')
HTTPServer(('0.0.0.0', $PORT), Handler).serve_forever()
"
