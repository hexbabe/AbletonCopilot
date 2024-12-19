import socket
import time

from protocol.protocol import Command, Response, CommandType

class LiveClient:
    """Client for interacting with Ableton Live via the Copilot server"""
    
    def __init__(self, host: str = '127.0.0.1', port: int = 9001):
        self.host = host
        self.port = port

    def send_command(self, command: Command) -> Response:
        """Send a command to the Live server and return the response"""
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.host, self.port))
            
            # Send command
            client.send(command.to_json().encode())
            
            # Receive response
            response_data = client.recv(1024).decode()
            response = Response.from_json(response_data)
            
            client.close()
            return response
        except Exception as e:
            return Response(success=False, error=str(e))

    def set_tempo(self, bpm: float) -> Response:
        """Set the tempo to the specified BPM"""
        command = Command(
            command=CommandType.SET_TEMPO,
            params={'bpm': bpm}
        )
        return self.send_command(command)

    def get_tempo(self) -> Response:
        """Get the current tempo"""
        command = Command(command=CommandType.GET_TEMPO)
        return self.send_command(command)

    def play(self) -> Response:
        """Start playback"""
        command = Command(command=CommandType.PLAY)
        return self.send_command(command)

    def stop(self) -> Response:
        """Stop playback"""
        command = Command(command=CommandType.STOP)
        return self.send_command(command)

    def get_playing_status(self) -> Response:
        """Get current playing status"""
        command = Command(command=CommandType.GET_PLAYING_STATUS)
        return self.send_command(command)
    
    def create_midi_track(self, name: str) -> Response:
        """Create a new MIDI track with the specified name"""
        command = Command(
            command=CommandType.CREATE_MIDI_TRACK,
            params={'name': name}
        )
        return self.send_command(command)

    def create_midi_clip(self, track_index=None, track_name=None, clip_start=0.0, clip_length=4.0) -> Response:
        """Create a MIDI clip in the specified track. Between track index and track name, please specify one.

        Parameters:
            track_index (Optional[int]): The index of the track where the MIDI clip will be created.
            track_name (Optional[str]): The name of the track where the MIDI clip will be created.
            clip_start (float): The start time of the clip in beats.
            clip_length (float): The length of the clip in beats.
        """
        command = Command(
            command=CommandType.CREATE_MIDI_CLIP,
            params={
                'track_index': track_index,
                'track_name': track_name,
                'clip_start': clip_start,
                'clip_length': clip_length
            }
        )
        return self.send_command(command)

    def create_midi_notes(self, track_index=None, track_name=None, notes_info=None) -> Response:
        """Create multiple MIDI notes in the specified track and clip slot.

        Parameters:
            track_index (Optional[int]): The index of the track where the MIDI notes will be created.
            track_name (Optional[str]): The name of the track where the MIDI notes will be created.
            notes_info (List[Dict[str, Union[int, float]]]): A list of dictionaries, each required, each representing a MIDI note with the following schema:
                - note_pitch (int): The pitch of the note (MIDI number).
                - note_start (float): The start time of the note in beats.
                - note_duration (float): The duration of the note in beats.
                - note_velocity (int): The velocity of the note.
        """
        if not isinstance(notes_info, list) or len(notes_info) == 0:
            raise ValueError("notes_info is required as a list of dictionaries with pitch, start_time, duration, and velocity keys")
        command = Command(
            command=CommandType.CREATE_MIDI_NOTES,
            params={
                'track_index': track_index,
                'track_name': track_name,
                'notes_info': notes_info
            }
        )
        return self.send_command(command)
