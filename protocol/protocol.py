from dataclasses import dataclass
from enum import Enum, auto
import json
from typing import Optional, Dict, Any

class CommandType(Enum):
    """Enumeration of all available command types"""
    SET_TEMPO = "set_tempo"
    GET_TEMPO = "get_tempo"
    PLAY = "play"
    STOP = "stop"
    GET_PLAYING_STATUS = "get_playing_status"
    CREATE_MIDI_TRACK = "create_midi_track"

@dataclass
class Command:
    """Represents a command sent from client to server"""
    command: CommandType
    params: Optional[Dict[str, Any]] = None

    @classmethod
    def from_json(cls, json_str: str) -> 'Command':
        """Create Command instance from JSON string"""
        data = json.loads(json_str)
        return cls(
            command=CommandType(data['command']),
            params=data.get('params')
        )

    def to_json(self) -> str:
        """Convert Command to JSON string"""
        return json.dumps({
            'command': self.command.value,
            'params': self.params or {}
        })

@dataclass
class Response:
    """Represents a response sent from server to client"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_json(self) -> str:
        """Convert Response to JSON string"""
        return json.dumps({
            'success': self.success,
            'data': self.data or {},
            'error': self.error
        })

    @classmethod
    def from_json(cls, json_str: str) -> 'Response':
        """Create Response instance from JSON string"""
        data = json.loads(json_str)
        return cls(
            success=data['success'],
            data=data.get('data'),
            error=data.get('error')
        )
