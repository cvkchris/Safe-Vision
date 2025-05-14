# SafeVision 🔍🚨

**Real-time Violence Detection System Using Deep Learning**

SafeVision is a real-time crowd surveillance system designed to detect violent behavior in video footage using deep learning models. The goal is to assist in public safety monitoring by automatically flagging potential violent actions for rapid response.

---

## 💡 Motivation

In high-density public environments, human surveillance can be error-prone and slow. SafeVision aims to enhance safety by combining video processing, deep learning, and alert mechanisms to detect violent actions as they occur.

---

## 🎯 Key Features

- 📹 **Video-based input**: Processes live or recorded video footage
- 🧠 **Deep learning models**: Combines CNN-LSTM, ResNet50, InceptionV3, VIVIT, and TCN models
- ⚡ **Real-time detection**: Flags violence with over 90% accuracy in testing
- 📲 **Live alerts**: Sends instant Telegram alerts upon detection
- 🛠️ **Custom labeling pipeline**: Built using CVAT for precise frame-level annotations

---

## 🛠️ Tech Stack

| Area             | Tools Used                                     |
|------------------|------------------------------------------------|
| Language         | Python                                         |
| Deep Learning    | TensorFlow, Keras, OpenCV, Scikit-learn        |
| Video Processing | OpenCV, FFmpeg                                 |
| Backend/API      | Flask                                          |
| Notifications    | Telegram Bot API                               |
| Deployment       | Docker                                         |
| UI               | HTML, CSS, JavaScript (Basic Frontend)         |
| Annotation Tool  | CVAT                                           |

---

## 🧪 Models Implemented

- **ResNet50**: Base image classifier
- **CNN + LSTM**: Temporal violence classification
- **TCN** (Temporal Convolutional Network): Captures long-term sequence patterns
- **InceptionV3**: Visual feature extractor
- **VIVIT** (Vision Transformer): For spatio-temporal video modeling

---
## Methodology 
![image](https://github.com/user-attachments/assets/26f2dca1-aed6-4b20-95b0-7276570f28c1)


## 📊 Dataset

- Self-curated dataset with **2,000+ video clips**, including violent and non-violent scenes
- Annotated using **CVAT** at the frame level for fine-grained detection
- Balanced across multiple environmental conditions and angles

---
## Result 

https://drive.google.com/file/d/1Bh-7aT1qkCYRVfD19R0qaac2JnrREVdG/view
https://drive.google.com/file/d/1F2tYTWcy1nyFxUnqR_4gk1MUt5YYL3Yq/view?usp=drive_link
![image](https://github.com/user-attachments/assets/cfe25fc2-ba90-4366-af9b-4818af19fa04)





