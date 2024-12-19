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

def run_tests():
    """Run a series of tests to verify all functionality"""
    client = LiveClient()
    
    def print_test_header(name: str):
        print(f"\n{'='*20} Testing {name} {'='*20}")

    # Test 1: Get initial tempo
    print_test_header("Initial Tempo")
    response = client.get_tempo()
    if response.success:
        print(f"Current tempo is {response.data['tempo']} BPM")
    else:
        print(f"Error: {response.error}")

    # Test 2: Set new tempo
    print_test_header("Setting Tempo")
    new_tempo = 128.0
    response = client.set_tempo(new_tempo)
    if response.success:
        print(f"Changed tempo from {response.data['old_tempo']} to {response.data['new_tempo']} BPM")
    else:
        print(f"Error: {response.error}")

    # Test 3: Verify tempo change
    print_test_header("Verifying Tempo Change")
    response = client.get_tempo()
    if response.success:
        print(f"Current tempo is {response.data['tempo']} BPM")
    else:
        print(f"Error: {response.error}")

    # Test 4: Get initial playing status
    print_test_header("Initial Playing Status")
    response = client.get_playing_status()
    if response.success:
        print(f"Currently playing: {response.data['is_playing']}")
    else:
        print(f"Error: {response.error}")

    # Test 5: Start playback
    print_test_header("Starting Playback")
    response = client.play()
    if response.success:
        print("Started playback")
    else:
        print(f"Error: {response.error}")

    # Short delay to let it play
    time.sleep(2)

    # Test 6: Verify playing status
    print_test_header("Verifying Playing Status")
    response = client.get_playing_status()
    if response.success:
        print(f"Currently playing: {response.data['is_playing']}")
    else:
        print(f"Error: {response.error}")

    # Test 7: Stop playback
    print_test_header("Stopping Playback")
    response = client.stop()
    if response.success:
        print("Stopped playback")
    else:
        print(f"Error: {response.error}")

    # Test 8: Final playing status check
    print_test_header("Final Playing Status")
    response = client.get_playing_status()
    if response.success:
        print(f"Currently playing: {response.data['is_playing']}")
    else:
        print(f"Error: {response.error}")

    # Test 9: Create MIDI Track
    print_test_header("Creating MIDI Track")
    track_name = "Test MIDI Track"
    response = client.create_midi_track(track_name)
    if response.success:
        print(f"Created MIDI track '{response.data['track_name']}' at index {response.data['track_index']}")
    else:
        print(f"Error: {response.error}")
    
    # Test 10: Create MIDI Clip by Track Index
    print_test_header("Creating MIDI Clip by Index")
    response = client.create_midi_clip(
        track_index=0,
        clip_start=1.0,
        clip_length=4.0
    )
    if response.success:
        print(f"Created MIDI clip in track {response.data['track_name']}")
        print(f"Clip position: {response.data['clip_slot_index']}")
        print(f"Clip length: {response.data['clip_length']} beats")
    else:
        print(f"Error: {response.error}")

    # Test 11: Create MIDI Clip by Track Name
    print_test_header("Creating MIDI Clip by Name")
    response = client.create_midi_clip(
        track_name="Test MIDI Track",
        clip_start=4.0,  # Start at bar 2
        clip_length=8.0  # 2 bars long
    )
    if response.success:
        print(f"Created MIDI clip in track {response.data['track_name']}")
        print(f"Clip slot index: {response.data['clip_slot_index']}")
        print(f"Clip length: {response.data['clip_length']} beats")
    else:
        print(f"Error: {response.error}")

    # Test 12: Create MIDI Notes
    print_test_header("Creating MIDI Notes")
    response = client.create_midi_notes(
        track_index=0,
        notes_info=[
            {
                'note_pitch': 60,
                'note_start': 0.0,
                'note_duration': 1.0,
                'note_velocity': 100
            },
            {
                'note_pitch': 62,
                'note_start': 1.0,
                'note_duration': 1.0,
                'note_velocity': 100
            }
        ]
    )
    if response.success:
        print(f"Created MIDI notes in track {response.data['track_name']}")
        for note in response.data['notes_info']:
            print(f"Note pitch: {note['note_pitch']}, start: {note['note_start']}, duration: {note['note_duration']}, velocity: {note['note_velocity']}")
    else:
        print(f"Error: {response.error}")

if __name__ == "__main__":
    print("Starting Ableton Live Copilot test suite...")
    run_tests()
