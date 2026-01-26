# Bridging the Metadata Gap: Automated VRE Provisioning via Agentic AI and CodeMeta Knowledge Graphs

## Abstract
Virtual Research Environments (VREs) are essential for modern data-driven research, yet the manual overhead of configuring these environments remains a significant barrier for researchers in the Social Sciences and Humanities (SSH). This paper proposes a framework within the Macroscope project to automate VRE setup by leveraging Agentic AI for metadata generation. By populating a Knowledge Graph with CodeMeta descriptions generated automatically from software repositories, we enable a machine-readable pipeline that bridges the gap between raw data access and functional, containerized research environments.

<img width="1354" height="792" alt="image" src="https://github.com/user-attachments/assets/68db96af-450c-4a53-9e5b-a796d0f04cb2" />

## Question we try to solve:
- Which tools and versions can manipulate my specific data?
- Are the software licenses compatible with my research stack and institutional requirements?
- What are the specific operating system, memory, and CPU requirements?
- Where is the documentation, and how should packages be sequenced during installation?
- Is there a citable publication or an ORCID associated with the authors?

# How to run

Install Multipass to create your VMs locally (Experiments with Macbook):
- `brew install --cask multipass`

Install PyYAML: You'll need this for the Python script to read your configuration. 
- `pip install pyyaml`

Execution
- `python run_vm.py`

# How it Works
The script leverages the macOS Hypervisor through Multipass. Here is a high-level look at how the layers interact:
- **YAML Parsing**: The script uses PyYAML to turn your human-readable settings into a Python dictionary.
- **Resource Allocation**: It maps the cpus, memory, and disk keys directly to the command-line arguments that Multipass requires.
- **Cloud-Init**: If you want the VM to come pre-installed with software (like Git or Docker), the cloud_init section handles that automatically upon the first boot.
- **Native Performance**: Because it uses Virtualization.framework (on Apple Silicon or Intel), there is very little overhead compared to heavier tools like VirtualBox.

## Useful Management VM multipass Commands
Once your script has started the VM, you can manage it from your terminal, here some useful commands:
- **Enter the VM**	`multipass shell mac-dev-box`
- **Check Status**	`multipass list`
- **Stop the VM**	`multipass stop mac-dev-box`
- **Delete the VM** `multipass delete --purge mac-dev-box`

# Ro-Crate experiments
**run_vm_rocrate.py** creates a **ro-crate-metadata.yaml** file and runs a VM configured by it.

You can use this ro-crate file to create a vm in other environments, no need to be multipass on a MacBook.
