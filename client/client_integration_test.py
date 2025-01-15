from client.client import LiveClient
import time

class AbletonLiveTestSuite:
    def __init__(self):
        self.client = LiveClient()

    def print_test_header(self, name: str):
        print(f"\n{'='*20} Testing {name} {'='*20}")

    def test_get_initial_tempo(self):
        self.print_test_header("Initial Tempo")
        response = self.client.get_tempo()
        if response.success:
            print(f"Current tempo is {response.data['tempo']} BPM")
        else:
            print(f"Error: {response.error}")

    def test_set_tempo(self, new_tempo):
        self.print_test_header("Setting Tempo")
        response = self.client.set_tempo(new_tempo)
        if response.success:
            print(f"Changed tempo from {response.data['old_tempo']} to {response.data['new_tempo']} BPM")
        else:
            print(f"Error: {response.error}")

    def test_verify_tempo_change(self):
        self.print_test_header("Verifying Tempo Change")
        response = self.client.get_tempo()
        if response.success:
            print(f"Current tempo is {response.data['tempo']} BPM")
        else:
            print(f"Error: {response.error}")

    def test_get_initial_playing_status(self):
        self.print_test_header("Initial Playing Status")
        response = self.client.get_playing_status()
        if response.success:
            print(f"Currently playing: {response.data['is_playing']}")
        else:
            print(f"Error: {response.error}")

    def test_start_playback(self):
        self.print_test_header("Starting Playback")
        response = self.client.play()
        if response.success:
            print("Started playback")
        else:
            print(f"Error: {response.error}")

    def test_verify_playing_status(self):
        self.print_test_header("Verifying Playing Status")
        response = self.client.get_playing_status()
        if response.success:
            print(f"Currently playing: {response.data['is_playing']}")
        else:
            print(f"Error: {response.error}")

    def test_stop_playback(self):
        self.print_test_header("Stopping Playback")
        response = self.client.stop()
        if response.success:
            print("Stopped playback")
        else:
            print(f"Error: {response.error}")

    def test_final_playing_status_check(self):
        self.print_test_header("Final Playing Status")
        response = self.client.get_playing_status()
        if response.success:
            print(f"Currently playing: {response.data['is_playing']}")
        else:
            print(f"Error: {response.error}")

    def test_create_midi_track(self, track_name):
        self.print_test_header("Creating MIDI Track")
        response = self.client.create_midi_track(track_name)
        if response.success:
            print(f"Created MIDI track '{response.data['track_name']}' at index {response.data['track_index']}")
        else:
            print(f"Error: {response.error}")

    def test_create_midi_clip_by_index(self, track_index, clip_start, clip_length):
        self.print_test_header("Creating MIDI Clip by Index")
        response = self.client.create_midi_clip(
            track_index=track_index,
            clip_start=clip_start,
            clip_length=clip_length
        )
        if response.success:
            print(f"Created MIDI clip in track {response.data['track_name']}")
            print(f"Clip position: {response.data['clip_slot_index']}")
            print(f"Clip length: {response.data['clip_length']} beats")
        else:
            print(f"Error: {response.error}")

    def test_create_midi_clip_by_name(self, track_name, clip_start, clip_length):
        self.print_test_header("Creating MIDI Clip by Name")
        response = self.client.create_midi_clip(
            track_name=track_name,
            clip_start=clip_start,
            clip_length=clip_length
        )
        if response.success:
            print(f"Created MIDI clip in track {response.data['track_name']}")
            print(f"Clip slot index: {response.data['clip_slot_index']}")
            print(f"Clip length: {response.data['clip_length']} beats")
        else:
            print(f"Error: {response.error}")

    def test_create_midi_notes(self, track_index, notes_info):
        self.print_test_header("Creating MIDI Notes")
        response = self.client.create_midi_notes(
            track_index=track_index,
            notes_info=notes_info
        )
        if response.success:
            print(f"Created MIDI notes in track {response.data['track_name']}")
            for note in response.data['notes_info']:
                print(f"Note pitch: {note['note_pitch']}, start: {note['note_start']}, duration: {note['note_duration']}, velocity: {note['note_velocity']}")
        else:
            print(f"Error: {response.error}")

    def test_get_track_names(self):
        self.print_test_header("Getting Track Names")
        response = self.client.get_track_names()
        if response.success:
            print(f"Track names: {response.data['track_names']}")
        else:
            print(f"Error: {response.error}")

    def test_set_track_name_by_index(self, track_index, new_name):
        self.print_test_header("Setting Track Name by Index")
        response = self.client.set_track_name(track_index, None, new_name)
        if response.success:
            print("Track name set successfully")
        else:
            print(f"Error: {response.error}")

    def test_set_track_name_by_name(self, old_name, new_name):
        self.print_test_header("Setting Track Name by Name Only")
        response = self.client.set_track_name(None, old_name, new_name)
        if response.success:
            print("Track name set successfully")
        else:
            print(f"Error: {response.error}")

    def test_delete_track_by_index(self, track_index):
        self.print_test_header("Deleting Track")
        response = self.client.delete_track(track_index=track_index)
        if response.success:
            print(f"Deleted track '{response.data['track_name']}' at index {response.data['track_index']}")
        else:
            print(f"Error: {response.error}")

    def test_delete_track_by_name(self, track_name):
        self.print_test_header("Deleting Track with Name Only")
        response = self.client.delete_track(track_name=track_name)
        if response.success:
            print(f"Deleted track '{response.data['track_name']}' at index {response.data['track_index']}")
        else:
            print(f"Error: {response.error}")

    def test_get_track_index(self, track_name):
        self.print_test_header("Getting Track Index")
        # Create multiple tracks with the same name
        self.client.create_midi_track(track_name)
        self.client.create_midi_track(track_name)
        
        # Get indices
        response = self.client.get_track_index(track_name)
        if response.success:
            print(f"Found {response.data['count']} tracks named '{response.data['track_name']}'")
            print(f"Track indices: {response.data['track_indices']}")
        else:
            print(f"Error: {response.error}")

        # Test with nonexistent track
        self.print_test_header("Getting Nonexistent Track Index")
        response = self.client.get_track_index("NonexistentTrack")
        if not response.success:
            print("Successfully caught nonexistent track exception")
        else:
            print("Error: Should not have found nonexistent track")

    def run_all_tests(self):
        self.test_get_initial_tempo()
        self.test_set_tempo(128.0)
        self.test_verify_tempo_change()
        self.test_get_initial_playing_status()
        self.test_start_playback()
        time.sleep(2)
        self.test_verify_playing_status()
        self.test_stop_playback()
        self.test_final_playing_status_check()
        self.test_create_midi_track("Test Create Midi Track")
        self.test_create_midi_clip_by_index(-1, 1.0, 4.0)
        self.test_create_midi_track("Test Create Midi Clip")
        self.test_create_midi_clip_by_name("Test Create Midi Clip", 4.0, 8.0)
        self.test_create_midi_notes(-1, [
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
        ])
        self.test_get_track_names()
        self.test_create_midi_track("foo")
        self.test_set_track_name_by_index(-1, "Test Rename Track Name 1")
        self.test_set_track_name_by_name("Test Rename Track Name 1", "Test Rename Track Name 2")
        self.test_delete_track_by_index(0)
        self.test_delete_track_by_name("Test Rename Track Name 2")
        test_name = f"Index Test Track {time.time()}"
        self.test_get_track_index(test_name)

if __name__ == "__main__":
    print("Starting Ableton Live Copilot test suite...")
    test_suite = AbletonLiveTestSuite()
    test_suite.run_all_tests()
