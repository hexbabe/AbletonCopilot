from client.client import LiveClient
import time

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
