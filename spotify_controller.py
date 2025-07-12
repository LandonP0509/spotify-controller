import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    redirect_uri='http://localhost:8888/callback',
    scope='user-read-playback-state user-modify-playback-state'
))

def get_current_track():
    track = sp.current_playback()
    if not track: return None
    return {
        "title": track["item"]["name"],
        "artist": ", ".join([a["name"] for a in track["item"]["artists"]]),
        "album_url": track["item"]["album"]["images"][0]["url"],
        "is_playing": track["is_playing"]
    }

def refresh_display():
    track = get_current_track()
    if track:
        title_var.set(track["title"])
        artist_var.set(track["artist"])
        play_button.config(text="Pause" if track["is_playing"] else "Play")

        response = requests.get(track["album_url"])
        img_data = Image.open(BytesIO(response.content)).resize((200, 200))
        img = ImageTk.PhotoImage(img_data)
        album_label.config(image=img)
        album_label.image = img
    root.after(5000, refresh_display)

def toggle_play():
    current = sp.current_playback()
    if current["is_playing"]:
        sp.pause_playback()
    else:
        sp.start_playback()
    refresh_display()

def skip():
    sp.next_track()
    refresh_display()

root = tk.Tk()
root.title("Spotify Controller")

title_var = tk.StringVar()
artist_var = tk.StringVar()

tk.Label(root, textvariable=title_var, font=("Helvetica", 16)).pack(pady=5)
tk.Label(root, textvariable=artist_var, font=("Helvetica", 12)).pack(pady=5)
album_label = tk.Label(root)
album_label.pack(pady=5)

play_button = tk.Button(root, text="Play", command=toggle_play, width=10)
play_button.pack(side="left", padx=10, pady=10)

skip_button = tk.Button(root, text="Skip", command=skip, width=10)
skip_button.pack(side="right", padx=10, pady=10)

refresh_display()
root.mainloop()

