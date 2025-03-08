import speech_recognition as sr 
import pyaudio
import pywhatkit

def get_audio():
    recorder = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say Something...")
        audio = recorder.listen(source, timeout = 20)
        
    text = recorder.recognize_google(audio)
    print(f"You said: {text}")
    return text

text = get_audio()

if "youtube" in text.lower():
    pywhatkit.playonyt(text)
else:
    pywhatkit.search(text)
