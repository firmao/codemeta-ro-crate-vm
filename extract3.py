import requests
import re
import yaml

def generate_requirements_and_ansible():
    # Verified URL from the repository
    url = "https://github.com/rug-compling/Alpino/raw/refs/heads/master/README.md"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text
    except Exception as e:
        print(f"Error: {e}")
        return

    # 1. Identify Software for Installation
    # We focus on the packages that need 'apt' or 'pip' installation inside the VM
    software_to_install = []
    
    # Core system requirements mentioned or implied
    if "git" in content.lower(): software_to_install.append("git")
    if "python" in content.lower(): software_to_install.extend(["python3", "python3-pip"])
    
    # Metadata-specific tools (usually installed via pip or custom scripts)
    # Adding common dependencies for RO-Crate/CodeMeta workflows
    additional_packages = ["curl", "jq", "build-essential"]
    software_to_install.extend(additional_packages)

    # 2. Define the Ansible Playbook Structure
    ansible_playbook = [{
        'name': 'Install Required Software for CodeMeta RO-Crate VM',
        'hosts': 'all',
        'become': True,
        'tasks': [
            {
                'name': 'Update apt cache',
                'apt': {'update_cache': 'yes', 'cache_valid_time': 3600}
            },
            {
                'name': 'Install system packages identified from Readme',
                'apt': {
                    'name': software_to_install,
                    'state': 'present'
                }
            },
            {
                'name': 'Install Python libraries for RO-Crate and CodeMeta',
                'pip': {
                    'name': ['rocrate', 'codemetapy'],
                    'state': 'present',
                    'executable': 'pip3'
                }
            }
        ]
    }]

    # 3. Write to YAML file
    with open('setup_vm.yml', 'w') as f:
        yaml.dump(ansible_playbook, f, default_flow_style=False, sort_keys=False)
    
    print("--- Analysis Complete ---")
    print(f"Software Identified: {', '.join(software_to_install)}")
    print("Ansible playbook generated: setup_vm.yml")

if __name__ == "__main__":
    generate_requirements_and_ansible()