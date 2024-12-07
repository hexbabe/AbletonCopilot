from __future__ import absolute_import
import socket
import threading
from typing import Optional, Dict, Callable
from ableton.v2.control_surface import ControlSurface
from _Framework.ControlSurface import ControlSurface as CSurface
import Live
import traceback
import os
from datetime import datetime
from ..protocol.protocol import Command, Response, CommandType
from .live_handlers import LiveSetHandler

class AbletonCopilotServer:
    def __init__(self, c_instance: CSurface) -> None:
        """Initialize the script."""
        self.c_instance: CSurface = c_instance
        self.song: Live.Song.Song = self.c_instance.song()
        
        # Initialize handlers
        self.live_handler = LiveSetHandler(self.song)
        
        # Socket server settings
        self.host: str = '127.0.0.1'
        self.port: int = 9001
        self.server: Optional[socket.socket] = None
        self.server_thread: Optional[threading.Thread] = None
        
        # Custom log file setup
        self.log_file_path = os.path.expanduser('~/Desktop/copilot_live.log')
        
        # Map commands to handler methods
        self.command_handlers: Dict[CommandType, Callable] = {
            CommandType.SET_TEMPO: self.live_handler.set_tempo,
            CommandType.GET_TEMPO: self.live_handler.get_tempo,
            CommandType.PLAY: self.live_handler.play,
            CommandType.STOP: self.live_handler.stop,
            CommandType.GET_PLAYING_STATUS: self.live_handler.get_playing_status
        }
        
        self.log_message("Copilot script initializing...")
        try:
            self.start_server()
            self.log_message(f"Server started successfully on port {self.port}")
        except Exception as e:
            self.log_message(f"Error starting server: {str(e)}")
            self.log_message(traceback.format_exc())
    
    def log_message(self, message: str) -> None:
        """Log a message to both Live's log (if available) and our custom log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_line = f"[{timestamp}] {message}\n"
        
        if hasattr(self.c_instance, 'log_message'):
            self.c_instance.log_message(str(message))
        
        try:
            with open(self.log_file_path, 'a') as f:
                f.write(log_line)
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    def start_server(self) -> None:
        """Initialize and start the socket server in a separate thread."""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(1)
            
            self.server_thread = threading.Thread(target=self.listen_for_connections)
            self.server_thread.daemon = True
            self.server_thread.start()
        except Exception as e:
            self.log_message(f"Error in start_server: {str(e)}")
            raise
        
    def listen_for_connections(self) -> None:
        """Listen for and handle incoming connections."""
        while True:
            try:
                client, address = self.server.accept()
                self.log_message(f"New connection from {address}")
                
                data = client.recv(1024).decode()
                self.log_message(f"Received data: {data}")
                
                try:
                    command = Command.from_json(data)
                    handler = self.command_handlers.get(command.command)
                    
                    if handler:
                        response = handler(command.params or {})
                    else:
                        response = Response(
                            success=False,
                            error=f"Unknown command: {command.command}"
                        )
                except Exception as e:
                    response = Response(
                        success=False,
                        error=f"Error processing command: {str(e)}"
                    )
                
                client.send(response.to_json().encode())
                client.close()
                
            except Exception as e:
                self.log_message(f"Error handling connection: {str(e)}")
                self.log_message(traceback.format_exc())
                continue
    
    def disconnect(self) -> None:
        """Clean up on script shutdown."""
        self.log_message("Copilot script disconnecting...")
        if self.server:
            self.server.close()