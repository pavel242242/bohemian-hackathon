#!/bin/bash

# STAGEHAND - Start All Mock Servers
# Launches all 4 mock servers in the background

echo "=========================================="
echo "Starting STAGEHAND Mock Servers"
echo "=========================================="
echo ""

# Kill any existing processes on our ports
echo "Cleaning up existing processes..."
lsof -ti:3001 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3003 | xargs kill -9 2>/dev/null
lsof -ti:5000 | xargs kill -9 2>/dev/null
sleep 1

# Create logs directory
mkdir -p logs

# Start Meta Ad Library Mock (port 3001)
echo "Starting Meta Ad Library Mock on port 3001..."
cd mocks/meta-api
npm install --silent 2>/dev/null
npm start > ../../logs/meta-mock.log 2>&1 &
META_PID=$!
cd ../..

# Start Google Ads Mock (port 8000)
echo "Starting Google Ads Mock on port 8000..."
cd mocks/google-ads
pip install -q -r requirements.txt 2>/dev/null
python server.py > ../../logs/google-mock.log 2>&1 &
GOOGLE_PID=$!
cd ../..

# Start TikTok Ads Mock (port 3003)
echo "Starting TikTok Ads Mock on port 3003..."
cd mocks/tiktok-api
npm install --silent 2>/dev/null
npm start > ../../logs/tiktok-mock.log 2>&1 &
TIKTOK_PID=$!
cd ../..

# Start SOAP Budget Mock (port 5001)
echo "Starting SOAP Budget Mock on port 5001..."
cd mocks/soap-budget
venv/bin/python3.11 simple_soap_server.py > ../../logs/soap-mock.log 2>&1 &
SOAP_PID=$!
cd ../..

# Save PIDs
echo $META_PID > logs/meta.pid
echo $GOOGLE_PID > logs/google.pid
echo $TIKTOK_PID > logs/tiktok.pid
echo $SOAP_PID > logs/soap.pid

echo ""
echo "Waiting for servers to start..."
sleep 5

echo ""
echo "=========================================="
echo "Server Status"
echo "=========================================="
echo "Meta Ad Library:  http://localhost:3001  (PID: $META_PID)"
echo "Google Ads:       http://localhost:8000  (PID: $GOOGLE_PID)"
echo "TikTok Ads:       http://localhost:3003  (PID: $TIKTOK_PID)"
echo "SOAP Budget:      http://localhost:5001  (PID: $SOAP_PID)"
echo ""
echo "Logs are in: ./logs/"
echo ""
echo "To test servers, run:"
echo "  ./test-all-mocks.sh"
echo ""
echo "To stop all servers, run:"
echo "  ./stop-all-mocks.sh"
echo ""
