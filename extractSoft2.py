import requests
import re

def extract_requirements():
    # Using the exact verified URL
    url = "https://github.com/rug-compling/Alpino/raw/refs/heads/master/README.md"
    
    try:
        print(f"Connecting to: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text
        print("Successfully read Readme.md\n")
    except Exception as e:
        print(f"Connection Error: {e}")
        return

    # 1. SOFTWARE EXTRACTION
    # We scan for the primary host tools and the guest environment tools
    software_to_check = {
        "Host Orchestration": ["Multipass", "Snap", "Git"],
        "VM Environment": ["Ubuntu", "Bash", "Python"],
        "Application Layer": ["RO-Crate", "CodeMeta", "JSON-LD"]
    }

    # 2. RESOURCE ALLOCATION EXTRACTION
    # Looking for flags like --mem 2G, --cpus 2, --disk 5G
    resources = {
        "Memory (RAM)": re.search(r"--mem\s+([\w\d]+)", content),
        "CPU Cores": re.search(r"--cpus\s+(\d+)", content),
        "Disk Space": re.search(r"--disk\s+([\w\d]+)", content)
    }

    print("="*50)
    print("COMPLETE SOFTWARE & HARDWARE REQUIREMENTS")
    print("="*50)

    # Output Software
    for category, tools in software_to_check.items():
        print(f"\n[{category}]")
        for tool in tools:
            if re.search(rf"\b{tool}\b", content, re.IGNORECASE):
                print(f" • {tool}")

    # Output System Resources
    print("\n[VM HARDWARE ALLOCATIONS]")
    for label, match in resources.items():
        val = match.group(1) if match else "Default (Check Multipass docs)"
        print(f" • {label}: {val}")

if __name__ == "__main__":
    extract_requirements()