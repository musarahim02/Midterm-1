import pygame
import numpy as np
import tkinter as tk
from tkinter import messagebox
import threading
import time

# Initialize pygame mixer
SAMPLE_RATE = 44100  # Samples per second
pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1)

def generate_tone(frequency, duration=1.0, volume=1.0, waveform='sine', adsr=(0.01, 0.1, 0.8, 0.1)):
    n_samples = int(round(duration * SAMPLE_RATE))
    t = np.linspace(0, duration, n_samples, endpoint=False)

    # Generate the waveform
    if waveform == 'sine':
        wave = np.sin(2 * np.pi * frequency * t)
    elif waveform == 'square':
        wave = np.sign(np.sin(2 * np.pi * frequency * t))
    elif waveform == 'sawtooth':
        wave = 2 * (t * frequency - np.floor(0.5 + t * frequency))
    elif waveform == 'triangle':
        wave = 2 * np.abs(2 * (t * frequency - np.floor(0.5 + t * frequency))) - 1
    else:
        wave = np.sin(2 * np.pi * frequency * t)  # Default to sine

    # Apply ADSR envelope
    attack, decay, sustain_level, release = adsr
    adsr_envelope = np.ones_like(wave)
    attack_samples = int(attack * SAMPLE_RATE)
    decay_samples = int(decay * SAMPLE_RATE)
    release_samples = int(release * SAMPLE_RATE)
    sustain_samples = n_samples - attack_samples - decay_samples - release_samples

    if attack_samples > 0:
        adsr_envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    if decay_samples > 0:
        adsr_envelope[attack_samples:attack_samples+decay_samples] = np.linspace(1, sustain_level, decay_samples)
    if sustain_samples > 0:
        adsr_envelope[attack_samples+decay_samples:attack_samples+decay_samples+sustain_samples] = sustain_level
    if release_samples > 0:
        adsr_envelope[-release_samples:] = np.linspace(sustain_level, 0, release_samples)

    wave *= adsr_envelope

    # Normalize the waveform
    wave *= volume / np.max(np.abs(wave))

    # Convert to 16-bit signed integers
    wave_integers = np.int16(wave * 32767)
    sound = pygame.sndarray.make_sound(wave_integers)
    return sound

def add_echo(sound_array, delay, attenuation):
    delay_samples = int(delay * SAMPLE_RATE)
    echo_wave = np.zeros(len(sound_array) + delay_samples)
    echo_wave[:len(sound_array)] += sound_array
    echo_wave[delay_samples:] += sound_array * attenuation
    return echo_wave[:len(sound_array)]  # Return the original length

def add_reverb(sound_array, delays, attenuations):
    reverb_wave = np.copy(sound_array)
    for delay, attenuation in zip(delays, attenuations):
        delay_samples = int(delay * SAMPLE_RATE)
        reverb_wave[delay_samples:] += sound_array[:-delay_samples] * attenuation
    return reverb_wave

def strum_chord(note_names, duration=1.0, volume=1.0, strum_delay=0.1, waveform='sine', adsr=(0.01, 0.1, 0.8, 0.1),
                effect='None', stop_event=None, playing_channels=None):
    total_samples = int(duration * SAMPLE_RATE)
    chord_wave = np.zeros(total_samples)
    for note in note_names:
        if stop_event and stop_event.is_set():
            break
        freq = note_frequencies.get(note)
        if freq:
            freq *= 2 ** app.octave_shift.get()  # Apply octave shift
            sound = generate_tone(freq, duration, volume, waveform, adsr)
            sound_array = pygame.sndarray.array(sound)
            chord_wave[:len(sound_array)] += sound_array.flatten()
            time.sleep(strum_delay)  # Delay between notes
        else:
            messagebox.showerror("Error", f"Frequency for note '{note}' not found.")
            return

    # Apply effects
    chord_wave = chord_wave.astype(np.float32)
    if effect == 'Echo':
        chord_wave = add_echo(chord_wave, delay=0.2, attenuation=0.6)
    elif effect == 'Reverb':
        delays = [0.03, 0.05, 0.07]
        attenuations = [0.6, 0.4, 0.3]
        chord_wave = add_reverb(chord_wave, delays, attenuations)

    # Normalize to prevent clipping
    max_val = np.max(np.abs(chord_wave))
    if max_val > 0:
        chord_wave = chord_wave * (32767 / max_val)
    else:
        chord_wave = chord_wave * 0

    chord_wave = chord_wave.astype(np.int16)
    sound = pygame.sndarray.make_sound(chord_wave)
    channel = sound.play()
    if playing_channels is not None:
        playing_channels.append(channel)

# Frequencies for standard musical notes
note_frequencies = {
    'C': 261.63,
    'C#': 277.18,
    'D': 293.66,
    'D#': 311.13,
    'E': 329.63,
    'F': 349.23,
    'F#': 369.99,
    'G': 392.00,
    'G#': 415.30,
    'A': 440.00,
    'A#': 466.16,
    'B': 493.88,
}

# Chord definitions (Chord Name: List of Notes)
chord_definitions = {
    'C Major': ['C', 'E', 'G'],
    'D Major': ['D', 'F#', 'A'],
    'E Major': ['E', 'G#', 'B'],
    'F Major': ['F', 'A', 'C'],
    'G Major': ['G', 'B', 'D'],
    'A Minor': ['A', 'C', 'E'],
    'B Diminished': ['B', 'D', 'F'],
    # Add more chords as needed
}

# Map keys to chord names
key_to_chord = {
    'C': 'C Major',
    'D': 'D Major',
    'E': 'E Major',
    'F': 'F Major',
    'G': 'G Major',
    'A': 'A Minor',
    'B': 'B Diminished',
    # Add more mappings as needed
}

class ChordApp:
    def __init__(self, master):
        self.master = master
        master.title("Chord Player with Strumming and Effects")

        # Bind key press event to the main window
        master.bind('<Key>', self.key_pressed)

        # Strum delay variable
        self.strum_delay = tk.DoubleVar(value=0.1)  # Default strum delay in seconds
        # Note duration variable
        self.note_duration = tk.DoubleVar(value=2.0)  # Default note duration in seconds
        # Waveform variable
        self.waveform = tk.StringVar(value='sine')
        # Octave shift variable
        self.octave_shift = tk.IntVar(value=0)  # 0 for no shift
        # Effect variable
        self.effect = tk.StringVar(value='None')

        # Variables to manage chord playing
        self.current_strum_thread = None
        self.stop_strum_event = threading.Event()
        self.playing_channels = []

        # Create buttons for each chord
        for i, (key, chord_name) in enumerate(key_to_chord.items()):
            btn = tk.Button(master, text=chord_name, width=15, height=2,
                            command=lambda cn=chord_name: self.play_chord(cn))
            btn.grid(row=0, column=i, padx=5, pady=5)

        # Strum speed control
        strum_label = tk.Label(master, text="Strum Speed (Delay in seconds):")
        strum_label.grid(row=1, column=0, columnspan=2)

        strum_scale = tk.Scale(master, from_=0.02, to=0.2, resolution=0.01,
                               orient=tk.HORIZONTAL, variable=self.strum_delay)
        strum_scale.grid(row=1, column=2, columnspan=2)

        # Note duration control
        duration_label = tk.Label(master, text="Note Duration (seconds):")
        duration_label.grid(row=2, column=0, columnspan=2)

        duration_scale = tk.Scale(master, from_=1.0, to=5.0, resolution=0.5,
                                  orient=tk.HORIZONTAL, variable=self.note_duration)
        duration_scale.grid(row=2, column=2, columnspan=2)

        # Waveform selection
        waveform_label = tk.Label(master, text="Waveform:")
        waveform_label.grid(row=3, column=0)
        waveform_menu = tk.OptionMenu(master, self.waveform, 'sine', 'square', 'sawtooth', 'triangle')
        waveform_menu.grid(row=3, column=1)

        # Octave shift control
        octave_label = tk.Label(master, text="Octave Shift:")
        octave_label.grid(row=3, column=2)
        octave_scale = tk.Scale(master, from_=-2, to=2, resolution=1,
                                orient=tk.HORIZONTAL, variable=self.octave_shift)
        octave_scale.grid(row=3, column=3)

        # Effect selection
        effect_label = tk.Label(master, text="Effect:")
        effect_label.grid(row=4, column=0)
        effect_menu = tk.OptionMenu(master, self.effect, 'None', 'Echo', 'Reverb')
        effect_menu.grid(row=4, column=1)

        # Create quit button
        quit_btn = tk.Button(master, text="Quit", width=10, height=2,
                             command=master.quit)
        quit_btn.grid(row=5, column=len(key_to_chord)//2, pady=10)

    def play_chord(self, chord_name):
        note_names = chord_definitions.get(chord_name)
        if note_names:
            # Stop previous chord if any
            if self.current_strum_thread and self.current_strum_thread.is_alive():
                self.stop_strum_event.set()
                self.current_strum_thread.join()
                # Stop all playing channels
                for channel in self.playing_channels:
                    channel.stop()
                self.playing_channels.clear()
                self.stop_strum_event.clear()
            strum_delay = self.strum_delay.get()
            note_duration = self.note_duration.get()
            waveform = self.waveform.get()
            effect = self.effect.get()
            # Start new chord
            self.current_strum_thread = threading.Thread(
                target=strum_chord,
                args=(note_names,),
                kwargs={
                    'duration': note_duration,
                    'volume': 1.0,
                    'strum_delay': strum_delay,
                    'waveform': waveform,
                    'effect': effect,
                    'stop_event': self.stop_strum_event,
                    'playing_channels': self.playing_channels
                }
            )
            self.current_strum_thread.start()
        else:
            messagebox.showerror("Error", f"Chord '{chord_name}' not found.")

    def key_pressed(self, event):
        key = event.char.upper()
        chord_name = key_to_chord.get(key)
        if chord_name:
            self.play_chord(chord_name)
        else:
            pass  # Ignore unassigned keys

if __name__ == "__main__":
    root = tk.Tk()
    app = ChordApp(root)
    root.mainloop()
