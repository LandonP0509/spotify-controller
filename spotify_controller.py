import os
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from io import BytesIO

# Spotify Auth Setup
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://127.0.0.1:8888/callback'

auth_manager = SpotifyOAuth(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUUR_CLIENT_SECRET',
    redirect_uri='http://127.0.0.1:8888/callback',
    scope='user-read-playback-state user-modify-playback-state',
    open_browser=False
)

sp = spotipy.Spotify(auth_manager=auth_manager)

# GUI Setup
root = tk.Tk()
root.title("Spotify Controller")
root.attributes('-fullscreen', True)
root.geometry("800x480")  # 5-inch screen resolution
root.configure(bg='black')
root.config(cursor="none")  # Hide the cursor

album_label = tk.Label(root, bg='black')
album_label.pack(pady=10)

info_frame = tk.Frame(root, bg='black')
info_frame.pack()

title_var = tk.StringVar()
artist_var = tk.StringVar()

title_label = tk.Label(info_frame, textvariable=title_var,
                       font=("Helvetica", 18, "bold"), fg='white', bg='black', wraplength=700)
title_label.pack()

artist_label = tk.Label(info_frame, textvariable=artist_var,
                        font=("Helvetica", 14), fg='gray', bg='black', wraplength=700)
artist_label.pack()

button_frame = tk.Frame(root, bg='black')
button_frame.pack(pady=20)

# Load button images
play_img = ImageTk.PhotoImage(Image.open("assets/icons8-play-60.png").resize((64, 64)))
pause_img = ImageTk.PhotoImage(Image.open("assets/icons8-pause-60.png").resize((64, 64)))
skip_img = ImageTk.PhotoImage(Image.open("assets/icons8-forward-60.png").resize((64, 64)))
prev_img = ImageTk.PhotoImage(Image.open("assets/icons8-back-60.png").resize((64, 64)))

# Control functions
def toggle_play():
    try:
        playback = sp.current_playback()
        if playback and playback["is_playing"]:
            sp.pause_playback()
        else:
            sp.start_playback()
    except Exception as e:
        print("Error toggling play/pause:", e)

def skip_forward():
    try:
        sp.next_track()
    except Exception as e:
        print("Error skipping forward:", e)

def skip_back():
    try:
        sp.previous_track()
    except Exception as e:
        print("Error skipping backward:", e)

# Labels as buttons (no cursor style)
skip_back_label = tk.Label(button_frame, image=prev_img, bg='black')
play_label = tk.Label(button_frame, image=play_img, bg='black')
skip_forward_label = tk.Label(button_frame, image=skip_img, bg='black')

skip_back_label.bind("<Button-1>", lambda e: [skip_back(), refresh_display(force=True)])
play_label.bind("<Button-1>", lambda e: [toggle_play(), refresh_display(force=True)])
skip_forward_label.bind("<Button-1>", lambda e: [skip_forward(), refresh_display(force=True)])

skip_back_label.pack(side='left', padx=20)
play_label.pack(side='left', padx=40)
skip_forward_label.pack(side='left', padx=20)

def get_play_symbol(is_playing):
    return pause_img if is_playing else play_img

def get_current_track():
    try:
        track = sp.current_playback()
        if not track or not track["item"]:
            return None
        return {
            "title": track["item"]["name"],
            "artist": ", ".join([a["name"] for a in track["item"]["artists"]]),
            "album_url": track["item"]["album"]["images"][0]["url"],
            "is_playing": track["is_playing"]
        }
    except Exception as e:
        print("Error fetching current track:", e)
        return None

def make_rounded_image(image, size, radius=50):
    image = image.resize(size, Image.LANCZOS)
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    rounded = Image.new('RGBA', size)
    rounded.paste(image, (0, 0), mask=mask)
    return rounded.convert('RGB')

last_album_url = None

def refresh_display(force=False):
    global last_album_url, play_label
    track = get_current_track()
    if track:
        title_var.set(track["title"])
        artist_var.set(track["artist"])
        play_label.config(image=get_play_symbol(track["is_playing"]))
        if force or track["album_url"] != last_album_url:
            last_album_url = track["album_url"]
            try:
                response = requests.get(track["album_url"])
                img_data = Image.open(BytesIO(response.content))
                rounded = make_rounded_image(img_data, (300, 300), radius=30)
                img = ImageTk.PhotoImage(rounded)
                album_label.config(image=img)
                album_label.image = img
            except Exception as e:
                print("Error loading album art:", e)
                album_label.config(image=None)
                album_label.image = None
    else:
        title_var.set("Nothing Playing")
        artist_var.set("")
        play_label.config(image=play_img)
        album_label.config(image=None)
        album_label.image = None
        last_album_url = None

    root.after(3000, refresh_display)

# Initial display
refresh_display()
root.mainloop()
