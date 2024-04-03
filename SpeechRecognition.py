import speech_recognition as sr
import pyautogui

def listen_for_command(timeout_duration=2, phrase_limit=5):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak (listening for 'START' to activate):")
        # Wait for up to timeout_duration seconds for the user to start speaking
        # Listen to the user for up to phrase_limit seconds
        audio = r.listen(source, timeout=timeout_duration, phrase_time_limit=phrase_limit)
        
    try:
        if "jarvis" in r.recognize_google(audio).lower():
            print("'jarvis' keyword detected. Now listening for your command:")
            with sr.Microphone() as source:
                # Again, wait for up to timeout_duration seconds for the user to start speaking
                # Listen to the user for up to phrase_limit seconds for their command
                audio = r.listen(source, timeout=timeout_duration, phrase_time_limit=phrase_limit)
            text = r.recognize_google(audio)
            print("You said: " + text)
            pyautogui.typewrite(text)
            return text
        else:
            print("Keyword 'START' not detected.")
            return None
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    return None

text = listen_for_command()
