import json


def load_config(file_path):
    try:
        with open(file_path, "r") as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        exit(1)
    except json.JSONDecodeError:
        print(
            f"Error: Failed to decode JSON from the file {file_path}. Please check the file format."
        )
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)


# Load the configuration from the layout.json file
base = load_config("layout.json")
