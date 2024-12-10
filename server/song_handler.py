from typing import Dict
from ableton.v2.base import task
from ..protocol.protocol import Response

class SongHandler:
    def __init__(self, song, tasks):
        self._song = song
        self._tasks = tasks # SHARED WITH SERVER

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
                self._song.create_midi_track()
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
