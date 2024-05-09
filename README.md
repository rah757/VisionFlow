
# VisionFlow

VisionFlow is an interactive system that combines computer vision and speech recognition technologies to control a computer interface. It allows users to execute commands through facial gestures and voice commands.

## Installation

### Prerequisites
- Python 3.7+
- Libraries:
  - OpenCV (cv2)
  - SpeechRecognition
  - imutils
  - numpy
  - pyttsx3
  - pyautogui
  - dlib

### Setup
1. Clone the repository:
> git clone https://example.com/VisionFlow.git

> cd VisionFlow

2. Install the required Python libraries:
> pip install -r requirements.txt


## Usage

### Starting the Application
Execute the main script to start the application:


> python visionflow.py  



## Key Features

- **Eye Tracking and Blinks**: Control the cursor and execute clicks using eye movements and blinks.
- **Mouth Movements**: Toggle input and scroll modes by opening the mouth.
- **Voice Commands**: Activate by saying "Jarvis" followed by commands such as opening applications or performing Google searches.

## Voice Commands

- **Open Brave**: Launch the Brave browser.
- **Open VS Code**: Start Visual Studio Code.
- **Search for [query]**: Perform a Google search.

## Modules

### Main Loop

The `main_loop` function captures video from the webcam, processes the images to detect facial landmarks, and interprets these to control the mouse and other system functions based on pre-defined thresholds and counters for eye and mouth aspect ratios.

### Speech Recognition

The `listen_for_command` function continuously listens for the wake word "Jarvis". Upon activation, it captures further speech to process commands such as opening software or searching the internet.

## Troubleshooting

- **Webcam Access**: Ensure that no other application is using the webcam.
- **Microphone Sensitivity**: Adjust the microphone settings if the system is having difficulty recognizing commands.

## Contributing

Contributions to VisionFlow are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to submit pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Special thanks to the developers and contributors of OpenCV, dlib, SpeechRecognition, PyAutoGUI, and other libraries used in this project.

