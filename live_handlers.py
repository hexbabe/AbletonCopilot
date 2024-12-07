import Live
from typing import Dict
from .protocol import Response

class LiveSetHandler:
    """Handles all interactions with the Live set"""
    
    def __init__(self, song: Live.Song.Song):
        self.song = song

    def set_tempo(self, params: Dict) -> Response:
        """Set the tempo in the Live set"""
        try:
            bpm = float(params.get('bpm', 120.0))
            old_tempo = self.song.tempo
            self.song.tempo = bpm
            return Response(
                success=True,
                data={"old_tempo": old_tempo, "new_tempo": bpm}
            )
        except Exception as e:
            return Response(success=False, error=str(e))

    def get_tempo(self, params: Dict) -> Response:
        """Get the current tempo"""
        try:
            return Response(
                success=True,
                data={"tempo": self.song.tempo}
            )
        except Exception as e:
            return Response(success=False, error=str(e))

    def play(self, params: Dict) -> Response:
        """Start playback"""
        try:
            self.song.start_playing()
            return Response(
                success=True,
                data={"is_playing": True}
            )
        except Exception as e:
            return Response(success=False, error=str(e))

    def stop(self, params: Dict) -> Response:
        """Stop playback"""
        try:
            self.song.stop_playing()
            return Response(
                success=True,
                data={"is_playing": False}
            )
        except Exception as e:
            return Response(success=False, error=str(e))

    def get_playing_status(self, params: Dict) -> Response:
        """Get current playing status"""
        try:
            return Response(
                success=True,
                data={"is_playing": self.song.is_playing}
            )
        except Exception as e:
            return Response(success=False, error=str(e))
