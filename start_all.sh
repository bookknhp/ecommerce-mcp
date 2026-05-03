#!/bin/bash

# 🚀 E-Commerce MCP Complete - Start All Services

echo "🚀 E-Commerce MCP - Complete Setup"
echo "===================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python3 found${NC}"
echo ""

# Create logs directory
mkdir -p logs

echo "📋 Services to start:"
echo "  1. Flask API Server (Port 5001)"
echo "  2. HTTP Dashboard Server (Port 8000)"
echo "  3. Telegram Bot"
echo ""

# Start Flask
echo -e "${YELLOW}▶ Starting Flask API Server...${NC}"
python3 app.py > logs/flask.log 2>&1 &
FLASK_PID=$!
echo -e "${GREEN}✅ Flask started (PID: $FLASK_PID)${NC}"

# Wait for Flask to start
sleep 2

# Start HTTP Server
echo -e "${YELLOW}▶ Starting HTTP Dashboard Server...${NC}"
python3 -m http.server 8000 > logs/http.log 2>&1 &
HTTP_PID=$!
echo -e "${GREEN}✅ HTTP Server started (PID: $HTTP_PID)${NC}"

# Start Telegram Bot
echo -e "${YELLOW}▶ Starting Telegram Bot...${NC}"
python3 telegram_bot.py > logs/telegram.log 2>&1 &
TELEGRAM_PID=$!
echo -e "${GREEN}✅ Telegram Bot started (PID: $TELEGRAM_PID)${NC}"

echo ""
echo "═════════════════════════════════════════"
echo -e "${GREEN}✅ All Services Running!${NC}"
echo "═════════════════════════════════════════"
echo ""

echo "📍 URLs:"
echo "  🌐 Dashboard:   http://localhost:8000/dashboard.html"
echo "  📡 API Base:    http://localhost:5001/api"
echo "  💬 Telegram:    Search @ecommerce_mcp_bot (or your bot name)"
echo ""

echo "🔧 Process IDs:"
echo "  Flask:     $FLASK_PID"
echo "  HTTP:      $HTTP_PID"
echo "  Telegram:  $TELEGRAM_PID"
echo ""

echo "📝 Log files:"
echo "  Flask:     logs/flask.log"
echo "  HTTP:      logs/http.log"
echo "  Telegram:  logs/telegram.log"
echo ""

echo "🛑 To stop all services:"
echo "  kill $FLASK_PID $HTTP_PID $TELEGRAM_PID"
echo ""

echo "📚 Documentation:"
echo "  • README.md - Complete guide"
echo "  • QUICK_REFERENCE.md - Cheat sheet"
echo "  • TELEGRAM_BOT.md - Bot commands"
echo "  • FORMULA.md - Calculation formulas"
echo ""

# Keep the script running
wait
