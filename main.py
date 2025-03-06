import sys
import os
import datetime
import pyttsx3
import requests
import speech_recognition as sr
import openai
import subprocess
import difflib
import webbrowser
import time
import pyautogui
import psutil
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

API_KEY = ""

OPENAI_API_KEY = ""
openai.api_key = OPENAI_API_KEY


# Initialize Text-to-Speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 170)  # Adjust speed
engine.setProperty("volume", 1.0)  # Set volume

class Goose(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")  # Apply dark theme
        self.title("Goose AI Assistant")
        self.geometry("700x500")
        self.chat_history = ""
        self.init_ui()
        
        # Search handling keywords
        self.youtube_aliases = ["youtube", "you tube", "yt", "utube"]
        self.google_aliases = ["google", "gogle", "googl", "search"]

    def init_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=BOTH, expand=True)

        self.label = ttk.Label(frame, text="Welcome to Goose", font=("Helvetica", 16, "bold"))
        self.label.pack(pady=10)

        self.text_display = ttk.Text(frame, height=12, width=65, wrap="word", state=NORMAL, background="#222", foreground="#fff")
        self.text_display.pack(pady=10)

        self.text_input = ttk.Entry(frame, width=50, bootstyle="dark")
        self.text_input.pack(pady=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)

        self.send_button = ttk.Button(btn_frame, text="Send", bootstyle="info", command=self.handle_query)
        self.send_button.pack(side=LEFT, padx=5)

        self.voice_button = ttk.Button(btn_frame, text="🎙️ Voice Command", bootstyle="success", command=self.take_command)
        self.voice_button.pack(side=LEFT, padx=5)

    def say(self, text):
        engine.say(text)
        engine.runAndWait()

    def handle_query(self):
        query = self.text_input.get().lower()
        if query:
            self.process_query(query)
            self.text_input.delete(0, END)

    def process_query(self, query):
        self.chat_history += f"User: {query}\nGoose: "

        if query in ["talk to me rooster", "talk to me goose"]:
            response_text = "Feeling the need... the need for speed!"
            self.display_response(response_text)
            return

        if query.startswith("open "):
            app_name = query.replace("open", "").strip()
            self.open_application(app_name)

        elif query.startswith("search "):
            search_query = query.replace("search", "").strip()
            self.search(search_query)

        elif "time" in query:
            time_now = datetime.datetime.now().strftime("%H:%M")
            self.display_response(f"The time is {time_now}.")

        elif query.startswith("play "):
            self.play_music(query)
            return
        
        elif "weather in" in query:
            city = query.split("weather in")[-1].strip()
            if city:
                self.get_weather(city)
            else:
                self.display_response("Please specify a city name.")

        else:
            self.ask_openai(query)

    def ask_openai(self, query):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": self.chat_history},
                ],
                temperature=0.7,
                max_tokens=256,
            )
            reply = response["choices"][0]["message"]["content"]
            self.chat_history += f"{reply}\n"
            self.display_response(reply)
        except Exception:
            self.display_response("I didn't understand that.")

    def take_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            self.display_response("Listening...")
            try:
                audio = r.listen(source, timeout=5)
                query = r.recognize_google(audio, language="en-in").lower()
                self.display_response(f"User said: {query}")
                self.process_query(query)
            except sr.UnknownValueError:
                self.display_response("Sorry, I couldn't understand that.")
            except sr.RequestError:
                self.display_response("Network error. Please check your connection.")

    def open_application(self, app_name):
        common_apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "wordpad": "write.exe",
            "paint": "mspaint.exe",
            "task manager": "taskmgr.exe",
            "command prompt": "cmd.exe",
            "file explorer": "explorer.exe",
            "powershell": "powershell.exe",
        }

        if app_name in common_apps:
            subprocess.Popen(common_apps[app_name], shell=True)
            self.display_response(f"Opening {app_name}...")
            return

        self.display_response(f"No matching application found for '{app_name}'")

    def search(self, query):
        platform = "google"
        search_query = query.strip().lower()

        for word in search_query.split():
            if difflib.get_close_matches(word, self.youtube_aliases, cutoff=0.7):
                platform = "youtube"
                search_query = search_query.replace(word, "").strip()
                break

        search_url = (f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
                      if platform == "youtube" else
                      f"https://www.google.com/search?q={search_query}")
        webbrowser.open(search_url)
        self.display_response(f"Searching on {platform.capitalize()}: {search_query}")
    
    def is_spotify_running(self):
        return any("spotify.exe" in process.info['name'].lower() for process in psutil.process_iter(['name']) if process.info['name'])

    def play_music(self, command):
        song_name = command[5:].strip()
        self.display_response(f"Searching for '{song_name}' on Spotify...")

        spotify_path = os.path.join(os.getenv("APPDATA"), "Spotify", "Spotify.exe")
        if not os.path.exists(spotify_path):
            self.display_response("Spotify not found!")
            return

        if not self.is_spotify_running():
            subprocess.Popen(spotify_path, shell=True)
            time.sleep(8)

        pyautogui.hotkey("win", "d")
        time.sleep(1)
        pyautogui.hotkey("ctrl", "l")
        time.sleep(2)
        pyautogui.typewrite(song_name, interval=0.1)
        time.sleep(2)
        pyautogui.press("enter")
        time.sleep(4)
        pyautogui.press("enter")
        self.display_response(f"Playing '{song_name}' on Spotify...")

    def display_response(self, text):
        self.text_display.config(state=NORMAL)
        self.text_display.insert(END, f"Goose: {text}\n")
        self.text_display.config(state=DISABLED)
        self.say(text)
    
    def get_weather(self, city):
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        try:
            response = requests.get(url)
            data = response.json()
            if data["cod"] == 200:
                temp = data["main"]["temp"]
                description = data["weather"][0]["description"]
                self.display_response(f"The weather in {city} is {description} with a temperature of {temp}°C.")
            else:
                self.display_response("Could not retrieve weather data. Please check the city name.")
        except Exception:
            self.display_response("Error fetching weather information.")

if __name__ == "__main__":
    app = Goose()
    app.mainloop()
