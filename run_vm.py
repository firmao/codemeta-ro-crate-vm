import subprocess
import os
import urllib.request

def setup_and_run_vm():
    # 1. Configuration
    ISO_URL = "https://dl-cdn.alpinelinux.org/alpine/v3.18/releases/x86_64/alpine-virt-3.18.4-x86_64.iso"
    ISO_NAME = "alpine.iso"
    
    print("--- 🛠️  Installing QEMU (This may take a moment) ---")
    subprocess.run(["sudo", "apt-get", "update"], check=True)
    subprocess.run(["sudo", "apt-get", "install", "-y", "qemu-system-x86"], check=True)

    # 2. Download Alpine Linux ISO if it doesn't exist
    if not os.path.exists(ISO_NAME):
        print(f"--- 📥 Downloading {ISO_NAME}... ---")
        urllib.request.urlretrieve(ISO_URL, ISO_NAME)
    else:
        print(f"--- ✅ {ISO_NAME} already exists. ---")

    # 3. Construct the QEMU command
    # -m: Memory (512MB)
    # -cdrom: The ISO file
    # -nographic: Run in terminal instead of a GUI window
    # -serial mon:stdio: Multiplexes the monitor and serial port to your terminal
    qemu_cmd = [
        "qemu-system-x86_64",
        "-m", "512",
        "-cdrom", ISO_NAME,
        "-nographic",
        "-serial", "mon:stdio"
    ]

    print("--- 🚀 Launching Virtual Machine... ---")
    print("--- TIP: To exit, press 'Ctrl+A' then 'X' ---")
    
    try:
        subprocess.run(qemu_cmd, check=True)
    except KeyboardInterrupt:
        print("\n--- VM Stopped by user ---")

if __name__ == "__main__":
    setup_and_run_vm()