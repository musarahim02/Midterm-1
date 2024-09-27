# Guitar Chord Player Application

This Python application allows you to play guitar chord sounds using either a graphical user interface (GUI) or specific keyboard keys. The app is designed to handle basic guitar chords like A Major, C Major, D Major, E Major, and G Major, and it uses `pygame` for sound playback and `Tkinter` for the user interface.

## Features
- Play guitar chord sounds by pressing buttons on the GUI.
- Play guitar chords by pressing specific keys on your keyboard ('A', 'C', 'D', 'E', 'G').
- Simple, intuitive interface built using `Tkinter`.
- Easily customizable to add more chords.

## Prerequisites

Before running the application, make sure you have the following installed:

1. **Python 3.x**: This app is built for Python 3.x versions.
2. **Pygame**: Install the `pygame` library for handling sound playback:
   ```bash
   pip install pygame

    #project-directory
│
├── /SoundFiles                 # Directory for sound files
│   ├── a_major.wav
│   ├── c_major.wav
│   ├── d_major.wav
│   ├── e_major.wav
│   └── g_major.wav
│
├── guitar_chord_player.py      # Main Python script
├── README.md                   # Project documentation (this file)
