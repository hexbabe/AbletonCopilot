from __future__ import absolute_import

import os
import socket
import threading
import traceback
from datetime import datetime
from typing import Optional, Dict, Callable

from ableton.v2.control_surface import ControlSurface

from ..protocol.protocol import Command, Response, CommandType
from .song_handler import SongHandler

class AbletonCopilotServer(ControlSurface):
    """Main server class that handles socket connections and Live set control"""

    def __init__(self, c_instance, log):
        self._c_instance = c_instance
        self.log: Callable = log
        self._do_send_midi = self._c_instance.send_midi

        # Initialize base ControlSurface
        super().__init__(c_instance=c_instance)

        # Get song reference
        self._song = self.song

        # Socket server settings
        self.host = '127.0.0.1'
        self.port = 9001
        self.server: Optional[socket.socket] = None
        self.server_thread: Optional[threading.Thread] = None
        
        # Initialize song handler
        if not hasattr(self._song, 'tempo') or not hasattr(self._tasks, 'add'):
            raise AttributeError("Required attributes 'tempo' and 'add' are missing from song or tasks.")
        self.song_handler = SongHandler(self._song, self._tasks, self.log)
        
        self.command_handlers: Dict[CommandType, Callable] = {
            CommandType.SET_TEMPO: self.song_handler.handle_set_tempo,
            CommandType.GET_TEMPO: self.song_handler.handle_get_tempo,
            CommandType.PLAY: self.song_handler.handle_play,
            CommandType.STOP: self.song_handler.handle_stop,
            CommandType.GET_PLAYING_STATUS: self.song_handler.handle_get_playing_status,
            CommandType.CREATE_MIDI_TRACK: self.song_handler.handle_create_midi_track,
            CommandType.CREATE_MIDI_CLIP: self.song_handler.handle_create_midi_clip,
            CommandType.CREATE_MIDI_NOTES: self.song_handler.handle_create_midi_notes,
            CommandType.GET_TRACK_NAMES: self.song_handler.handle_get_track_names,
            CommandType.SET_TRACK_NAME: self.song_handler.handle_set_track_name,
            CommandType.DELETE_TRACK: self.song_handler.handle_delete_track,
            CommandType.GET_TRACK_INDEX: self.song_handler.handle_get_track_index
        }
        
        self.log("Copilot script initializing...")
        try:
            self.start_server()
            self.log(f"Server started successfully on port {self.port}")
        except Exception as e:
            self.log(f"Error starting server: {str(e)}")
            self.log(traceback.format_exc())
    
    def log_message(self, message: str) -> None:
        """Log a message to our custom log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_line = f"[{timestamp}] {message}\n"

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
            self.server.listen(5)
            
            self.server_thread = threading.Thread(target=self.handle_connections)
            self.server_thread.daemon = True
            self.server_thread.start()
        except Exception as e:
            self.log(f"Error in start_server: {str(e)}")
            raise

    def handle_connections(self) -> None:
        """Listen for and handle incoming connections."""
        while True:
            try:
                client, address = self.server.accept()
                threading.Thread(target=self.handle_client, 
                               args=(client, address)).start()
            except Exception as e:
                self.log(f"Connection handling error: {str(e)}")
                continue

    def handle_client(self, client: socket.socket, address: tuple) -> None:
        """Handle a single client connection"""
        try:
            with client:
                data = client.recv(4096).decode()
                self.log(f"Received data from {address}: {data}")
                
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
                
        except Exception as e:
            self.log(f"Error handling client {address}: {str(e)}")
            self.log(traceback.format_exc())

    def disconnect(self) -> None:
        """Clean up on script shutdown."""
        self.log("Copilot script disconnecting...")
        if hasattr(self, '_tasks'):
            self._tasks.kill()
        if hasattr(self, 'server'):
            self.server.close()
        super().disconnect()
