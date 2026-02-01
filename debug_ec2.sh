#!/bin/bash
# EC2 Debugging Script
# Run this script on your EC2 instance to diagnose issues

echo "================================"
echo "EC2 Network Security Debugging"
echo "================================"
echo ""

echo "1. Checking Docker containers..."
docker ps -a
echo ""

echo "2. Checking networksecurity container logs..."
docker logs networksecurity --tail 100 2>&1 || echo "Container not found or not running"
echo ""

echo "3. Checking if port 8080 is listening..."
sudo netstat -tlnp | grep 8080 || sudo ss -tlnp | grep 8080 || echo "Port 8080 is not listening"
echo ""

echo "4. Checking Docker network..."
docker inspect networksecurity 2>&1 | grep IPAddress || echo "Cannot inspect container"
echo ""

echo "5. Testing local connection..."
curl -v http://localhost:8080/docs 2>&1 || echo "Cannot connect locally"
echo ""

echo "6. Checking disk space..."
df -h
echo ""

echo "7. Checking memory..."
free -h
echo ""

echo "8. Checking if Docker service is running..."
sudo systemctl status docker --no-pager
echo ""

echo "================================"
echo "Debugging complete!"
echo "================================"
