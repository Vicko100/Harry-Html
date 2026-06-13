import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import socket
import sounddevice as sd
import numpy as np
import sys
import os

# --- Configuration ---
SAMPLERATE = 48000
CHANNELS = 2
PORT = 28200
BLOCKSIZE = 1024

class AudioSharingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wireless Audio Sharing")
        self.root.geometry("450x550")
        self.root.resizable(False, False)
        
        # State
        self.is_streaming = False
        self.stream = None
        
        self.setup_ui()

    def setup_ui(self):
        # Styling
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Connection Section ---
        ttk.Label(main_frame, text="1. Network Connection", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")
        
        ttk.Label(main_frame, text="Phone IP:").grid(row=1, column=0, sticky="w")
        self.ip_entry = ttk.Entry(main_frame, width=25)
        self.ip_entry.insert(0, "192.168.137.97") # Default from user's history
        self.ip_entry.grid(row=1, column=1, pady=5)

        ttk.Label(main_frame, text="Connection Port:").grid(row=2, column=0, sticky="w")
        self.conn_port_entry = ttk.Entry(main_frame, width=25)
        self.conn_port_entry.insert(0, "37053")
        self.conn_port_entry.grid(row=2, column=1, pady=5)

        self.connect_btn = ttk.Button(main_frame, text="Connect to Phone", command=self.run_connect)
        self.connect_btn.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

        # --- Pairing Section (Optional) ---
        ttk.Separator(main_frame, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky='ew', pady=15)
        ttk.Label(main_frame, text="2. Pairing (First Time Only)", style="Header.TLabel").grid(row=5, column=0, columnspan=2, pady=(0, 10), sticky="w")

        ttk.Label(main_frame, text="Pairing Port:").grid(row=6, column=0, sticky="w")
        self.pair_port_entry = ttk.Entry(main_frame, width=25)
        self.pair_port_entry.grid(row=6, column=1, pady=5)

        ttk.Label(main_frame, text="Pairing Code:").grid(row=7, column=0, sticky="w")
        self.pair_code_entry = ttk.Entry(main_frame, width=25)
        self.pair_code_entry.grid(row=7, column=1, pady=5)

        self.pair_btn = ttk.Button(main_frame, text="Pair Device", command=self.run_pair)
        self.pair_btn.grid(row=8, column=0, columnspan=2, pady=10, sticky="ew")

        # --- Streaming Section ---
        ttk.Separator(main_frame, orient='horizontal').grid(row=9, column=0, columnspan=2, sticky='ew', pady=15)
        ttk.Label(main_frame, text="3. Audio Stream", style="Header.TLabel").grid(row=10, column=0, columnspan=2, pady=(0, 10), sticky="w")

        self.stream_btn = ttk.Button(main_frame, text="START STREAMING", command=self.toggle_stream)
        self.stream_btn.grid(row=11, column=0, columnspan=2, pady=5, sticky="ew")

        # --- Status ---
        self.status_label = ttk.Label(main_frame, text="Status: Ready", foreground="gray")
        self.status_label.grid(row=12, column=0, columnspan=2, pady=20)

    def log(self, message, success=True):
        color = "green" if success else "red"
        self.status_label.config(text=f"Status: {message}", foreground=color)

    def run_adb(self, cmd):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)

    def run_pair(self):
        ip = self.ip_entry.get()
        port = self.pair_port_entry.get()
        code = self.pair_code_entry.get()
        
        if not (ip and port and code):
            messagebox.showwarning("Missing Info", "Please enter IP, Pairing Port, and Code.")
            return

        def task():
            self.log("Pairing...")
            success, output = self.run_adb(f"adb pair {ip}:{port} {code}")
            if success:
                self.log("Successfully Paired!")
            else:
                self.log("Pairing Failed", False)
                messagebox.showerror("Error", output)
        
        threading.Thread(target=task).start()

    def run_connect(self):
        ip = self.ip_entry.get()
        port = self.conn_port_entry.get()
        
        if not (ip and port):
            messagebox.showwarning("Missing Info", "Please enter IP and Connection Port.")
            return

        def task():
            self.log("Connecting...")
            # Disconnect first to be safe
            self.run_adb("adb disconnect")
            success, output = self.run_adb(f"adb connect {ip}:{port}")
            if success and "connected" in output.lower():
                self.log("Connected!")
            else:
                self.log("Connection Failed", False)
                messagebox.showerror("Error", output)
        
        threading.Thread(target=task).start()

    def toggle_stream(self):
        if self.is_streaming:
            self.is_streaming = False
            self.stream_btn.config(text="START STREAMING")
            self.log("Stream Stopped")
        else:
            self.start_stream()

    def start_stream(self):
        ip = self.ip_entry.get()
        port = self.conn_port_entry.get()
        device_id = f"{ip}:{port}"

        # 1. Forward port
        self.log("Setting up port forward...")
        success, output = self.run_adb(f"adb -s {device_id} forward tcp:{PORT} localabstract:sndcpy")
        if not success:
            # Try without -s if it's the only device
            success, output = self.run_adb(f"adb forward tcp:{PORT} localabstract:sndcpy")
            if not success:
                self.log("Forwarding Failed", False)
                messagebox.showinfo("Wait!", "Make sure you have tapped 'Start' in the sndcpy app on your phone first!")
                return

        # 2. Start Audio Thread
        self.is_streaming = True
        self.stream_btn.config(text="STOP STREAMING")
        threading.Thread(target=self.audio_loop, daemon=True).start()

    def audio_loop(self):
        self.log("Streaming Audio...")
        try:
            # Initialize sounddevice
            self.stream = sd.RawOutputStream(
                samplerate=SAMPLERATE,
                blocksize=BLOCKSIZE,
                channels=CHANNELS,
                dtype='int16'
            )
            self.stream.start()

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                try:
                    s.connect(('127.0.0.1', PORT))
                except Exception as e:
                    self.is_streaming = False
                    self.root.after(0, lambda: self.log("Socket Connection Failed", False))
                    return

                while self.is_streaming:
                    try:
                        data = s.recv(BLOCKSIZE * 4)
                        if not data: break
                        self.stream.write(data)
                    except socket.timeout:
                        continue
                    except Exception:
                        break

        except Exception as e:
            self.root.after(0, lambda: self.log(f"Stream Error: {e}", False))
        finally:
            self.is_streaming = False
            if self.stream:
                self.stream.stop()
                self.stream.close()
            self.root.after(0, lambda: self.stream_btn.config(text="START STREAMING"))
            self.root.after(0, lambda: self.log("Stream Ended"))

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioSharingApp(root)
    root.mainloop()
