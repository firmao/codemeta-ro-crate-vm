import json
import yaml
import os

def convert_json_to_yaml(input_file='code-meta.jsonld', output_file='code-meta.yaml'):
    # Check if the source file exists
    if not os.path.exists(input_file):
        print(f"Error: The file '{input_file}' was not found.")
        return

    try:
        # Load the JSON data
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Write the YAML data
        with open(output_file, 'w', encoding='utf-8') as f:
            # sort_keys=False preserves the original order of the JSON
            # default_flow_style=False ensures a clean, block-style YAML
            yaml.dump(data, f, sort_keys=False, default_flow_style=False, allow_unicode=True)

        print(f"Success! '{input_file}' has been converted to '{output_file}'.")

    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    convert_json_to_yaml()