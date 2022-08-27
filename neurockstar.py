import datetime

import os
import pyttsx3
import speech_recognition
import wikipedia

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from bandcamp import BandcampController
from chrome import ChromeController
from openweather import OpenweatherController

load_dotenv()

# chromedriver_path = './resources/chromedriver_win32/chromedriver.exe'
chrome_path = os.getenv('chrome_path')
chrome_options = Options()
chrome_options.headless = False
# browser = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
browser = webdriver.Chrome()

bandcamp_controller = BandcampController(browser=browser)
chrome_controller = ChromeController(browser=browser)
openweather_controller = OpenweatherController()

speech_engine = pyttsx3.init('sapi5')  # Sapi5 is MS text-2-speech voice recognition engine
# voices = speech_engine.getProperty('voices')
# speech_engine.setProperty('voice', 'voices[0].id')


def speak(text):
    speech_engine.say(text)
    speech_engine.runAndWait()  # blocking function until processing of all currently queued commands using


def greet_user():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak('Hello, Good Morning')
        print('Hello, Good Morning')
    elif 12 <= hour < 18:
        speak('Hello, Good Afternoon')
        print('Hello, Good Afternoon')
    else:
        speak('Hello, Good Evening')
        print('Hello, Good Evening')


def receive_command():
    speech_detector = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:
        print('Listening...')
        audio = speech_detector.listen(source)
        try:
            command_statement = speech_detector.recognize_google(audio, language='en-us')
            print(f'user said:{command_statement}')
            return command_statement
        except Exception as e:
            print(f'exception: {e}')
            return "None"


print('neurockstar Initiating')
speak('neurockstar Initiating')
greet_user()

if __name__ == '__main__':

    while True:
        statement = receive_command().lower()
        bandcamp_response = bandcamp_controller.check_statement(statement)
        openweather_response = openweather_controller.dispatch(statement)
        chrome_controller_response = chrome_controller.dispatch(statement)

        if statement == 0:
            continue

        elif "Neurock off" in statement:
            speak('neurock signing off')
            print('Goodbye Again, From neurock.')
            break

        elif 'wikipedia' in statement:
            speak('Searching Wikipedia...')
            statement = statement.replace('wikipedia', '')
            results = wikipedia.summary(statement, sentences=3)
            speak('According to Wikipedia')
            print(results)
            speak(results)

        elif bandcamp_response:
            print(f'BANDCAMP RESPONSE: {bandcamp_response}')
            speak(bandcamp_response)
            break

        elif openweather_response:
            print(f'OPENWEATHER RESPONSE = {openweather_response}')
            speak(openweather_response)
            break

        elif chrome_controller_response:
            print(f'CHROME CONTROLLER RESPONSE = {chrome_controller_response}')
            speak(chrome_controller_response)
            break

