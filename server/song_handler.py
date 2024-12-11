from typing import Callable, Dict
from ableton.v2.base import task
from ..protocol.protocol import Response

class SongHandler:
    def __init__(self, song, tasks, log: Callable):
        self._song = song
        self._tasks = tasks # SHARED WITH SERVER
        self.log = log

    def handle_set_tempo(self, params: Dict) -> Response:
        """Set the tempo in the Live set"""
        try:
            bpm = float(params.get('bpm', 120.0))
            old_tempo = self._song.tempo
            self._song.tempo = bpm
            return Response(
                success=True,
                data={"old_tempo": old_tempo, "new_tempo": bpm}
            )
        except Exception as e:
            return Response(success=False, error=str(e))

    def handle_get_tempo(self, params: Dict) -> Response:
        """Get the current tempo"""
        try:
            return Response(
                success=True,
                data={"tempo": self._song.tempo}
            )
        except Exception as e:
            return Response(success=False, error=str(e))

    def handle_play(self, params: Dict) -> Response:
        """Start playback"""
        try:
            self._song.start_playing()
            return Response(
                success=True,
                data={"is_playing": True}
            )
        except Exception as e:
            return Response(success=False, error=str(e))

    def handle_stop(self, params: Dict) -> Response:
        """Stop playback"""
        try:
            self._song.stop_playing()
            return Response(
                success=True,
                data={"is_playing": False}
            )
        except Exception as e:
            return Response(success=False, error=str(e))

    def handle_get_playing_status(self, params: Dict) -> Response:
        """Get current playing status"""
        try:
            return Response(
                success=True,
                data={"is_playing": self._song.is_playing}
            )
        except Exception as e:
            return Response(success=False, error=str(e))

    def handle_create_midi_track(self, params: Dict) -> Response:
        """Create a new MIDI track with specified name"""
        try:
            track_name = params.get('name', 'New MIDI Track')
            pre_track_count = len(self._song.tracks)
            
            def do_create_track():
                self._song.create_midi_track(-1)
                if len(self._song.tracks) > pre_track_count:
                    new_track = self._song.tracks[-1]
                    new_track.name = track_name

            self._tasks.add(task.run(do_create_track))
            
            return Response(
                success=True,
                data={
                    "track_name": track_name,
                    "track_index": pre_track_count
                }
            )
        except Exception as e:
            return Response(success=False, error=str(e)) 

    def handle_create_midi_clip(self, params: Dict) -> Response:
        """Create a MIDI clip in the specified track"""
        try:
            # Get track by index or name
            track_index = params.get('track_index')
            track_name = params.get('track_name')
            
            if track_index is not None:
                track_index = int(track_index)
                if track_index >= len(self._song.tracks):
                    return Response(success=False, error="Track index out of range")
                track = self._song.tracks[track_index]
            elif track_name is not None:
                matching_tracks = [t for t in self._song.tracks if t.name == track_name]
                if not matching_tracks:
                    return Response(success=False, error=f"No track found with name: {track_name}")
                track = matching_tracks[0]
            else:
                return Response(success=False, error="Must specify either track_index or track_name")

            # Verify it's a MIDI track
            if not track.has_midi_input:
                return Response(success=False, error=f"Selected track {track.name} is not a MIDI track")

            # Get clip parameters
            clip_start = float(params.get('clip_start', 0.0))
            clip_length = int(params.get('clip_length', 4.0))

            # Find the clip slot at the specified position
            clip_slot_index = int(clip_start // 4)
            if clip_slot_index >= len(track.clip_slots):
                return Response(success=False, error="Clip position out of range")
            
            clip_slot = track.clip_slots[clip_slot_index]

            def do_create_clip():
                try:
                    # Re-validate track's MIDI input
                    if not track.has_midi_input:
                        raise Exception(f"Track {track.name} is no longer a MIDI track.")
                    # Create the clip directly with position and length
                    if clip_slot.has_clip:
                        clip_slot.delete_clip()
                    clip_slot.create_clip(clip_length)
                    self.log("Created clip")
                except Exception as e:
                    self.log(f"Failed to create clip: {str(e)}")

            self._tasks.add(task.run(do_create_clip))
            
            return Response(success=True, data={
                "track_name": track.name,
                "track_index": list(self._song.tracks).index(track),
                "clip_slot_index": clip_slot_index,
                "clip_start": clip_start,
                "clip_length": clip_length
            })

        except Exception as e:
            return Response(success=False, error=str(e))
