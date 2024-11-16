# Safe Vision
*A Project on Crowd Surveillance*

This API branch contains the code to make a mobile app using **Flutter** in the front-end and **Flask-API** in the backend.

---
## How to Run

1. Clone the repository using ```git clone https://github.com/cvkchris/Safe-Vision.git``` or download the file.
2. Create a python environment with ``` python -m venv venv```.
3. Pip install all the requirements using ```pip install -r requirements.txt```.
4. Download Android studio and set up an emulator of Android 14 or above version.
5. In Android Studio, go to the SDK manager and install flutter and dart plugin in the plugins.
6. Now open cmd in the root directory of the project and run the app.py file by using ```python app.py```. This makes the flask api ready to respond to the API requests.
7. Now open a second cmd  in the root directory and navigate to the safevision directory by using ```cd safevision```
8. In the safevision directory run the following  ```flutter pub get``` to get the latest version of the libraries.
9. Then run ```flutter emulators``` to see the list of emulators
10. Run ```flutter emulators --launch <emulator-id>``` to launch the emulator and connect it with fluttter.
11. Now ```flutter run``` to build the apk and install it in the emulator.
12. Now you can use the app.

---

