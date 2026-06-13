# Wireless Audio Sharing Setup

This project allows you to stream your Android phone's system audio to your PC over Wi-Fi (or USB). It is optimized for **Python 3.14+**.

## Prerequisites

1.  **Python 3.14+** installed on your PC.
2.  **Android 10+** phone.
3.  **ADB (Android Debug Bridge)** installed system-wide.
4.  **sndcpy** from https://github.com/rom1v/sndcpy/releases (Standard version) extracted on your PC and send APK to your phone

---

## Step 1: Install Python Dependencies

Open your terminal and run:

```powershell
pip install sounddevice numpy
```

---

## Step 2: Prepare the Android Phone

1.  Enable **Developer Options** and **USB Debugging**.
2.  (For Wireless) Enable **Wireless Debugging**.
3.  Install the **sndcpy** APK on your phone.
4.  Open `sndcpy`, tap **"Start"**, and grant permission.

---

## Step 3: Connect and Stream

### 1. Connect to the Phone
If using wireless, ensure you have **paired** the device first if it's your first time:
```powershell
adb pair <PHONE_IP>:<PAIRING_PORT>
adb connect <PHONE_IP>:<CONNECTION_PORT>
```

### 2. Forward the Audio Port
If you have multiple devices listed in `adb devices`, specify your target:
```powershell
adb -s <DEVICE_ID_OR_IP> forward tcp:28200 localabstract:sndcpy
```

### 3. Start the Receiver
```powershell
python receiver.py
```

---

## Troubleshooting (Lessons Learned)

### 1. ADB Connection Failed
- **Symptoms:** `failed to connect to 192.168.x.x`
- **Solution:** 
  - Ensure the phone and PC are on the same subnet (e.g., both on 192.168.137.x).
  - Android 11+ requires `adb pair` before the first `adb connect`.
  - Toggle Wireless Debugging OFF and ON to refresh the port.

### 2. "More than one device/emulator"
- **Symptoms:** Error when running `adb forward`.
- **Solution:** Use the `-s` flag followed by the device ID found in `adb devices`. 
  - Example: `adb -s 192.168.137.97:37053 forward ...`
  - Alternatively, unplug any USB cables if you only want to use the wireless connection.

### 3. Python 3.14+ Compatibility
- **Symptoms:** `pyaudio` fails to build or `pipwin` errors.
- **Solution:** Use `sounddevice` and `numpy` as they support modern Python bytecodes and offer better performance on Windows.

### 4. Audio Lag
- **Solution:** Use a 5GHz Wi-Fi band or connect via USB for the lowest possible latency.
