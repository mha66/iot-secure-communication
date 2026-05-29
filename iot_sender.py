import socket
import json
import time
import random

from rsa import RSA
from aes import AES

SERVER_IP = '127.0.0.1' # REPLACE WITH SERVER'S IP ADDRESS OR 127.0.0.1 FOR LOCAL TESTING
PORT = 65432

def simulate_power_sensor_reading():
    reading = random.randint(100, 2000)
    return f'{{"sensor": "CT_Clamp_Main", "value": {reading}, "unit": "W", "status": "ACTIVE"}}'

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_IP, PORT))
        
        # PHASE 1: INITIALIZATION & HANDSHAKE
        print("[IoT] Booting up... Requesting RSA Public Key.")
        client_socket.sendall(json.dumps({"action": "request_public_key"}).encode('utf-8') + b'\n')
        
        # Receive Server's RSA Public Key
        response_data = client_socket.recv(4096).decode('utf-8')
        server_key_json = json.loads(response_data)
        SERVER_E = server_key_json["e"]
        SERVER_N = int(server_key_json["n"], 16)
        server_rsa = RSA(n=SERVER_N, e=SERVER_E)
        
        # Generate the AES Session Key for this TCP connection
        print("[IoT] Generating AES Session Key...")
        aes = AES()  # This will generate a random 16-byte key
        SESSION_KEY = aes.key.flatten(order='F').tobytes()
        
        # Encrypt the Session Key using RSA
        session_key_int = int(SESSION_KEY.hex(), 16)
        encrypted_session_key_int = server_rsa.encrypt(session_key_int) 
        
        # Send the Session Key to the Server
        handshake_payload = {
            "action": "key_exchange",
            "session_key": hex(encrypted_session_key_int)[2:]
        }
        client_socket.sendall((json.dumps(handshake_payload) + "\n").encode('utf-8'))
        print("[IoT] Handshake Complete! Entering operational mode.\n")
        

        # PHASE 2: OPERATIONAL LOOP
        while True:
            sensor_data = simulate_power_sensor_reading()
            
            # Generate a NEW IV for every message, but use the SAME session Key
            iv, ciphertext = aes.cbc_encrypt(sensor_data)  # AES class will generate a random IV internally
            
            payload = {
                "action": "send_data",
                "iv": iv.hex(),
                "data": ciphertext.hex()
            }
            
            client_socket.sendall((json.dumps(payload) + "\n").encode('utf-8'))
            time.sleep(10)

if __name__ == "__main__":
    main()