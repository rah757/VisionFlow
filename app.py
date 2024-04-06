from multiprocessing import Process
import speech_recognition as sr
import cv2
from imutils import face_utils
from utils import *
import numpy as np
import pyautogui as pyag
import imutils
import dlib
import pyttsx3
engine = pyttsx3.init()         # tts engine setup
import os
import webbrowser


MOUTH_AR_THRESH = 0.6
MOUTH_AR_CONSECUTIVE_FRAMES = 15  
EYE_AR_THRESH = 0.19        #0.19
EYE_AR_CONSECUTIVE_FRAMES = 20      #15
WINK_AR_DIFF_THRESH = 0.03
WINK_AR_CLOSE_THRESH = 0.23    #0.19
WINK_CONSECUTIVE_FRAMES = 3    #10

MOUTH_COUNTER = 0
EYE_COUNTER = 0
WINK_COUNTER = 0
INPUT_MODE = False
EYE_CLICK = False
LEFT_WINK = False
RIGHT_WINK = False
SCROLL_MODE = False
ANCHOR_POINT = (0, 0)
YELLOW_COLOR = (0, 255, 255)
RED_COLOR = (0, 0, 255)
GREEN_COLOR = (0, 255, 0)
BLUE_COLOR = (255, 0, 0)
BLACK_COLOR = (0, 0, 0)


def main_loop():
    global MOUTH_COUNTER, EYE_COUNTER, WINK_COUNTER, INPUT_MODE, EYE_CLICK, LEFT_WINK, RIGHT_WINK, SCROLL_MODE, ANCHOR_POINT, SCROLL_MODE_ANNOUNCED
    shape_predictor = "model/shape_predictor_68_face_landmarks.dat"
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(shape_predictor)


    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
    (nStart, nEnd) = face_utils.FACIAL_LANDMARKS_IDXS["nose"]
    (mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

    # Video capture
    vid = cv2.VideoCapture(0)
    resolution_w = 1366
    resolution_h = 768
    cam_w = 640
    cam_h = 480
    unit_w = resolution_w / cam_w
    unit_h = resolution_h / cam_h

    while True:
        _, frame = vid.read()
        frame = cv2.flip(frame, 1)
        frame = imutils.resize(frame, width=cam_w, height=cam_h)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


        rects = detector(gray, 0)

        # Loop over the face detections
        if len(rects) > 0:
            rect = rects[0]
        else:
            cv2.imshow("VisionFlow", frame)
            key = cv2.waitKey(1) & 0xFF
            continue


        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)


        mouth = shape[mStart:mEnd]
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        nose = shape[nStart:nEnd]

        temp = leftEye
        leftEye = rightEye
        rightEye = temp

        mar = mouth_aspect_ratio(mouth)
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        ear = (leftEAR + rightEAR) / 2.0
        diff_ear = np.abs(leftEAR - rightEAR)

        nose_point = (nose[3, 0], nose[3, 1])

        # outline
        mouthHull = cv2.convexHull(mouth)
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [mouthHull], -1, YELLOW_COLOR, 1)
        cv2.drawContours(frame, [leftEyeHull], -1, YELLOW_COLOR, 1)
        cv2.drawContours(frame, [rightEyeHull], -1, YELLOW_COLOR, 1)

        for (x, y) in np.concatenate((mouth, leftEye, rightEye), axis=0):
            cv2.circle(frame, (x, y), 2, GREEN_COLOR, -1)
            
        # Check eye aspect ratio for blink
        if diff_ear > WINK_AR_DIFF_THRESH:

            if leftEAR < rightEAR:
                if leftEAR < EYE_AR_THRESH:
                    WINK_COUNTER += 1

                    if WINK_COUNTER > WINK_CONSECUTIVE_FRAMES:
                        pyag.click(button='left')

                        WINK_COUNTER = 0

            elif leftEAR > rightEAR:
                if rightEAR < EYE_AR_THRESH:
                    WINK_COUNTER += 1

                    if WINK_COUNTER > WINK_CONSECUTIVE_FRAMES:
                        pyag.click(button='right')

                        WINK_COUNTER = 0
            else:
                WINK_COUNTER = 0
        else:
            if ear <= EYE_AR_THRESH:
                EYE_COUNTER += 1

                if EYE_COUNTER > EYE_AR_CONSECUTIVE_FRAMES:
                    SCROLL_MODE = not SCROLL_MODE
                    
                    EYE_COUNTER = 0

            else:
                EYE_COUNTER = 0
                WINK_COUNTER = 0

        if mar > MOUTH_AR_THRESH:
            MOUTH_COUNTER += 1

        if MOUTH_COUNTER >= MOUTH_AR_CONSECUTIVE_FRAMES:
            
            INPUT_MODE = not INPUT_MODE
            
            MOUTH_COUNTER = 0
            ANCHOR_POINT = nose_point
    

        if INPUT_MODE:
            cv2.putText(frame, "READING INPUT", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED_COLOR, 2)
            x, y = ANCHOR_POINT
            nx, ny = nose_point
            w, h = 60, 35
            multiple = 1
            cv2.rectangle(frame, (x - w, y - h), (x + w, y + h), GREEN_COLOR, 2)
            cv2.line(frame, ANCHOR_POINT, nose_point, BLUE_COLOR, 2)

            dir = direction(nose_point, ANCHOR_POINT, w, h)
            cv2.putText(frame, dir.upper(), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED_COLOR, 2)
            
            drag = 18      # amount of distance to move per movement
            
            if dir == 'right':
                pyag.moveRel(drag, 0)
            elif dir == 'left':
                pyag.moveRel(-drag, 0)
            elif dir == 'up':
                if SCROLL_MODE:
                    pyag.scroll(40)
                else:
                    pyag.moveRel(0, -drag)
            elif dir == 'down':
                if SCROLL_MODE:
                    pyag.scroll(-40)
                else:
                    pyag.moveRel(0, drag)
            
        if SCROLL_MODE and not SCROLL_MODE_ANNOUNCED:       # announce scroll mode on and off
            engine.say('Scroll mode is on')
            engine.runAndWait()
            SCROLL_MODE_ANNOUNCED = True  
        elif not SCROLL_MODE:
            SCROLL_MODE_ANNOUNCED = False  
        
        if SCROLL_MODE:
            cv2.putText(frame, 'Scroll mode!', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED_COLOR, 2)
            
        cv2.putText(frame, "MAR: {:.2f}".format(mar), (522, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, BLACK_COLOR, 2)
        cv2.putText(frame, "Right EAR: {:.2f}".format(rightEAR), (460, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, BLACK_COLOR, 2)
        cv2.putText(frame, "Left EAR: {:.2f}".format(leftEAR), (470, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, BLACK_COLOR, 2)
        cv2.putText(frame, "Diff EAR: {:.2f}".format(np.abs(leftEAR - rightEAR)), (474, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, BLACK_COLOR, 2)


        cv2.imshow("VisionFlow", frame)
        key = cv2.waitKey(1) & 0xFF

        # escape to exit
        if key == 27:
            break


    cv2.destroyAllWindows()
    vid.release()


def listen_for_command(timeout_duration=2, phrase_limit=5):
    r = sr.Recognizer()
    while True:  # listen for commands
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)  # Adjust for ambient noise once at the start
            print("Speak (listening for 'jarvis' to activate):")
            try:
                audio = r.listen(source, timeout=timeout_duration, phrase_time_limit=phrase_limit)
            except sr.WaitTimeoutError:
                print("Timed out waiting for phrase to start. Please try again.")
                continue  # Go back to the start of the loop and listen again

        try:
            command_detected = r.recognize_google(audio).lower()
            if "jarvis" in command_detected:
                print("'jarvis' keyword detected. Now listening for your command:")
                engine.say('listening to command')
                engine.runAndWait()
                try:
                    with sr.Microphone() as source:
                        r.adjust_for_ambient_noise(source)  # Adjust for ambient noise
                        audio = r.listen(source, timeout=timeout_duration, phrase_time_limit=phrase_limit)
                    text = r.recognize_google(audio).lower()
                    print("You said: " + text)
                    
                    # stop listening
                    
                    if text == "stop listening":  # exits loop
                        print("Stopping listening.")
                        break  
                    
                    # automation
                    
                    elif text == "open brave":
                        os.startfile('C:\\Users\\a\\AppData\\Local\\BraveSoftware\\Brave-Browser\\Application\\brave.exe')     # opens brave browser
                    elif text == "open vs code":
                        os.startfile('C:\\Users\\a\\AppData\\Local\\Programs\\Microsoft VS Code\\code.exe')     # opens brave browser
                        
                    # automate google search
                    
                    elif "search" in text:
                        query = text.split("search for ", 1)[1]
                        if query:
                            search_url = f"https://www.google.com/search?q={query}"
                            webbrowser.open(search_url)
                            print(f"Searching for: {query}")
                        else:
                            print("No search query provided.") 
                    
                    else:
                        pyag.typewrite(text)
                        
                except sr.WaitTimeoutError:
                    print("Timed out waiting for command. Please try again.")
            else:
                print("Keyword 'jarvis' not detected.")
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

if __name__ == "__main__":
    # Create a process for each function
    process1 = Process(target=main_loop)
    process2 = Process(target=listen_for_command)

    # Start both processes
    process1.start()
    process2.start()

    process1.join()
    process2.join()
