# NOVA Assistant

**NOVA Assistant** is a Flask-based virtual assistant web application that allows users to control their computer using both voice and text commands. The app provides functionality such as opening websites, performing searches, playing music, and more. It integrates with external APIs (like Gemini) for advanced responses and includes text-to-speech output using Windows SAPI with a preferred female voice.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Features

- **Voice Command Recognition:** Uses the `speech_recognition` library to capture and transcribe voice commands.
- **Manual Command Processing:** Allows users to type commands via an input field. When the command starts with "search," suggestions appear and you can autocomplete with the Tab key.
- **Text-to-Speech Output:** Utilizes Windows SAPI (via `pywin32`) to speak responses. The function is configured to force the use of a female voice (Microsoft Zira) if available.
- **Stop Speech Functionality:** Provides a button to interrupt ongoing speech.
- **External API Integration:** Uses the Gemini API for advanced response generation for unrecognized commands.
- **Search Suggestions & Autocomplete:** Offers Google-like suggestions for search queries.
- **Result Controls:** Allows users to copy the response text to the clipboard or clear the result.
- **Easy Deployment:** Clear folder structure and minimal configuration make deployment (e.g., on PythonAnywhere) straightforward.

---

## Project Structure

The repository is organized as follows:

NovaProject/
├── app.py               # Main Flask application.
├── requirements.txt     # Required Python libraries.
├── .env                 # Environment variables (e.g., GEMINI_API_KEY). (Keep this file secure!)
├── .gitignore           # Files/directories to ignore (e.g., __pycache__, venv, app.log, .env).
├── README.md            # This file.
├── templates/           # Contains HTML templates.
│   └── base.html
└── static/              # Contains static assets.
    ├── css/
    │   └── styles.css
    └── js/
        └── script.js

---

## Installation

### 1. Clone the Repository

Open your terminal or Command Prompt and run:

    git clone https://github.com/GovindTechie/nova-assistant.git
    cd nova-assistant

### 2. Create a Virtual Environment (Recommended)

- On Linux/macOS:

    python3 -m venv venv
    source venv/bin/activate

- On Windows:

    python -m venv venv
    venv\Scripts\activate

### 3. Install Dependencies

With your virtual environment activated, run:

    pip install -r requirements.txt

*Make sure your requirements.txt file is clean and does not contain any local file paths.*

---

## Configuration

### Environment Variables

The app requires environment variables (like GEMINI_API_KEY). You can set these in one of two ways:

1. **Using a `.env` File:**  
   Create a file named `.env` in your project root and add:

       GEMINI_API_KEY=your_actual_gemini_api_key_here

   The project uses `python-dotenv` to automatically load these variables.

2. **Manually on Deployment Platforms:**  
   When deploying (for example, on PythonAnywhere), set the environment variables via the platform’s dashboard.

### .gitignore

Ensure you have a `.gitignore` file to avoid uploading unnecessary or sensitive files. Example content:

       __pycache__/
       venv/
       *.log
       app.log
       .env

---

## Usage

### Running the Application Locally

After installing dependencies, start your Flask app by running:

    python app.py

or, if using the Flask CLI:

    flask run

Then, open your browser and navigate to http://127.0.0.1:5000 to interact with NOVA Assistant.

### How to Use NOVA Assistant

- **Voice Commands:**  
  Click the microphone button to speak your command.
- **Manual Commands:**  
  Type your command into the input field. If your command starts with "search," suggestions will appear; press the Tab key to autocomplete with the first suggestion.
- **Stop Speech:**  
  If NOVA is speaking, click the Stop Speech button to interrupt the text-to-speech output.
- **Result Controls:**  
  Use the copy button to copy the response or the clear button to remove it.

---

## Deployment

### Deploying on PythonAnywhere

1. **Sign Up:**  
   Create a free account at https://www.pythonanywhere.com.
2. **Upload Your Project:**  
   Clone your GitHub repository or manually upload the entire NovaProject folder.
3. **Set Up a Virtual Environment:**  
   Create and activate a virtual environment on PythonAnywhere, then run:

       pip install -r requirements.txt

4. **Configure Your Web App:**  
   In PythonAnywhere’s Web tab, set up a new web app with manual configuration, select your Python version, and update the WSGI file to point to your project directory and import your Flask app. For example, your WSGI file might include:

       import sys
       import os

       project_home = '/home/yourusername/NovaProject'
       if project_home not in sys.path:
           sys.path.insert(0, project_home)

       activate_this = '/home/yourusername/venv/bin/activate_this.py'
       with open(activate_this) as file_:
           exec(file_.read(), dict(__file__=activate_this))

       from app import app as application

5. **Set Environment Variables:**  
   Either upload your `.env` file (if kept private) or set variables in the PythonAnywhere dashboard.
6. **Reload Your Web App:**  
   Click the Reload button and visit your PythonAnywhere URL (e.g., https://yourusername.pythonanywhere.com).

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your changes.
3. Commit your changes with a clear message.
4. Open a pull request describing your modifications.
5. Follow the coding style and include tests if applicable.

---

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

---

## Acknowledgements

- Thanks to the open-source community for the libraries and tools that power NOVA Assistant.
- Special thanks to the developers and maintainers of Flask, pywin32, SpeechRecognition, and other packages used in this project.

---

*If you have any questions or need further assistance, please open an issue in this repository or contact me directly.*
