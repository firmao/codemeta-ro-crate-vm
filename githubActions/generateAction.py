import yaml
import os

def generate_github_action(repo_url):
    # Extract repo name for the filename
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    
    workflow = {
        "name": f"Configure VM for {repo_name}",
        "on": {
            "workflow_dispatch": None,  # Allows manual triggering
            "push": {"branches": ["main"]}
        },
        "jobs": {
            "setup-vm": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {
                        "name": "Checkout Script Repository",
                        "uses": "actions/checkout@v4"
                    },
                    {
                        "name": f"Clone Target Repository: {repo_name}",
                        "run": f"git clone {repo_url} target_repo"
                    },
                    {
                        "name": "Install System Dependencies",
                        "run": "sudo apt-get update && sudo apt-get install -y build-essential python3-pip"
                    },
                    {
                        "name": "Configure Environment",
                        "working-directory": "./target_repo",
                        "run": (
                            "if [ -f requirements.txt ]; then pip install -r requirements.txt; fi\n"
                            "if [ -f setup.sh ]; then chmod +x setup.sh && ./setup.sh; fi"
                        )
                    },
                    {
                        "name": "Run Software",
                        "working-directory": "./target_repo",
                        "run": "# Add your execution command here, e.g., python main.py"
                    }
                ]
            }
        }
    }

    file_name = f"setup_{repo_name.lower()}.yml"
    
    with open(file_name, 'w') as file:
        yaml.dump(workflow, file, sort_keys=False, default_flow_style=False)
    
    print(f"Successfully generated: {file_name}")

if __name__ == "__main__":
    target_repo = "https://github.com/firmao/codemeta-ro-crate-vm.git"
    generate_github_action(target_repo)