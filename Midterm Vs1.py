import pygame
import os
import tkinter as tk
from tkinter import messagebox

# Initialize pygame mixer
pygame.mixer.init()

# Define the path to your sound files
# Replace this with the actual path to your sound files
SOUND_DIR = "/Users/musarahim/Desktop/CMPS 1100/SoundFiles"

# Define note sound files
notes = {
    'A': 'a_major.wav',
    'C': 'c_major.wav',
    'D': 'd_major.wav',
    'E': 'e_major.wav',
    'G': 'g_major.wav',
}

def play_note(note):
    try:
        sound_file = os.path.join(SOUND_DIR, notes[note])
        if not os.path.exists(sound_file):
            messagebox.showerror("Error", f"Sound file '{sound_file}' not found.")
            return
        sound = pygame.mixer.Sound(sound_file)
        sound.play()
    except pygame.error as e:
        messagebox.showerror("Error", f"Error playing sound: {e}")

        # Function to bind keys to specific notes
def key_pressed(event):
    key = event.char.upper()  # Convert key to uppercase to match notes
    if key in notes:
        play_note(key)

class GuitarApp:
    def __init__(self, master):
        self.master = master
        master.title("Guitar Chord Player")

        # Create buttons for each note
        for i, (note, _) in enumerate(notes.items()):
            btn = tk.Button(master, text=note, width=10, height=2,
                            command=lambda n=note: play_note(n))
            btn.grid(row=0, column=i, padx=5, pady=5)

        # Create quit button
        quit_btn = tk.Button(master, text="Quit", width=10, height=2,
                             command=master.quit)
        quit_btn.grid(row=1, column=len(notes)//2, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = GuitarApp(root)
    root.mainloop()