import json
import yaml
import subprocess
import os

def generate_ro_crate(codemeta_path, output_yaml, repo_url):
    """Converts Codemeta to RO-Crate YAML and extracts VM specs + GitHub Repo."""
    if not os.path.exists(codemeta_path):
        print(f"❌ Error: {codemeta_path} not found.")
        return None

    with open(codemeta_path, 'r') as f:
        cm = json.load(f)

    deps = cm.get("softwareRequirements", [])
    if isinstance(deps, str):
        deps = [deps]
    
    # Ensure 'git' is in dependencies to allow cloning
    if "git" not in deps:
        deps.append("git")

    # Extract repo name for the VM folder
    repo_name = repo_url.split("/")[-1].replace(".git", "")

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
                "name": cm.get("name", repo_name),
                "description": cm.get("description", f"Environment for {repo_url}"),
                "author": cm.get("author", "Unknown"),
                "license": cm.get("license", "Unspecified"),
                "url": repo_url, # Store the source repository URL
                "virtualization": {
                    "cpus": cm.get("runtimePlatform", {}).get("cpus", 2),
                    "memory": cm.get("runtimePlatform", {}).get("memory", "2G"),
                    "disk": cm.get("runtimePlatform", {}).get("disk", "10G"),
                    "os": cm.get("operatingSystem", "22.04")
                },
                "dependencies": deps
            }
        ]
    }

    with open(output_yaml, 'w') as f:
        yaml.dump(ro_crate_data, f, sort_keys=False, default_flow_style=False)
    
    print(f"✅ Generated RO-Crate file: {output_yaml}")
    return ro_crate_data

def launch_vm_with_repo(crate_data):
    """Creates Cloud-init config, clones the repo, and launches the VM."""
    main_node = next(n for n in crate_data["@graph"] if n["@id"] == "./")
    specs = main_node["virtualization"]
    deps = main_node["dependencies"]
    repo_url = main_node["url"]
    vm_name = main_node["name"].lower().replace(" ", "-")
    repo_name = repo_url.split("/")[-1].replace(".git", "")

    # Generate Cloud-init: Install packages AND clone/run the repo
    cloud_init = {
        "package_update": True,
        "packages": deps,
        "runcmd": [
            f"git clone {repo_url} /home/ubuntu/{repo_name}",
            f"cd /home/ubuntu/{repo_name}",
            # Attempt to run a setup or main script if it exists
            "if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi",
            "echo '--- Repository Ready ---' >> /home/ubuntu/setup.log"
        ]
    }
    
    with open("init.yaml", "w") as f:
        yaml.dump(cloud_init, f)

    print(f"🚀 Provisioning VM '{vm_name}' for repo: {repo_url}...")

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
        print(f"✨ Success! VM '{vm_name}' is live and code is cloned.")
        print(f"👉 Enter with: multipass shell {vm_name}")
        print(f"📂 Code located at: /home/ubuntu/{repo_name}")
    finally:
        if os.path.exists("init.yaml"):
            os.remove("init.yaml")

if __name__ == "__main__":
    # --- CONFIGURATION ---
    SOURCE_JSON = "codemeta.json"
    TARGET_YAML = "ro-crate-metadata.yaml"
    GITHUB_REPO = "https://github.com/firmao/codemeta-ro-crate-vm.git"

    if not GITHUB_REPO.startswith("http"):
        print("❌ Invalid URL. Please provide a full GitHub URL.")
    else:
        crate_config = generate_ro_crate(SOURCE_JSON, TARGET_YAML, GITHUB_REPO)
        if crate_config:
            launch_vm_with_repo(crate_config)