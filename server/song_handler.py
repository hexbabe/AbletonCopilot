from typing import Callable, Dict

import Live
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
            
            if track_name is not None:
                matching_tracks = [t for t in self._song.tracks if t.name == track_name]
                self.log(f"Matching tracks: {[t.name for t in matching_tracks]}") # test this
                if not matching_tracks:
                    return Response(success=False, error=f"No track found with name: {track_name}")
                track = matching_tracks[0]
            elif track_index is not None:
                track_index = int(track_index)
                if track_index >= len(self._song.tracks):
                    return Response(success=False, error="Track index out of range")
                track = self._song.tracks[track_index]
            else:
                return Response(success=False, error="Must specify either track_index or track_name")

            # Verify it's a MIDI track
            if not track.has_midi_input:
                return Response(success=False, error=f"Selected track {track.name} is not a MIDI track")

            # Get clip parameters
            clip_start = float(params.get('clip_start', 0.0))
            clip_length = int(params.get('clip_length', 4.0))

            # Convert beat position to clip slot index (4 beats per slot)
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

    def handle_create_midi_notes(self, params: Dict) -> Response:
        """Create multiple MIDI notes in the specified track and clip slot"""
        try:
            track_index = params.get('track_index')
            track_name = params.get('track_name')
            notes_info = params.get('notes_info', [])

            if track_index is not None:
                track = self._song.tracks[track_index]
            elif track_name is not None:
                matching_tracks = [t for t in self._song.tracks if t.name == track_name]
                if not matching_tracks:
                    return Response(success=False, error=f"No track found with name: {track_name}")
                track = matching_tracks[0]
            else:
                return Response(success=False, error="Must specify either track_index or track_name")

            if not track.has_midi_input:
                return Response(success=False, error=f"Selected track {track.name} is not a MIDI track")

            clip_start = float(params.get('clip_start', 0.0))
            clip_length = int(params.get('clip_length', 4.0))
            clip_slot_index = int(clip_start // 4)
            if clip_slot_index >= len(track.clip_slots):
                return Response(success=False, error="Clip position out of range")
            
            clip_slot = track.clip_slots[clip_slot_index]

            def do_create_midi_notes():
                try:
                    if not track.has_midi_input:
                        raise Exception(f"Track {track.name} is no longer a MIDI track.")
                    if not clip_slot.has_clip:
                        clip_slot.create_clip(clip_length)
                    clip = clip_slot.clip
                    # Create MidiNoteSpecification objects for each note
                    note_specs = [
                        Live.Clip.MidiNoteSpecification(
                            pitch=note_info['note_pitch'],
                            start_time=note_info['note_start'],
                            duration=note_info['note_duration'],
                            velocity=note_info['note_velocity']
                        ) for note_info in notes_info
                    ]
                    # Use the new API to add the notes
                    clip.add_new_notes(note_specs)
                    self.log("Created MIDI notes")
                except Exception as e:
                    self.log(f"Failed to create MIDI notes: {str(e)}")

            self._tasks.add(task.run(do_create_midi_notes))
            
            return Response(success=True, data={
                "track_name": track.name,
                "track_index": list(self._song.tracks).index(track),
                "clip_slot_index": clip_slot_index,
                "clip_start": clip_start,
                "clip_length": clip_length,
                "notes_info": notes_info
            })

        except Exception as e:
            return Response(success=False, error=str(e))
        
    def handle_get_track_names(self, params: Dict) -> Response:
        """Get the names of all tracks in the current song"""
        try:
            return Response(success=True, data={"track_names": [t.name for t in self._song.tracks]})
        except Exception as e:
            return Response(success=False, error=str(e))
        
    def handle_set_track_name(self, params: Dict) -> Response:
        """Set the name of a track"""
        try:
            track_index = params.get('track_index')
            old_name = params.get('old_name')
            new_name = params.get('new_name')
            if new_name == old_name:
                return Response(success=True)
            if not new_name:
                return Response(success=False, error="New name cannot be empty")

            if track_index is not None:
                track = self._song.tracks[track_index]
            elif old_name is not None:
                matching_tracks = [t for t in self._song.tracks if t.name == old_name]
                if not matching_tracks:
                    return Response(success=False, error=f"No track found with name: {old_name}")
                track = matching_tracks[0]
            else:
                return Response(success=False, error="Must specify either track_index or old_name")

            def do_set_track_name():
                try:
                    track.name = new_name
                    self.log(f"Set track name from {old_name} to {new_name}")
                except Exception as e:
                    self.log(f"Failed to set track name: {str(e)}")

            self._tasks.add(task.run(do_set_track_name))
            return Response(success=True)
        except Exception as e:
            return Response(success=False, error=str(e))

    def handle_delete_track(self, params: Dict) -> Response:
        """Delete a track by index or name
        
        Args:
            params: Dict containing either:
                - track_index: int - Index of track to delete
                - track_name: str - Name of track to delete
        """
        try:
            track_index = params.get('track_index')
            track_name = params.get('track_name')
            
            if track_index is None and track_name is None:
                return Response(success=False, error="Must specify either track_index or track_name")
            
            # Find the track to delete
            if track_index is not None:
                if not isinstance(track_index, int):
                    return Response(success=False, error="track_index must be an integer")
                if track_index < 0 or track_index >= len(self._song.tracks):
                    return Response(success=False, error=f"Track index {track_index} out of range")
                track = self._song.tracks[track_index]
            else:
                # Find track by name
                matching_tracks = [t for t in self._song.tracks if t.name == track_name]
                if not matching_tracks:
                    return Response(success=False, error=f"No track found with name: {track_name}")
                if len(matching_tracks) > 1:
                    return Response(success=False, error=f"Multiple tracks found with name: {track_name}")
                track = matching_tracks[0]
                track_index = list(self._song.tracks).index(track)
            
            # Store track info for response
            track_info = {
                "track_index": track_index,
                "track_name": track.name
            }
            
            def do_delete_track():
                try:
                    # Verify track still exists
                    if track_index >= len(self._song.tracks):
                        self.log(f"Track at index {track_index} no longer exists")
                        return
                    if self._song.tracks[track_index] != track:
                        self.log(f"Track at index {track_index} has changed")
                        return
                    self._song.delete_track(track_index)
                    self.log(f"Deleted track: {track_info['track_name']} at index {track_info['track_index']}")
                except Exception as e:
                    self.log(f"Failed to delete track: {str(e)}")
            
            # Schedule track deletion on next tick
            self._tasks.add(task.run(do_delete_track))
            
            return Response(success=True, data=track_info)
            
        except Exception as e:
            return Response(success=False, error=f"Error deleting track: {str(e)}")

    def handle_get_track_index(self, params: Dict) -> Response:
        """Get all indices of tracks matching the given name
        
        Args:
            params: Dict containing:
                - track_name: str - Name of tracks to find
                
        Returns:
            Response with list of track indices matching the name
        """
        try:
            track_name = params.get('track_name')
            if not track_name:
                return Response(success=False, error="track_name parameter is required")
            
            # Find all matching tracks and their indices
            matching_tracks = [
                (i, t) for i, t in enumerate(self._song.tracks) 
                if t.name == track_name
            ]
            
            if not matching_tracks:
                return Response(
                    success=False, 
                    error=f"No tracks found with name: {track_name}"
                )
            
            # Return all matching indices
            indices = [i for i, _ in matching_tracks]
            return Response(
                success=True,
                data={
                    "track_indices": indices,
                    "track_name": track_name,
                    "count": len(indices)
                }
            )
            
        except Exception as e:
            return Response(success=False, error=f"Error getting track indices: {str(e)}")