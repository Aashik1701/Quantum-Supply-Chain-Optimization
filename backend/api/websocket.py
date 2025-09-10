"""
WebSocket events for real-time optimization updates
"""

from flask_socketio import emit, join_room, leave_room
import json


def socketio_events(socketio):
    """Register WebSocket event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print('Client connected')
        emit('status', {'message': 'Connected to optimization service'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print('Client disconnected')
    
    @socketio.on('join_optimization')
    def handle_join_optimization(data):
        """Join optimization room for updates"""
        job_id = data.get('job_id')
        if job_id:
            join_room(job_id)
            emit('joined', {'job_id': job_id})
    
    @socketio.on('leave_optimization')
    def handle_leave_optimization(data):
        """Leave optimization room"""
        job_id = data.get('job_id')
        if job_id:
            leave_room(job_id)
            emit('left', {'job_id': job_id})
    
    def emit_optimization_progress(job_id, progress_data):
        """Emit optimization progress to specific room"""
        socketio.emit('optimization_progress', progress_data, room=job_id)
    
    def emit_optimization_complete(job_id, result_data):
        """Emit optimization completion to specific room"""
        socketio.emit('optimization_complete', result_data, room=job_id)
    
    def emit_optimization_error(job_id, error_data):
        """Emit optimization error to specific room"""
        socketio.emit('optimization_error', error_data, room=job_id)
    
    # Store emit functions for external use
    socketio.emit_progress = emit_optimization_progress
    socketio.emit_complete = emit_optimization_complete
    socketio.emit_error = emit_optimization_error
    
    return socketio
