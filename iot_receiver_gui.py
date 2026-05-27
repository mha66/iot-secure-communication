import queue
import socket
import json

from rsa import RSA
from aes import AES

HOST = '0.0.0.0'
PORT = 65432

class SmartEnergyDashboard:
    def __init__(self):
        self.data_queue = queue.Queue()

    def run_secure_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            
            rsa = RSA()
            aes = None  # AES is initialized once the server has the session key from the device
            
            while True:
                conn, addr = server_socket.accept()
                with conn:
                    self.data_queue.put(("status", "connected")) # for UI update
                    
                    buffer = ""
                    while True:
                        data = conn.recv(4096)
                        if not data:
                            self.data_queue.put(("status", "disconnected")) # for UI update
                            break 
                            
                        buffer += data.decode('utf-8')
                        
                        while "\n" in buffer:
                            message, buffer = buffer.split("\n", 1)
                            if not message.strip(): continue
                            
                            request_json = json.loads(message)
                            
                            # Handle RSA Public Key Exchange
                            if request_json.get("action") == "request_public_key":
                                pub_key_payload = {"e": rsa.e, "n": hex(rsa.n)[2:]}
                                conn.sendall((json.dumps(pub_key_payload) + "\n").encode('utf-8'))

                            # Handle AES Session Key Exchange
                            elif request_json.get("action") == "key_exchange":
                                encrypted_session_key_int = int(request_json['session_key'], 16)
                                decrypted_session_key_int = rsa.decrypt(encrypted_session_key_int)
                                decrypted_session_key_bytes = decrypted_session_key_int.to_bytes(16, byteorder='big')
                                aes = AES(decrypted_session_key_bytes)  
                                
                            # Handle Continuous Data Streams
                            elif request_json.get("action") == "send_data":
                                if aes is not None:
                                    iv = bytes.fromhex(request_json['iv'])
                                    ciphertext = bytes.fromhex(request_json['data'])
                                    
                                    decrypted_string = aes.cbc_decrypt(iv, ciphertext)
                                    decrypted_json = json.loads(decrypted_string)
                                    self.data_queue.put(("data", decrypted_json)) # for UI update
                                else:
                                    self.log_message("Error: Received data before session key was established.")
