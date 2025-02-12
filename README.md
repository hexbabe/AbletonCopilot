# Ableton Live Copilot

An AI-powered music production assistant that enables natural language control of Ableton Live. This project bridges the gap between human creativity and digital audio workstations by allowing producers to control Ableton Live using plain English commands.

## Overview

Ableton Live Copilot provides a bridge between Python applications and Ableton Live, allowing you to:
- Control playback (play/stop)
- Modify tempo
- Create and manage MIDI tracks
- Create and manipulate MIDI clips
- Add MIDI notes programmatically
- Manage track names and organization

## Architecture

The project consists of three main components:

1. **Server** (`server/`): A Python-based server that runs as an Ableton Live Control Surface, handling commands and interfacing directly with Live.
   - Implements command handlers for all supported operations
   - Manages Live set modifications through Live's API
   - Handles task scheduling for Live-safe operations

2. **Client** (`client/`): A Python client library that applications can use to send commands to Live.
   - Provides a clean, typed API for all supported operations
   - Handles communication with the server
   - Includes error handling and parameter validation

3. **Protocol** (`protocol/`): Defines the communication protocol between client and server.
   - Uses JSON for data serialization
   - Implements command and response structures
   - Provides type safety through Python enums and dataclasses

## Some Features

- **Track Management**
  - Create MIDI tracks
  - Delete tracks
  - Rename tracks
  - Get track indices and names

- **MIDI Operations**
  - Create MIDI clips
  - Add MIDI notes with precise timing
  - Control clip length and position

- **Transport Control**
  - Start/stop playback
  - Get playing status
  - Set and get tempo

## Getting Started

1. Install/clone this repo and the Copilot server script in your Ableton Live MIDI Remote Scripts folder
2. Enable the Copilot script in Live's MIDI preferences
3. Use the Python LLM to start controlling Live
