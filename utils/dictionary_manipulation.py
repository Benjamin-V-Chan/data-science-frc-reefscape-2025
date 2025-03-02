import json

def retrieve_json(json_path):
    with open(json_path) as json_file:
        return json.load(json_file)


def single_dict(dictionary):
    if not isinstance(dictionary, dict):
        return False
    for key in dictionary:
        if isinstance(dictionary[key], dict):
            return False
    return True

def flatten_vars_in_dict(dictionary, return_dict=None, prefix=""):
    """Flattens only variable names but keeps their properties (statistical_data_type, values) intact."""
    if return_dict is None:
        return_dict = {}

    for key, value in dictionary.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict) and "statistical_data_type" not in value:
            # If the dictionary does NOT contain a 'statistical_data_type' key, keep flattening
            flatten_vars_in_dict(value, return_dict, full_key)
        else:
            # If we hit the final structure (statistical data type exists), store as-is
            return_dict[full_key] = value

    return return_dict
