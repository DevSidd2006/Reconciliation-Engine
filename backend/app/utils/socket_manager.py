import socketio

class SocketManager:
    def __init__(self):
        self.server = socketio.AsyncServer(
            async_mode='asgi',
            cors_allowed_origins='*',
            logger=True,
            engineio_logger=True
        )
        self.app = socketio.ASGIApp(self.server)

    async def emit_transaction(self, transaction_data):
        await self.server.emit('new_transaction', transaction_data)

    async def emit_mismatch(self, mismatch_data):
        await self.server.emit('new_mismatch', mismatch_data)

socket_manager = SocketManager()

@socket_manager.server.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@socket_manager.server.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
