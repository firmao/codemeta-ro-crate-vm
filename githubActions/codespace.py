import yaml
import os

def generate_codespace_workflow(repo_url):
    # Extract repo name for labeling
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    
    workflow = {
        "name": f"Provision Codespace for {repo_name}",
        "on": {
            "workflow_dispatch": {
                "inputs": {
                    "machine_type": {
                        "description": "Choose machine size",
                        "required": True,
                        "default": "basicLinux32gb",
                        "type": "choice",
                        "options": ["basicLinux32gb", "standardLinux32gb", "premiumLinux64gb"]
                    }
                }
            }
        },
        "jobs": {
            "create-codespace": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {
                        "name": "Install GitHub CLI",
                        "run": "sudo apt update && sudo apt install gh -y"
                    },
                    {
                        "name": "Authenticate and Create Codespace",
                        "env": {
                            "GH_TOKEN": "${{ secrets.CODESPACE_TOKEN }}"
                        },
                        "run": (
                            f"gh codespace create --repo {repo_url} "
                            "--machine ${{ github.event.inputs.machine_type }} "
                            f"--display-name 'DevEnv-{repo_name}'"
                        )
                    },
                    {
                        "name": "Verify Environment Setup",
                        "env": {
                            "GH_TOKEN": "${{ secrets.CODESPACE_TOKEN }}"
                        },
                        "run": (
                            f"gh codespace cp -r . '{repo_name}':/workspaces/ "
                            f"&& gh codespace ssh -c 'cd /workspaces/{repo_name} && "
                            "if [ -f requirements.txt ]; then pip install -r requirements.txt; fi && "
                            "if [ -f setup.sh ]; then chmod +x setup.sh && ./setup.sh; fi'"
                        )
                    }
                ]
            }
        }
    }

    file_name = f"codespace_setup_{repo_name.lower()}.yml"
    
    with open(file_name, 'w') as file:
        yaml.dump(workflow, file, sort_keys=False, default_flow_style=False)
    
    print(f"✅ Generated GitHub Action: {file_name}")
    print(f"👉 Note: Ensure you have a 'CODESPACE_TOKEN' secret in your repository.")

if __name__ == "__main__":
    target_repo = "https://github.com/firmao/codemeta-ro-crate-vm.git"
    generate_codespace_workflow(target_repo)