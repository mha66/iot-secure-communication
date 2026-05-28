import tkinter as tk
import threading
import queue
import socket
import json
from datetime import datetime


from rsa import RSA
from aes import AES

HOST = '0.0.0.0'
PORT = 65432

class SmartEnergyDashboard:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("IoT Smart Energy Monitor - Secure Gateway")
        self.root.geometry("650x750")
        self.root.configure(bg="#f4f4f4")
        
        self.data_queue = queue.Queue()
        self.alert_active = False
        
        # Array to hold the last 10 decrypted power readings for the graph
        self.history = [0] * 10 
        
        self.build_ui()
        
        self.server_thread = threading.Thread(target=self.run_secure_server, daemon=True)
        self.server_thread.start()
        
        self.root.after(100, self.update_ui_from_queue)

    def build_ui(self):
        # --- 1. SYSTEM ARCHITECTURE ---
        arch_frame = tk.LabelFrame(self.root, text="System Architecture Status", bg="#f4f4f4", font=("Arial", 10, "bold"))
        arch_frame.pack(fill="x", padx=20, pady=5)
        
        self.lbl_gateway = tk.Label(arch_frame, text="Gateway Server: ONLINE (Listening...)", fg="green", bg="#f4f4f4")
        self.lbl_gateway.pack(anchor="w", padx=10, pady=2)
        
        self.lbl_node = tk.Label(arch_frame, text="IoT Sensor Node: WAITING FOR CONNECTION...", fg="orange", bg="#f4f4f4")
        self.lbl_node.pack(anchor="w", padx=10, pady=2)

        # --- 2. LIVE DATA & GRAPH ---
        data_frame = tk.Frame(self.root, bg="white", highlightbackground="gray", highlightthickness=1)
        data_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(data_frame, text="Current Power Consumption", font=("Arial", 14), bg="white").pack(pady=5)
        
        self.lbl_power = tk.Label(data_frame, text="-- W", font=("Arial", 40, "bold"), fg="#2c3e50", bg="white")
        self.lbl_power.pack()
        
        self.lbl_sensor_id = tk.Label(data_frame, text="Sensor ID: N/A", font=("Arial", 10), bg="white", fg="gray")
        self.lbl_sensor_id.pack(pady=5)
        
        # The Native Tkinter Graph Canvas
        self.graph_width = 500
        self.graph_height = 120
        self.graph_canvas = tk.Canvas(data_frame, width=self.graph_width, height=self.graph_height, bg="white", highlightthickness=0)
        self.graph_canvas.pack(pady=10)
        self.draw_graph() # Draw the initial empty graph

        # --- 3. USER ACTIONS ---
        action_frame = tk.LabelFrame(self.root, text="User Actions & Thresholds", bg="#f4f4f4", font=("Arial", 10, "bold"))
        action_frame.pack(fill="x", padx=20, pady=5)
        
        tk.Label(action_frame, text="Set Overload Warning Limit (Watts):", bg="#f4f4f4").pack(pady=5)
        self.threshold_slider = tk.Scale(action_frame, from_=100, to=3000, orient="horizontal", bg="#f4f4f4", length=300)
        self.threshold_slider.set(1500) 
        self.threshold_slider.pack()
        
        self.lbl_alert = tk.Label(action_frame, text="SYSTEM NORMAL", font=("Arial", 12, "bold"), bg="green", fg="white", width=30)
        self.lbl_alert.pack(pady=10)
        
        self.btn_ack = tk.Button(action_frame, text="Acknowledge Alert", command=self.acknowledge_alert, state=tk.DISABLED)
        self.btn_ack.pack(pady=5)
        
        # --- 4. DECRYPTED EVENT LOG ---
        log_frame = tk.LabelFrame(self.root, text="Decrypted Event Log", bg="#f4f4f4")
        log_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.log_text = tk.Text(log_frame, height=5, bg="black", fg="lime", font=("Courier", 9))
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    def draw_graph(self):
        """Draws a rolling line graph dynamically on the Tkinter Canvas."""
        self.graph_canvas.delete("all") # Clear previous drawing
        
        # Draw grid lines
        for i in range(1, 4):
            y = i * (self.graph_height / 4)
            self.graph_canvas.create_line(0, y, self.graph_width, y, fill="#e0e0e0", dash=(2, 2))
        
        max_val = 3000 # Fixed scale to match the slider max
        num_points = len(self.history)
        spacing = self.graph_width / (num_points - 1) if num_points > 1 else self.graph_width
        
        points = []
        for i, val in enumerate(self.history):
            x = i * spacing
            # Invert Y axis because Canvas (0,0) is top-left
            y = self.graph_height - ((val / max_val) * self.graph_height)
            points.append((x, y))
            
        # Draw the line connecting the data points
        if len(points) > 1:
            for i in range(len(points) - 1):
                self.graph_canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill="#3498db", width=3)
                
        # Draw dots at the exact data points
        for x, y in points:
            self.graph_canvas.create_oval(x-4, y-4, x+4, y+4, fill="#2980b9", outline="white", width=1)

    def log_message(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.log_text.see(tk.END) 

    def acknowledge_alert(self):
        self.alert_active = False
        self.lbl_alert.config(text="SYSTEM NORMAL", bg="green")
        self.btn_ack.config(state=tk.DISABLED)
        self.log_message("User acknowledged warning.")

    def trigger_alert(self):
        if not self.alert_active:
            self.alert_active = True
            self.lbl_alert.config(text="OVERLOAD WARNING!", bg="red")
            self.btn_ack.config(state=tk.NORMAL)
            self.log_message("ALERT: Power threshold exceeded!")

    def update_ui_from_queue(self):
        try:
            while True: 
                msg_type, data = self.data_queue.get_nowait()
                
                if msg_type == "status":
                    if data == "connected":
                        self.lbl_node.config(text="IoT Sensor Node: CONNECTED AND SECURE", fg="green")
                        self.log_message("Key Exchange successful. Secure connection established.")
                    elif data == "disconnected":
                        self.lbl_node.config(text="IoT Sensor Node: DISCONNECTED", fg="red")
                        self.lbl_power.config(text="-- W", fg="gray")
                
                elif msg_type == "data":
                    power_val = data.get("value", 0)
                    self.lbl_power.config(text=f"{power_val} W", fg="#2c3e50")
                    self.lbl_sensor_id.config(text=f"Sensor ID: {data.get('sensor', 'Unknown')}")
                    
                    self.log_message(f"Decrypted Payload: {json.dumps(data)}")
                    
                    # --- GRAPH UPDATE LOGIC ---
                    self.history.append(power_val)   # Add new reading
                    self.history = self.history[-10:] # Keep only the last 10 readings
                    self.draw_graph()                # Redraw the UI Canvas
                    
                    if power_val > self.threshold_slider.get():
                        self.trigger_alert()
                        
        except queue.Empty:
            pass
            
        self.root.after(100, self.update_ui_from_queue)

    def run_secure_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            
            rsa = RSA()
            aes = None  # AES is initialized once the server has the session key from the device
            
            while True:
                conn, addr = server_socket.accept()
                with conn:
                    self.data_queue.put(("status", "connected"))
                    
                    buffer = ""
                    while True:
                        data = conn.recv(4096)
                        if not data:
                            self.data_queue.put(("status", "disconnected"))
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
                                encrypted_session_key = int(request_json['session_key'], 16)
                                decrypted_session_key_int = rsa.decrypt(encrypted_session_key)
                                decrypted_session_key_bytes = decrypted_session_key_int.to_bytes(16, byteorder='big')
                                aes = AES(decrypted_session_key_bytes)  
                                
                            # Handle Continuous Data Streams
                            elif request_json.get("action") == "send_data":
                                if aes is not None:
                                    iv = bytes.fromhex(request_json['iv'])
                                    ciphertext = bytes.fromhex(request_json['data'])
                                    
                                    decrypted_string = aes.cbc_decrypt(iv, ciphertext)
                                    decrypted_json = json.loads(decrypted_string)
                                    self.data_queue.put(("data", decrypted_json))

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartEnergyDashboard(root)
    root.mainloop()