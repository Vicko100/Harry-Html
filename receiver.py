import socket
import sounddevice as sd
import numpy as np
import sys

# --- Configuration ---
# sndcpy uses: 48000Hz, 16-bit Signed PCM, Stereo
SAMPLERATE = 48000
CHANNELS = 2
PORT = 28200 # Port forwarded via ADB
BLOCKSIZE = 1024 # Buffer size

def start_receiver():
    print(f"[*] Audio receiver (SoundDevice Edition) started.")
    print(f"[*] Python Version: {sys.version.split()[0]}")
    
    # Initialize the output stream
    # dtype='int16' matches sndcpy's output
    try:
        stream = sd.RawOutputStream(
            samplerate=SAMPLERATE,
            blocksize=BLOCKSIZE,
            channels=CHANNELS,
            dtype='int16'
        )
        stream.start()
        
        print(f"[*] Waiting for audio data on localhost:{PORT}...")
        
        # Connect to the local port forwarded by ADB
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(('127.0.0.1', PORT))
                print("[+] Connected to audio stream! Play some music on your phone.")
            except ConnectionRefusedError:
                print("[-] Error: Could not connect to the audio stream.")
                print("    1. Make sure 'sndcpy' is running on your phone and you tapped 'Start'.")
                print(f"    2. Run: adb forward tcp:{PORT} localabstract:sndcpy")
                return

            try:
                while True:
                    # sndcpy sends raw 16-bit PCM. 
                    # Each sample is 2 bytes, 2 channels = 4 bytes per frame.
                    data = s.recv(BLOCKSIZE * 4) 
                    if not data:
                        print("\n[-] Stream closed by phone.")
                        break
                    
                    # Write raw bytes directly to sounddevice
                    stream.write(data)
                    
            except KeyboardInterrupt:
                print("\n[*] Stopping...")
            except Exception as e:
                print(f"\n[-] Streaming error: {e}")
    
    except Exception as e:
        print(f"[-] Sound Device error: {e}")
        print("    Try installing the latest sound drivers or check your output device.")
    
    finally:
        if 'stream' in locals():
            stream.stop()
            stream.close()

if __name__ == "__main__":
    start_receiver()
