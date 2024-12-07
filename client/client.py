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

if __name__ == "__main__":
    print("Starting Ableton Live Copilot test suite...")
    run_tests()
