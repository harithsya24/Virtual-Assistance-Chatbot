import speech_recognition as sr
import pywhatkit
import smtplib
import re
import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API setup
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    """Authenticates Gmail API and returns a service object."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_audio():
    """Captures voice input and converts it to text."""
    recorder = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say Something...")
        try:
            audio = recorder.listen(source, timeout=20)
            text = recorder.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand.")
            return None
        except sr.RequestError:
            print("Could not request results, check your internet.")
            return None

def send_email(subject, message, to_email):
    """Sends an email using Gmail API."""
    service = authenticate_gmail()
    message_obj = MIMEText(message)
    message_obj['to'] = to_email
    message_obj['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message_obj.as_bytes()).decode()
    
    service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
    print(f"Email sent to {to_email}")

def search_emails(query):
    """Searches emails using Gmail API."""
    service = authenticate_gmail()
    results = service.users().messages().list(userId="me", q=query).execute()
    messages = results.get('messages', [])
    if not messages:
        print("No emails found for the search query.")
    else:
        print(f"Found {len(messages)} email(s) related to '{query}'.")

def process_command(text):
    """Processes the spoken text and performs actions accordingly."""
    if text is None:
        return
    
    # Check for YouTube search
    if "youtube" in text:
        pywhatkit.playonyt(text)
    
    # Check for Google search
    elif "search" in text or "google" in text:
        pywhatkit.search(text)

    # Check for email sending
    elif "send email to" in text:
        match = re.search(r"send email to (.+?) saying (.+)", text)
        if match:
            recipient = match.group(1).strip()
            message = match.group(2).strip()
            send_email(subject="Voice Command Email", message=message, to_email=f"{recipient}@gmail.com")
        else:
            print("Could not understand the email command.")

    # Check for email search
    elif "search emails for" in text:
        query = text.replace("search emails for", "").strip()
        search_emails(query)

# Run the voice assistant
if __name__ == "__main__":
    spoken_text = get_audio()
    process_command(spoken_text)
