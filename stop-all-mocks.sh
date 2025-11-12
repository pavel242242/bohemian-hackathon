#!/bin/bash

# STAGEHAND - Stop All Mock Servers

echo "=========================================="
echo "Stopping STAGEHAND Mock Servers"
echo "=========================================="
echo ""

# Stop by PID if available
if [ -f logs/meta.pid ]; then
    META_PID=$(cat logs/meta.pid)
    kill $META_PID 2>/dev/null && echo "✓ Stopped Meta Mock (PID: $META_PID)"
fi

if [ -f logs/google.pid ]; then
    GOOGLE_PID=$(cat logs/google.pid)
    kill $GOOGLE_PID 2>/dev/null && echo "✓ Stopped Google Mock (PID: $GOOGLE_PID)"
fi

if [ -f logs/tiktok.pid ]; then
    TIKTOK_PID=$(cat logs/tiktok.pid)
    kill $TIKTOK_PID 2>/dev/null && echo "✓ Stopped TikTok Mock (PID: $TIKTOK_PID)"
fi

if [ -f logs/soap.pid ]; then
    SOAP_PID=$(cat logs/soap.pid)
    kill $SOAP_PID 2>/dev/null && echo "✓ Stopped SOAP Mock (PID: $SOAP_PID)"
fi

# Fallback: kill by port
echo ""
echo "Cleaning up any remaining processes on ports..."
lsof -ti:3001 | xargs kill -9 2>/dev/null && echo "✓ Cleaned up port 3001"
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "✓ Cleaned up port 8000"
lsof -ti:3003 | xargs kill -9 2>/dev/null && echo "✓ Cleaned up port 3003"
lsof -ti:5001 | xargs kill -9 2>/dev/null && echo "✓ Cleaned up port 5001"

# Clean up PID files
rm -f logs/*.pid

echo ""
echo "All mock servers stopped."
