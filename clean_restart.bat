@echo off
echo 🗑️ Banking Reconciliation Engine - Clean Restart
echo ===============================================

echo.
echo ⚠️  This will clear ALL transaction data and restart fresh
echo    Press Ctrl+C to cancel, or any key to continue...
pause

echo.
echo Step 1: Stopping all processes...
echo Closing any running Python/Node processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
echo ✅ Processes stopped

echo.
echo Step 2: Stopping Docker containers...
cd kafka
docker-compose down
cd ..\backend  
docker-compose down
echo ✅ Docker containers stopped

echo.
echo Step 3: Clearing database...
cd backend
python clear_all_data.py
if %errorlevel% neq 0 (
    echo ❌ Failed to clear database
    pause
    exit /b 1
)
echo ✅ Database cleared

echo.
echo Step 4: Clearing Redis cache...
docker exec reconciliation_redis redis-cli FLUSHALL 2>nul
echo ✅ Redis cache cleared

echo.
echo Step 5: Clearing Kafka topics...
echo Setting retention to 1 second to purge messages...
docker exec kafka-kafka-1 kafka-configs --bootstrap-server localhost:9092 --entity-type topics --entity-name core_txns --alter --add-config retention.ms=1000 2>nul
docker exec kafka-kafka-1 kafka-configs --bootstrap-server localhost:9092 --entity-type topics --entity-name gateway_txns --alter --add-config retention.ms=1000 2>nul
docker exec kafka-kafka-1 kafka-configs --bootstrap-server localhost:9092 --entity-type topics --entity-name mobile_txns --alter --add-config retention.ms=1000 2>nul

echo Waiting for messages to be purged...
timeout /t 5 /nobreak

echo Resetting retention to default...
docker exec kafka-kafka-1 kafka-configs --bootstrap-server localhost:9092 --entity-type topics --entity-name core_txns --alter --delete-config retention.ms 2>nul
docker exec kafka-kafka-1 kafka-configs --bootstrap-server localhost:9092 --entity-type topics --entity-name gateway_txns --alter --delete-config retention.ms 2>nul
docker exec kafka-kafka-1 kafka-configs --bootstrap-server localhost:9092 --entity-type topics --entity-name mobile_txns --alter --delete-config retention.ms 2>nul
echo ✅ Kafka topics cleared

echo.
echo ✅ Clean restart complete!
echo.
echo 🚀 Ready to start fresh. Run start_project.bat to begin
echo    or follow the manual steps in STARTUP_GUIDE.md
echo.
pause