# Wireless Audio Sharing

This project allows you to stream your Android phone's system audio to your PC over Wi-Fi (or USB). It features a user-friendly GUI and is optimized for **Python 3.14+**.

## Features
- **Graphical Interface**: No more messing with complex terminal commands.
- **Auto-ADB**: Handles pairing, connecting, and port forwarding automatically.
- **High Quality**: Uses 48kHz Stereo PCM streaming.
- **Modern Python Support**: Built using `sounddevice` for compatibility with Python 3.14.

---

## Prerequisites

1.  **Python 3.14+** installed on your PC.
2.  **Android 10+** phone.
3.  **ADB (Android Debug Bridge)** installed system-wide.
4.  **sndcpy** (Standard version) extracted on your PC.

---

## Quick Start (Using the GUI)

1.  **Install Dependencies**:
    ```powershell
    pip install sounddevice numpy
    ```

2.  **Prepare Phone**:
    - Enable **Developer Options** and **Wireless Debugging**.
    - Install the **sndcpy** APK on your phone.
    - Open `sndcpy`, tap **"Start"**, and grant permission.

3.  **Launch the App**:
    ```powershell
    python app.py
    ```

4.  **Connect**:
    - Enter your Phone's IP and Port (from Wireless Debugging settings).
    - If it's your first time, use the **Pairing Section** first.
    - Click **Connect to Phone**.
    - Once status shows "Connected", click **START STREAMING**.

---

## Troubleshooting (Lessons Learned)

### 1. ADB "More than one device"
- **Problem**: Error when both USB and Wireless are active.
- **Solution**: The GUI now attempts to target your specific IP automatically. If it fails, try unplugging your USB cable.

### 2. Connection Refused / Socket Error
- **Problem**: The stream won't start.
- **Solution**: You **must** tap "Start" in the `sndcpy` app on your phone *before* clicking "Start Streaming" in the PC app.

### 3. Tkinter "bad option -fill"
- **Problem**: Older versions of the script had layout bugs on Python 3.14.
- **Solution**: Fixed in the current `app.py`. Ensure you are using the latest version of the code which uses `sticky` instead of `fill`.

### 4. Audio Lag or Crackling
- **Problem**: Wi-Fi interference.
- **Solution**: Use a **5GHz** Wi-Fi band or connect via **USB**. If crackling occurs on 3.14, ensure your sound drivers are up to date.

---

## For Developers
If you prefer the command line, you can still use the lightweight `receiver.py`:
1. `adb forward tcp:28200 localabstract:sndcpy`
2. `python receiver.py`
