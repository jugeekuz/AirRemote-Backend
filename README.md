<p align="center">
  <img width="340" src="src/assets/imgs/logo-black.png#gh-light-mode-only" alt="AirRemote Logo">
  <img width="340" src="src/assets/imgs/logo-white.png#gh-dark-mode-only" alt="AirRemote Logo">
</p>
<h2 align="center">AirRemote Backend Repository ⚡</h2>
<p align="center">
    <a href="/LICENSE"><img alt="GPL-V3.0 License" src="https://img.shields.io/badge/License-GPLv3-orange.svg"></a>
    <a href="https://github.com/jugeekuz/AirRemote-Frontend/graphs/contributors"><img alt="Contributors" src="https://img.shields.io/github/contributors/jugeekuz/AirRemote-Frontend?color=green"></a>
    <a href="https://www.linkedin.com/in/anastasiosdiamantis"><img alt="Connect on LinkedIn" src="https://img.shields.io/badge/Connect%20on-LinkedIn-blue.svg"></a>
</p><br>

Turn your old remote-controlled devices into smart devices! With AirRemote, you can turn any legacy device that can be controlled by an IR remote, into a remotely accesible smart device.

<p align="center">
    <img src="./src/assets/imgs/air-remote-demo-short.gif" alt="AirRemote Short Demo" width="320">
</p>


--- 
## 📝  Description


AirRemote is a solution designed to modernize legacy remote-controlled devices by making them smart and remotely accessible. AirRemote operates as a universal remote emulator. It works by capturing the infrared (IR) signals from any remote control—regardless of how rare or obscure—and storing them for later use. You can then replay those commands remotely through the web interface (or through automated routines) enabling you to perform actions such as open the A/C or your heater on your way back, finding your house in the perfect temperature when you arrive, or just keep all your remotes in one place without needing to search for them every time.

## 🔧 Features 
- Record the IR signals by simply pressing the buttons of their existing remote control onto the AirRemote device.
- Replay the stored signals on command via a web interface.
- Create automations to perform a set of operations (such as open lighting, A/C etc.) at specific times.
- Give the device to a friend, with the capability to initialize the device and provide credentials through a Captive Portal interface.
- Manage, Delete, Reorder your favourite devices through the web interface.

With these capabilities, AirRemote turns virtually any device with an IR remote into a smart, remotely controllable appliance.

## 🎥 Demo
<div align="center" style="display: flex; flex-direction: row; justify-content: center; gap: 10px; flex-wrap: wrap;">
  <div>
    <h4>Login & Dashboard</h4>
    <img src="./src/assets/imgs/air-remote-demo-short.gif" alt="Demo 1" width="300">
  </div>
  <div>
    <h4>Add Remote and Execute</h4>
    <img src="./src/assets/imgs/air-remote-demo-short.gif" alt="Demo 2" width="300">
  </div>
  <div>
    <h4>Create Automations</h4>
    <img src="./src/assets/imgs/air-remote-demo-short.gif" width="300">
  </div>
  <div>
    <h4>Register Devices</h4>
    <img src="./src/assets/imgs/air-remote-demo-short.gif" width="300">
  </div>
  <div>
    <h4>Reorder & Edit tiles</h4>
    <img src="./src/assets/imgs/air-remote-demo-short.gif" width="300">
  </div>
</div>

## 🌟 Project Overview

The **AirRemote** project is divided into three main components. Each part contains instructions on how to deploy / install it:

- [**Embedded Device:**](https://github.com/jugeekuz/AirRemote-Embedded) 
    - A C/C++ PlatformIO project, involving ESP32-based unit with an IR receiver and 8 powerful IR blasters. It records IR signals from any remote control and replays them across the room, enabling universal compatibility.
    
- [**Serverless Backend (This Repository):**](https://github.com/jugeekuz/AirRemote-Backend) 
    - A Python project using Serverless framework to deploy a scalable AWS-based backend powered by Lambda, DynamoDB, API Gateway, and EventBridge. It ensures secure command storage, user authorization, and efficient routing between the web interface and devices.

- [**Frontend :**](https://github.com/jugeekuz/AirRemote-Frontend) 
    - A React JS project providing an application for managing devices, saving IR commands, authenticating users and creating powerful automation routines—all accessible through a sleek web interface.

---

## ⚙️ Installation and deployment
### 📦 Prerequisites

1. Make sure you have npm 10.0+ installed.
    ```bash
    npm -v
    ```

2. Make sure you have [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) installed and configured:
    ```bash
    aws --v
    aws s3 ls
    ```

3. Make sure you have [pip](https://pypi.org/project/pip/) installed in your system.
    ```bash
    pip --version
    ```

4. Make sure you have [Serverless Framework v3.39](https://www.serverless.com/) installed and credentials configured with correct permissions in AWS in your system.
    ```bash
    serverless -v
    ```

### 🚀 Deployment to AWS

1. #### Clone this repository:
    ```bash
    git clone https://github.com/jugeekuz/AirRemote-Backend
    ```
2. #### Install deployment dependencies:
    ```bash
    npm install
    ```
3. #### Install environment dependencies:
    ```bash
    pip install -r requirements.txt -t ./vendor
    ```
4. #### First deployment
    Deploy once initially, without configuring anything else, we will redeploy later.
    ```bash
    serverless deploy
    ```
5. 
---

## 📜 License
Licensed under the GPL V3.0 License.
<a href="https://github.com/jugeekuz/AirRemote-Embedded/blob/master/LICENSE">🔗 View License Details </a>


---

## 🤝 Contributing
Feel free to fork the repository and contribute! Pull requests and feedback are welcome.

