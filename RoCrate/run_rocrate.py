import boto3
from rocrate.rocrate import ROCrate
import base64

def deploy_vm_from_crate(crate_path):
    # 1. Load the RO-Crate
    crate = ROCrate(crate_path)
    print(f"--- Loading Crate: {crate.name} ---")

    # 2. Find the YAML configuration file
    # We look for the entity that is marked as SoftwareSourceCode
    vm_config_file = None
    for entity in crate.get_entities():
        if "SoftwareSourceCode" in entity.type and entity.id.endswith('.yaml'):
            vm_config_file = entity
            break
    
    if not vm_config_file:
        raise FileNotFoundError("Could not find a YAML configuration file in the RO-Crate.")

    # 3. Read the YAML content
    # Note: .id refers to the local path within the crate folder
    config_path = f"{crate_path}/{vm_config_file.id}"
    with open(config_path, 'r') as f:
        user_data_script = f.read()

    print(f"Deploying VM with config: {vm_config_file.id}")

    # 4. Provision the VM via AWS Boto3
    ec2 = boto3.resource('ec2', region_name='us-east-1')
    
    instances = ec2.create_instances(
        ImageId='ami-0c55b159cbfafe1f0', # Replace with a valid Ubuntu AMI for your region
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        UserData=user_data_script, # This is where the YAML goes!
        KeyName='my-key-pair'      # Ensure this key exists in your AWS account
    )

    print(f"Success! Instance created: {instances[0].id}")
    return instances[0].id

# Run the deployment
# deploy_vm_from_crate('./my-vm-crate')