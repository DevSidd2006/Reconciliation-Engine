import socketio
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SocketManager:
    def __init__(self):
        self.server = socketio.AsyncServer(
            async_mode='asgi',
            cors_allowed_origins=['http://localhost:5173', 'http://localhost:3000', '*'],
            logger=False,  # Reduce noise in logs
            engineio_logger=False
        )
        self.app = socketio.ASGIApp(self.server)
        self.connected_clients = set()

    async def emit_to_all(self, event: str, data: Dict[str, Any]):
        """Emit event to all connected clients"""
        if self.connected_clients:
            await self.server.emit(event, data)
            logger.info(f"Emitted {event} to {len(self.connected_clients)} clients")

    async def emit_transaction(self, transaction_data: Dict[str, Any]):
        """Emit new transaction event"""
        await self.emit_to_all('new_transaction', {
            **transaction_data,
            'timestamp': datetime.now().isoformat()
        })

    async def emit_mismatch(self, mismatch_data: Dict[str, Any]):
        """Emit new mismatch event"""
        await self.emit_to_all('new_mismatch', {
            **mismatch_data,
            'timestamp': datetime.now().isoformat()
        })

    async def emit_system_alert(self, alert_data: Dict[str, Any]):
        """Emit system alert event"""
        await self.emit_to_all('system_alert', {
            **alert_data,
            'timestamp': datetime.now().isoformat()
        })

    async def emit_stats_update(self, stats_data: Dict[str, Any]):
        """Emit statistics update event"""
        await self.emit_to_all('stats_update', {
            **stats_data,
            'timestamp': datetime.now().isoformat()
        })

    async def emit_ai_insight(self, insight_data: Dict[str, Any]):
        """Emit AI insight event"""
        await self.emit_to_all('ai_insight', {
            **insight_data,
            'timestamp': datetime.now().isoformat()
        })

    async def emit_transaction_flow_update(self, flow_data: Dict[str, Any]):
        """Emit transaction flow update for real-time charts"""
        await self.emit_to_all('transaction_flow_update', {
            **flow_data,
            'timestamp': datetime.now().isoformat()
        })

socket_manager = SocketManager()

@socket_manager.server.event
async def connect(sid, environ):
    """Handle client connection"""
    socket_manager.connected_clients.add(sid)
    logger.info(f"Client connected: {sid} (Total: {len(socket_manager.connected_clients)})")
    
    # Send welcome message with connection status
    await socket_manager.server.emit('connection_status', {
        'status': 'connected',
        'client_id': sid,
        'timestamp': datetime.now().isoformat()
    }, room=sid)

@socket_manager.server.event
async def disconnect(sid):
    """Handle client disconnection"""
    socket_manager.connected_clients.discard(sid)
    logger.info(f"Client disconnected: {sid} (Total: {len(socket_manager.connected_clients)})")

@socket_manager.server.event
async def join_room(sid, data):
    """Handle client joining specific rooms for targeted updates"""
    room = data.get('room')
    if room:
        await socket_manager.server.enter_room(sid, room)
        logger.info(f"Client {sid} joined room: {room}")

@socket_manager.server.event
async def leave_room(sid, data):
    """Handle client leaving specific rooms"""
    room = data.get('room')
    if room:
        await socket_manager.server.leave_room(sid, room)
        logger.info(f"Client {sid} left room: {room}")

@socket_manager.server.event
async def ping(sid, data):
    """Handle ping from client for connection testing"""
    await socket_manager.server.emit('pong', {
        'timestamp': datetime.now().isoformat(),
        'client_id': sid
    }, room=sid)
