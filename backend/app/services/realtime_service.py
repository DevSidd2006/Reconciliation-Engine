"""
Real-time Service for Banking-Grade Transaction Reconciliation Engine

This service provides background tasks for real-time updates:
- Transaction flow simulation
- Statistics updates
- AI insights generation
- System health monitoring
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any
from utils.socket_manager import socket_manager

logger = logging.getLogger(__name__)

class RealTimeService:
    def __init__(self):
        self.is_running = False
        self.tasks = []

    async def start(self):
        """Start all real-time background tasks"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Starting real-time service...")
        
        # Start background tasks
        self.tasks = [
            asyncio.create_task(self._transaction_flow_simulator()),
            asyncio.create_task(self._stats_updater()),
            asyncio.create_task(self._ai_insights_generator()),
            asyncio.create_task(self._system_health_monitor())
        ]
        
        logger.info("Real-time service started with 4 background tasks")

    async def stop(self):
        """Stop all real-time background tasks"""
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info("Stopping real-time service...")
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()
        
        logger.info("Real-time service stopped")

    async def _transaction_flow_simulator(self):
        """Simulate real-time transaction flow data for charts"""
        try:
            while self.is_running:
                # Generate simulated flow data
                flow_data = {
                    'coreBanking': random.randint(50, 150),
                    'mobileApp': random.randint(30, 100),
                    'paymentGateway': random.randint(40, 120),
                    'totalEvents': random.randint(120, 300)
                }
                
                await socket_manager.emit_transaction_flow_update(flow_data)
                
                # Wait 30 seconds before next update
                await asyncio.sleep(30)
                
        except asyncio.CancelledError:
            logger.info("Transaction flow simulator stopped")
        except Exception as e:
            logger.error(f"Error in transaction flow simulator: {e}")

    async def _stats_updater(self):
        """Update dashboard statistics periodically"""
        try:
            while self.is_running:
                # Generate simulated stats
                stats_data = {
                    'totalTransactions': random.randint(1000, 5000),
                    'matchedTransactions': random.randint(900, 4500),
                    'mismatches': random.randint(10, 100),
                    'pendingTransactions': random.randint(5, 50),
                    'highRiskAlerts': random.randint(0, 10)
                }
                
                await socket_manager.emit_stats_update(stats_data)
                
                # Wait 60 seconds before next update
                await asyncio.sleep(60)
                
        except asyncio.CancelledError:
            logger.info("Stats updater stopped")
        except Exception as e:
            logger.error(f"Error in stats updater: {e}")

    async def _ai_insights_generator(self):
        """Generate periodic AI insights and alerts"""
        try:
            insights = [
                {
                    'type': 'anomaly',
                    'message': 'Unusual spike in mobile app transactions detected',
                    'severity': 'medium',
                    'confidence': 87
                },
                {
                    'type': 'performance',
                    'message': 'Gateway response time increased by 15%',
                    'severity': 'low',
                    'confidence': 92
                },
                {
                    'type': 'security',
                    'message': 'High-value transaction pattern detected',
                    'severity': 'high',
                    'confidence': 94
                },
                {
                    'type': 'trend',
                    'message': 'Transaction volume trending upward',
                    'severity': 'info',
                    'confidence': 89
                }
            ]
            
            while self.is_running:
                # Randomly select and emit an insight
                if random.random() < 0.3:  # 30% chance every cycle
                    insight = random.choice(insights)
                    await socket_manager.emit_ai_insight(insight)
                
                # Wait 2 minutes before next check
                await asyncio.sleep(120)
                
        except asyncio.CancelledError:
            logger.info("AI insights generator stopped")
        except Exception as e:
            logger.error(f"Error in AI insights generator: {e}")

    async def _system_health_monitor(self):
        """Monitor system health and emit alerts"""
        try:
            while self.is_running:
                # Simulate system health checks
                alerts = []
                
                # Random system alerts
                if random.random() < 0.1:  # 10% chance
                    alerts.append({
                        'type': 'warning',
                        'message': 'High CPU usage detected on server',
                        'severity': 'medium',
                        'component': 'system'
                    })
                
                if random.random() < 0.05:  # 5% chance
                    alerts.append({
                        'type': 'error',
                        'message': 'Database connection pool near capacity',
                        'severity': 'high',
                        'component': 'database'
                    })
                
                # Emit alerts if any
                for alert in alerts:
                    await socket_manager.emit_system_alert(alert)
                
                # Wait 5 minutes before next health check
                await asyncio.sleep(300)
                
        except asyncio.CancelledError:
            logger.info("System health monitor stopped")
        except Exception as e:
            logger.error(f"Error in system health monitor: {e}")

    async def emit_transaction_event(self, transaction_data: Dict[str, Any]):
        """Emit a new transaction event"""
        await socket_manager.emit_transaction(transaction_data)

    async def emit_mismatch_event(self, mismatch_data: Dict[str, Any]):
        """Emit a new mismatch event"""
        await socket_manager.emit_mismatch(mismatch_data)

# Global instance
realtime_service = RealTimeService()