# IoT Secure Communication System

A Python-based IoT simulation demonstrating a secure communication pipeline between an IoT sensor node and a Gateway/Dashboard. This project features **from-scratch implementations of RSA and AES encryption algorithms** to establish a secure hybrid cryptography system. 

It uses RSA for a secure session key exchange and AES (CBC mode) for encrypting the continuous flow of telemetry data (power consumption readings). The receiver includes a real-time `tkinter` GUI dashboard to monitor incoming data, graph it, and trigger alerts.

## 🌟 Features

* **Custom Cryptography**: Pure Python implementations of AES (Advanced Encryption Standard) and RSA (Rivest-Shamir-Adleman) without relying on external crypto libraries.
* **Hybrid Encryption Pipeline**: 
    1. The client requests the server's RSA Public Key.
    2. The client generates an AES Session Key, encrypts it using RSA, and sends it to the server.
    3. The server decrypts the AES key using its RSA Private Key.
    4. Both parties communicate continuously using AES-CBC encryption.
* **Smart Energy Dashboard**: A real-time `tkinter` graphical user interface that plots live power usage, decrypts logs, and supports interactive threshold alerts.

---

## 📦 Dependencies

This project is written in Python 3. Because the cryptography is implemented from scratch, there are no external crypto dependencies. However, the following non-crypto utility package is required:

* **`numpy`**: Used extensively in `aes.py` for efficient matrix operations, Galois Field arithmetic, and fixed-size integer type handling (`np.uint8`).
* **`tkinter`**: Used for the GUI. (This is included in the Python Standard Library, but on some Linux distributions, you may need to install it via your package manager, e.g., `sudo apt install python3-tk`).

---

## 🛠️ Compilation & Setup Instructions

Python is an interpreted language, so no traditional AOT compilation is required. However, you need to set up the environment:

1. **Clone or Extract the Repository:**
   Navigate into the project folder containing the source files.

2. **Create a Virtual Environment (Optional but Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install the Required Packages:**
   ```bash
   pip install numpy 
   ```
---

## 🚀 Run Instructions

To simulate the system, you will need to run the Receiver (Server) and the Sender (Client) in two separate terminal windows.

### 1. Start the Receiver (Gateway Dashboard)
Run the server script first. This will open the Tkinter GUI and start listening for incoming connections on port `65432`.
```bash
python iot_receiver_gui.py
```

### 2. Configure the Sender (Sensor Node)
Open `iot_sender.py` in a text editor. By default, `SERVER_IP` is hardcoded to `'192.168.1.19'`. 
* If you are running both scripts on the same machine, **change this to `127.0.0.1`**:
  ```python
  SERVER_IP = '127.0.0.1' 
  ```

### 3. Start the Sender (Sensor Node)
In a new terminal window (on the same/another device), start the simulated IoT device. It will perform the handshake and begin sending encrypted telemetry data every 10 seconds.
```bash
python iot_sender.py
```

---

## 📊 Example Inputs & Outputs

### 🔹 Sender (Terminal Output)
When you start the `iot_sender.py`, the terminal will display the handshake process and confirm operational mode.

**Terminal Log:**
```text
[IoT] Booting up... Requesting RSA Public Key.
[IoT] Generating AES Session Key...
[IoT] Handshake Complete! Entering operational mode.
```

**Internal Generated Data (Plaintext Input):**
Behind the scenes, the sender generates a JSON payload similar to this:
```json
{"sensor": "CT_Clamp_Main", "value": 1456, "unit": "W", "status": "ACTIVE"}
```
*This data is immediately padded, encrypted via AES-CBC, and sent over the network as a hex string.*

### 🔹 Receiver (GUI Dashboard & Log)
When the sender connects and transmits, the Tkinter dashboard will update automatically. 

**GUI Dashboard in Normal State:**
<img style="width: auto; height: 700px;" alt="Screenshot 2026-05-26 005117" src="https://github.com/user-attachments/assets/931f2bd1-9482-42a7-a592-33c2ee7ab41b" />

**GUI Dashboard in Alert State:**
<img style="width: auto; height: 700px;" alt="Screenshot 2026-05-26 005136" src="https://github.com/user-attachments/assets/c4e0d5d6-dfce-43fc-98bc-e73624f5cf08" />


