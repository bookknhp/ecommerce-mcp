#!/bin/bash

# 🚀 E-Commerce MCP Quick Start

echo "🚀 E-Commerce MCP Dashboard & Server - Quick Start"
echo "=================================================="
echo ""

# Check Python
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python3 not installed"
    exit 1
fi

# Check if already running
if lsof -i :5000 > /dev/null 2>&1; then
    echo "✅ Flask Server already running on :5000"
else
    echo "🚀 Starting Flask Server..."
    cd /Users/bookk/Documents/ecommerce-mcp
    python3 app.py &
    sleep 2
    echo "✅ Flask Server started"
fi

echo ""
echo "📍 URLs:"
echo "  🌐 Dashboard: http://localhost:8000/dashboard.html"
echo "  📡 API Base: http://localhost:5000/api"
echo "  📊 Home: http://localhost:5000"
echo ""

echo "🤖 MCP Server (for Claude Desktop):"
echo "  📝 Config file: /Users/bookk/Documents/ecommerce-mcp/claude_desktop_config.json"
echo "  💻 Server script: /Users/bookk/Documents/ecommerce-mcp/mcp_server.py"
echo ""

echo "🔧 Available Tools:"
echo "  📦 Product: update_price, update_stock, delete, low_stock"
echo "  🏷️  Coupon: create, cleanup_expired, disable"
echo "  📋 Order: update_status, update_payment"
echo "  📊 Report: sales, products"
echo "  🔔 Alert: get_alerts"
echo "  🛠️  Maintenance: backup_database, cleanup_old_logs"
echo ""

echo "✅ Ready to use!"
echo ""
echo "📝 Next steps:"
echo "  1. Open Dashboard: http://localhost:8000/dashboard.html"
echo "  2. Setup Claude Desktop (copy config from README)"
echo "  3. Start using AI commands!"
