# saneVM
SANE VM test in the script [simplevm.yml](https://github.com/firmao/saneVM/blob/main/simplevm.yml)

Prerequisites for the script [vmlaunch.py](https://github.com/firmao/saneVM/blob/main/vmlaunch.py)

To ensure the script runs successfully, you'll need the following installed on your host machine:

- Python Libraries: You'll need PyYAML.

-- pip install pyyaml

- VM Hypervisor (Multipass):

-- macOS: brew install --cask multipass

-- Windows: Download the installer

-- Linux: sudo snap install multipass

Customizing for Cloud Providers
If you prefer to launch this on a public cloud (like AWS), please, swap the subprocess call from multipass to the Boto3 library (for AWS) or a Terraform command.
