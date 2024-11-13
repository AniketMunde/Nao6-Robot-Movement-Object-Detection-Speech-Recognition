from connector import getConnection
from os import path
from scp import SCPClient
  
import qi
import time
import math
import os
import sys
import random
import paramiko
import json
import soundfile
import cv2

import numpy as np
import speech_recognition as sr

r = sr.Recognizer()
file_path = path.dirname(path.realpath(__file__))
listening = True

# --------------------------- READ FILE FUNCTION -----------------------------------
def get_answers(txt_path):
    file = open(txt_path, "r")
    content = file.read()
    pairs = content.split(';')

    answers = {}
    for pair in pairs:
            if pair.strip():
                key, value = pair.split('=', 1)
                key = key.strip().strip('"')
                value = value.strip().strip('{}')
                value_list = json.loads(value)
                answers[f"answer_{key.replace(' ', '_')}"] = value_list
    return answers


# --------------------------- BASIC ROBOT FUNCTIONS -----------------------------------
def stand_position(posture_service):
    posture_service.goToPosture("StandInit", 1.0)
    return print("Robot is standing")

def sit_position(posture_service):
    posture_service.goToPosture("Sit", 1.0)
    return print("Robot is sitting")

def download_audio_file(file_name, scp):
    scp.get(file_name, local_path=file_path)
    print("[INFO]: File " + file_name + " downloaded")
    scp.close()

def listen(audio_service, scp):
    audio_service.stopMicrophonesRecording()
    print("Say something to the robot")
    
    audio_service.startMicrophonesRecording("/home/nao/speech.wav", "wav", 16000, (0, 0, 1, 0))
    time.sleep(5)
    audio_service.stopMicrophonesRecording
    
    download_audio_file("speech.wav", scp)

    return print("Listened")


# --------------------------- SPEECH RECOGNITION FUNCTIONS -----------------------------
def recognize_speech(services, obj_position, speech, answers):
    motion_service, tts, posture_service, video_service = services

    speech_lower = speech.lower()

    # Hello Condition
    if (("hello") in speech_lower):
        answer_hello = answers['answer_hello']
        return tts.say(random.choice(answer_hello))

    # What's Your Name Condition
    if (("your name") in speech_lower):
        answer_your_name = answers['answer_your_name']
        return tts.say(random.choice(answer_your_name))
    
    # They say their name Condition
    elif (("my name") in speech_lower):
        name = speech_lower.split()[-1]
        answer_my_name = answers['answer_my_name']
        tts.say(random.choice(answer_my_name) + name)
        return name
    
    # How are you Condition
    elif (("how are you") in speech_lower):
        answer_how_are_you = answers['answer_how_are_you']
        return tts.say(random.choice(answer_how_are_you))
    
    # What can you do Condition
    elif (("what can you") in speech_lower):
        answer_what_can_you = answers['answer_what_can_you']
        return tts.say(random.choice(answer_what_can_you))
    
    # Stand up Condition
    elif (("stand") in speech_lower):
        answer_stand = answers['answer_stand']
        tts.say(random.choice(answer_stand))
        return stand_position(posture_service)

    # Sit down Condition
    elif (("sit") in speech_lower):
        answer_sit = answers['answer_sit']
        tts.say(random.choice(answer_sit))
        return sit_position(posture_service)

    # Thank you Condition
    elif (("thank you") in speech_lower):
        answer_thank_you = answers['answer_thank_you']
        return tts.say(random.choice(answer_thank_you))
    
    # Good job Condition
    elif (("good job") in speech_lower):
        answer_good_job = answers['answer_good_job']
        return tts.say(random.choice(answer_good_job))

    # Bye Condition
    elif (("goodbye") in speech_lower):
        answer_bye = answers['answer_goodbye']
        tts.say(random.choice(answer_bye))
        listening = False
        return motion_service.rest()

    # Walk to 
    elif(("walk") in speech_lower):
        answer_walk = answers['answer_walk']
        tts.say(random.choice(answer_walk))
        return walk_to_object(motion_service, obj_position, posture_service)

    # Can you grab Condition
    elif (("grab") or ("pick up") or ("get") or ("i want") in speech_lower):
        answer_grab_pos = answers['answer_grab_pos']

        answer_grab_neg = answers['answer_grab_neg']

        answer_grab_neg_end = answers['answer_grab_neg_end']

        if (("red ball") in speech_lower):
            #if (detect_object(video_service)):
                tts.say(random.choice(answer_grab_pos) + "red ball")
                walk_to_object(motion_service, obj_position, posture_service)
                return pick_up_object(motion_service, obj_position)

            #else: 
                #return tts.say(random.choice(answer_grab_neg) + "red ball" + answer_grab_neg_end)

        if (("green ball") in speech_lower):
            #if (detect_object(video_service)):
                tts.say(random.choice(answer_grab_pos) + "green ball")
                walk_to_object(motion_service, obj_position, posture_service)
                return pick_up_object(motion_service, obj_position)

            #else: 
                #return tts.say(random.choice(answer_grab_neg) + "green ball" + answer_grab_neg_end)

        else:
            answer_else_grab = answers['answer_else_grab']
            return tts.say(random.choice(answer_else_grab))
    
    else:
        answer_else_speech = answers['answer_else_speech']
        return tts.say(random.choice(answer_else_speech))

def detect_speech(services, obj_position, answers):    
    AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "speech.wav")

    data, samplerate = soundfile.read(AUDIO_FILE)
    soundfile.write(AUDIO_FILE, data, samplerate)

    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)

    try:
        speech = r.recognize_google(audio)
        recognize_speech(services, obj_position, speech, answers)

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")

    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


# --------------------------------- OBJECT FUNCTIONS --------------------------------
def detect_color(img, lower_bound, upper_bound):
    """
    Detect regions in the image that fall within the specified color range.
    Returns the bounding boxes of detected regions.
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 20 and h > 20:  # Filter out small boxes
            boxes.append([x, y, w, h])
    
    return boxes

def draw_boxes(img, boxes, color):
    """
    Draw bounding boxes on the image.
    """
    for (x, y, w, h) in boxes:
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)

# Detect the object
def detect_object(video_service):
    # Set up camera parameters
    camera_index = 1
    resolution = 2  # VGA resolution
    color_space = 11  # RGB color space
    fps = 30

    cv2.namedWindow("NAO Camera Feed", cv2.WINDOW_NORMAL)

    video_client = video_service.subscribeCamera("color_detection", camera_index, resolution, color_space, fps)

    # Define color ranges for detection in HSV format
    color_ranges = {
        "red": (np.array([0, 120, 70]), np.array([10, 255, 255])),  # Adjusted for red
        "green": (np.array([36, 100, 100]), np.array([86, 255, 255])),  # Adjusted for green
        "blue": (np.array([94, 80, 2]), np.array([126, 255, 255]))  # Adjusted for blue
    }

    # Define colors for bounding boxes in BGR format
    box_colors = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255)
    }

    try:
        while True:
            # Get the image from the camera
            img = video_service.getImageRemote(video_client)
            if img is None:
                print("Failed to capture image")
                continue

            # Convert the image to a format suitable for OpenCV
            width, height = img[0], img[1]
            image_data = np.frombuffer(img[6], dtype=np.uint8).reshape((height, width, 3))

            # Detect and draw bounding boxes for each color
            for color_name, (lower_bound, upper_bound) in color_ranges.items():
                boxes = detect_color(image_data, lower_bound, upper_bound)
                draw_boxes(image_data, boxes, box_colors[color_name])

            # Display the image in the window
            cv2.imshow("NAO Camera Feed", image_data)

            # Check if the user has pressed the 'q' key to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Clean up
        video_service.unsubscribe(video_client)
        cv2.destroyAllWindows()
    return (0, 0, 10)

# Walk towards the object
def walk_to_object(motion_service, obj_position, posture_service):
    posture_service.goToPosture("StandInit", 1.0)
    x, y, z = obj_position 
    distance = math.sqrt(x*2 + y*2)
    angle = math.atan2(y, x)
    
    # Move towards the object
    motion_service.moveTo(distance, 0, angle)

# Pick up the object
def pick_up_object(motion_service, obj_position):
    # Assuming the object is in front and reachable by the arm
    motion_service.setAngles("RShoulderPitch", 0.0, 0.2)  # Adjust the arm pitch
    motion_service.setAngles("RElbowYaw", 0.0, 0.2)       # Adjust the elbow yaw
    motion_service.setAngles("RHand", 1.0, 0.2)           # Open the hand
    time.sleep(1)
    
    # Move the arm to grasp the object
    motion_service.setAngles("RShoulderPitch", 0.5, 0.2)  # Lower the arm
    time.sleep(1)
    motion_service.setAngles("RHand", 0.0, 0.2)           # Close the hand to grasp
    time.sleep(1)
    
    # Lift the object
    motion_service.setAngles("RShoulderPitch", 0.0, 0.2)  # Lift the arm
    time.sleep(1)


# ---------------------------- MAIN FUNCTION -------------------------------
def main():
    app = getConnection()
    
    # Get the services
    motion_service = app.session.service("ALMotion")
    tts = app.session.service("ALTextToSpeech")
    posture_service = app.session.service("ALRobotPosture")
    audio_service = app.session.service("ALAudioRecorder")
    video_service = app.session.service("ALVideoDevice")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.connect(hostname="IP_ADDRESS", username="username", password="password")
    scp = SCPClient(ssh.get_transport())

    services = motion_service, tts, posture_service, video_service
    
    # Wake up robot
    motion_service.wakeUp()
    
    # Detect the object
    obj_position = 0.3, 0, 0

    # Get dictionary
    txt_path = "/../dictionary.txt"
    answers = get_answers(txt_path)

    while listening is True:
        listen(audio_service, scp)
        detect_speech(services, obj_position, answers)
        time.sleep(3)

    # Rest robot
    motion_service.rest()

if __name__ == "__main__":
    main()
