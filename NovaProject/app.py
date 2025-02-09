from flask import Flask, render_template, jsonify, request
import os
import time
import datetime
import webbrowser
import pyautogui
import requests
import win32com.client
import speech_recognition as sr
import pythoncom
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logging.error("GEMINI_API_KEY is not set. Please add it to your .env file.")
    raise ValueError("GEMINI_API_KEY is not set. Please add it to your .env file.")

app = Flask(__name__)

# Global variable to store the active SAPI voice object.
global_voice = None

def query_gemini(prompt):
    """
    Query the Gemini API using the provided prompt.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except requests.RequestException as e:
        logging.error("Error querying Gemini API: %s", e)
        return "Error: Unable to contact Gemini API."
    except (KeyError, IndexError) as e:
        logging.error("Unexpected response format: %s", e)
        return "Error: Unexpected response format from Gemini API."

def speak(text):
    """
    Use the Windows SAPI to speak the given text asynchronously using a female voice.
    
    This function searches through the available voices and selects one that contains
    'zira' in its description (typically a female voice) before speaking.
    
    Args:
        text (str): The text to speak.
    """
    global global_voice
    pythoncom.CoInitialize()
    try:
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        # Force selection of a female voice (e.g., Microsoft Zira)
        for voice in speaker.GetVoices():
            if "zira" in voice.GetDescription().lower():
                speaker.Voice = voice
                break
        global_voice = speaker
        speaker.Speak(text, 1)
    except Exception as e:
        logging.error("Error in speak function: %s", e)
    # Do not uninitialize COM immediately since speech is asynchronous.

# (Rest of your code continues as before...)
5

def stop_speech():
    """
    Attempt to stop any ongoing speech by skipping remaining sentences.

    Returns:
        str: A message indicating whether speech was stopped.
    """
    global global_voice
    try:
        if global_voice:
            # Skip all remaining sentences.
            global_voice.Skip("SENTENCE", 1000)
            return "Speech stopped."
        else:
            return "No speech in progress."
    except Exception as e:
        logging.error("Error stopping speech: %s", e)
        return f"Error: {e}"

def take_command():
    """
    Listen for a voice command using the microphone.

    Returns:
        str: The recognized command as text, or "None" if recognition fails.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        logging.info("Listening for voice command...")
        r.pause_threshold = 0.8
        r.energy_threshold = 300
        try:
            audio = r.listen(source, timeout=5)
        except sr.WaitTimeoutError:
            logging.warning("Listening timed out.")
            return "None"
    try:
        logging.info("Recognizing voice command...")
        query = r.recognize_google(audio, language="en-in")
        logging.info("User said: %s", query)
        return query
    except sr.UnknownValueError:
        logging.warning("Could not understand audio.")
        return "None"
    except sr.RequestError as e:
        logging.error("Speech recognition error: %s", e)
        return "None"

def process_command(command):
    """
    Process a voice or manual command.

    Depending on the command text, perform an action such as opening a website,
    searching online, playing music, or using the Gemini API.

    Args:
        command (str): The command text.

    Returns:
        str: A response message after processing the command.
    """
    command_lower = command.lower().strip()
    response_text = ""

    # Special case: Introduction command.
    if command_lower in ["who are you", "what is your name", "who r u"]:
        response_text = "I am Nova, your personal assistant created by Govind Khedkar."
        speak(response_text)
        return response_text

    if command_lower in ["exit", "exits"]:
        speak("Goodbye!")
        response_text = "Goodbye! Exiting now..."
    elif command_lower and command_lower != "none":
        if "open" in command_lower:
            if "desktop" in command_lower:
                # Extract the application name for desktop command.
                app_name = command_lower.split("desktop", 1)[1].strip()
                try:
                    speak(f"Searching for {app_name} in the Start Menu...")
                    pyautogui.press("win")
                    time.sleep(1)
                    pyautogui.write(app_name)
                    time.sleep(1)
                    pyautogui.press("enter")
                    speak(f"Opening {app_name}...")
                    response_text = f"Opening {app_name} on your desktop..."
                except Exception as e:
                    logging.error("Error opening desktop app: %s", e)
                    speak(f"Sorry, I couldn't open {app_name}.")
                    response_text = f"Error: {e}"
            else:
                # Extract the website name for a website-opening command.
                website = command_lower.split("open", 1)[1].strip().replace(" ", "")
                speak(f"Opening {website}...")
                webbrowser.open(f"https://www.{website}.com")
                response_text = f"Opening website: {website}"
        elif "search" in command_lower:
            # Handle search commands.
            search_query = command_lower.split("search", 1)[1].strip()
            if search_query:
                speak(f"Searching for {search_query} on Google...")
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
                response_text = f"Searching for: {search_query}"
        elif "play music" in command_lower:
            try:
                # Handle commands to play music.
                music_name = command_lower.split("play music", 1)[1].strip()
                speak(f"Searching for {music_name} on YouTube...")
                query_str = music_name.replace(" ", "+")
                webbrowser.open(f"https://www.youtube.com/results?search_query={query_str}")
                speak(f"Playing music: {music_name} on YouTube...")
                response_text = f"Playing music: {music_name}"
            except Exception as e:
                logging.error("Error playing music: %s", e)
                speak("An error occurred while trying to play the music.")
                response_text = f"Error: {e}"
        elif "the time" in command_lower:
            # Provide the current time.
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The time is {current_time}")
            response_text = f"The time is {current_time}"
        else:
            # For unrecognized commands, use the Gemini API.
            gemini_response = query_gemini(command)
            speak(gemini_response)
            response_text = gemini_response
    else:
        speak("I didn't catch that. Please try again.")
        response_text = "No valid command recognized."

    return response_text

# ---------------- Flask Routes ----------------
@app.route('/')
def index():
    """
    Render the main interface.
    """
    return render_template("base.html")

@app.route('/listen', methods=["POST"])
def listen():
    """
    Endpoint to process voice commands.

    Returns:
        JSON: Contains the recognized command and the response.
    """
    command = take_command()
    result = process_command(command)
    return jsonify({"result": result, "command": command})

@app.route('/command', methods=["POST"])
def command():
    """
    Endpoint to process manual commands.

    Returns:
        JSON: Contains the command text and the response.
    """
    data = request.get_json()
    command_text = data.get("command", "")
    result = process_command(command_text)
    return jsonify({"result": result, "command": command_text})

@app.route('/stop_speech', methods=["POST"])
def stop_speech_route():
    """
    Endpoint to stop ongoing speech.

    Returns:
        JSON: Contains a message indicating whether speech was stopped.
    """
    result = stop_speech()
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=True)
