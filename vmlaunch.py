import json
import yaml
import subprocess
import os

def build_and_launch():
    # 1. Parse JSON-LD
    try:
        with open('code-meta.jsonld', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: code-meta.jsonld not found.")
        return

    vm_name = data.get('name', 'autovm').lower().replace(" ", "-")
    
    # 2. Map Metadata to Cloud-Init YAML
    cloud_config = {
        'package_update': True,
        'packages': data.get('softwareRequirements', ['python3', 'git']),
        'write_files': [{
            'path': '/etc/motd',
            'content': f"Welcome to the VM for {vm_name}\nVersion: {data.get('version', '1.0')}\n"
        }],
        'runcmd': [
            'echo "Environment setup complete."'
        ]
    }

    # Save the YAML file
    with open('vm-config.yaml', 'w') as f:
        yaml.dump(cloud_config, f)

    # 3. Provision the VM
    print(f"🚀 Launching Virtual Machine: {vm_name}...")
    
    # Command: multipass launch --name <name> --cloud-init <file>
    launch_cmd = ["multipass", "launch", "--name", vm_name, "--cloud-init", "vm-config.yaml"]
    
    try:
        result = subprocess.run(launch_cmd, capture_output=True, text=True, check=True)
        print(f"✅ VM '{vm_name}' is now running!")
        print(f"Access it using: multipass shell {vm_name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch VM: {e.stderr}")

if __name__ == "__main__":
    build_and_launch()
