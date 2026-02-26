import json
import yaml
import subprocess
import os
import requests
import base64
import re

def extract_github_requirements(repo_url):
    """Scans a GitHub repo for dependencies and OS hints via API."""
    # Parse owner and repo name from URL
    parts = repo_url.strip("/").split("/")
    owner, repo = parts[-2], parts[-1].replace(".git", "")
    
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/"
    response = requests.get(api_url)
    
    found_deps = ["git"] # Git is required to clone the repo in the VM
    detected_os = "22.04" # Default Ubuntu version

    if response.status_code == 200:
        files = [f['name'] for f in response.json()]

        # 1. Detect OS/Environment from Dockerfile
        if "Dockerfile" in files:
            d_resp = requests.get(f"{api_url}Dockerfile")
            if d_resp.status_code == 200:
                content = base64.b64decode(d_resp.json()['content']).decode('utf-8')
                if "ubuntu" in content.lower():
                    detected_os = "22.04"
                elif "alpine" in content.lower():
                    detected_os = "minimized"

        # 2. Detect Python Dependencies
        if "requirements.txt" in files:
            r_resp = requests.get(f"{api_url}requirements.txt")
            if r_resp.status_code == 200:
                content = base64.b64decode(r_resp.json()['content']).decode('utf-8')
                # Filter for package names only (simple regex)
                found_deps.extend(["python3-pip"])
                packages = re.findall(r'^([a-zA-Z0-9\-_]+)', content, re.MULTILINE)
                # Note: These are for system packages. For python-specific libs, 
                # we will use pip inside the VM's runcmd.

    return found_deps, detected_os, repo

def generate_ro_crate(output_yaml, repo_url):
    """Converts GitHub metadata to RO-Crate YAML."""
    deps, os_version, repo_name = extract_github_requirements(repo_url)

    ro_crate_data = {
        "@context": "https://w3id.org/ro/crate/1.1/context",
        "@graph": [
            {
                "@id": "ro-crate-metadata.yaml",
                "@type": "CreativeWork",
                "about": {"@id": "./"},
                "conformsTo": {"@id": "https://w3id.org/ro/crate/1.1"}
            },
            {
                "@id": "./",
                "@type": "Dataset",
                "name": repo_name,
                "description": f"Environment for {repo_url}",
                "url": repo_url,
                "virtualization": {
                    "cpus": 2,
                    "memory": "2G",
                    "disk": "10G",
                    "os": os_version
                },
                "dependencies": deps
            }
        ]
    }

    with open(output_yaml, 'w') as f:
        yaml.dump(ro_crate_data, f, sort_keys=False, default_flow_style=False)
    
    print(f"✅ Generated RO-Crate for: {repo_name}")
    return ro_crate_data

def launch_vm_with_repo(crate_data):
    """Creates Cloud-init config and clones the repo inside the VM."""
    main_node = next(n for n in crate_data["@graph"] if n["@id"] == "./")
    specs = main_node["virtualization"]
    deps = main_node["dependencies"]
    repo_url = main_node["url"]
    repo_name = main_node["name"]
    vm_name = repo_name.lower().replace(" ", "-")

    # Cloud-init to install software AND clone the code
    cloud_init = {
        "package_update": True,
        "packages": deps,
        "runcmd": [
            f"git clone {repo_url} /home/ubuntu/{repo_name}",
            f"cd /home/ubuntu/{repo_name} && if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi"
        ]
    }
    
    with open("init.yaml", "w") as f:
        yaml.dump(cloud_init, f)

    print(f"🚀 Launching VM '{vm_name}' with automated setup...")

    cmd = [
        "multipass", "launch",
        "--name", vm_name,
        "--cpus", str(specs["cpus"]),
        "--memory", specs["memory"],
        "--disk", specs["disk"],
        "--cloud-init", "init.yaml",
        specs["os"]
    ]
	
    try:
        subprocess.run(cmd, check=True)
        print(f"✨ Success! Code cloned to /home/ubuntu/{repo_name}")
        print(f"👉 Access VM: multipass shell {vm_name}")
    finally:
        if os.path.exists("init.yaml"):
            os.remove("init.yaml")

if __name__ == "__main__":
    REPO = "https://github.com/rug-compling/Alpino.git"
    TARGET = "ro-crate-metadata.yaml"

    crate_config = generate_ro_crate(TARGET, REPO)
    if crate_config:
        launch_vm_with_repo(crate_config)