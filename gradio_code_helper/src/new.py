```python
import yaml
from gin.gen.util import ref_resolver

"""
Helper functions
"""

def load_openapi_spec(file_path):
    """
    Load YAML file and safely deserialize it into a Python dictionary.

    Args:
        file_path (str): The path to the YAML file.

    Returns:
        dict: The deserialized YAML data.
    """
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return {}
    except yaml.YAMLError as e:
        print(f"Error: Unable to load YAML from {file_path}. Error: {e}")
        return None

def parse_endpoints(openapi_spec, instructions):
    """
    Extract needed endpoints data from the OpenAPI spec to create an operational FastAPI application.

    Args:
        openapi_spec (dict): The deserialized OpenAPI specification.
        instructions (dict): A dictionary containing SFDP endpoint instructions.

    Returns:
        list: A list of dictionaries representing the endpoints with their details.
    """
    try:
        paths = openapi_spec.get("paths", {})
    except AttributeError:
        print(f"Error: The input 'openapi_spec' does not contain a 'paths' key.")
        return []

    endpoints = []

    for path, methods in paths.items():
        sfdp_endpoint_name = ""

        # Process SFDP endpoint instructions
        for instruction in instructions["sfdp_endpoints"]:
            for key, content in instruction.items():
                if "fdp_path" in content and content["fdp_path"] == path:
                    sfdp_endpoint_name = key

                if "sfdp_path" in content and content["sfdp_path"] == path:
                    sfdp_endpoint_path = content["sfdp_path"]

        for method, details in methods.items():
            parameters = [
                {
                    "name": param["name"],
                    "in": param["in"],
                    "type": param["schema"]["type"],
                    "nullable": param["schema"].get("nullable", False),
                }
                for param in details.get("parameters", [])
            ]

            response_model_spec = {}

            if "$ref" in details["responses"]["200"]["content"]["application/json"][
                "schema"
            ]:
                response_ref = details["responses"]["200"]["content"]["application/json"][
                    "schema"
                ]["$ref"]
                response_model_name = response_ref.split("/")[-1]

                # Resolve the reference for the response model
                response_model_spec = ref_resolver.resolve_ref_for_object(
                    openapi_spec, openapi_spec["components"]["schemas"][response_model_name]
                )

            if "properties" in response_model_spec:
                if sfdp_endpoint_name != "":
                    endpoints.append(
                        {
                            "method": method,
                            "path": path,
                            "sfdp_endpoint_name": sfdp_endpoint_name,
                            "sfdp_endpoint_path": sfdp_endpoint_path,
                            "name": details["operationId"],
                            "parameters": parameters,
                            "description": details.get("description", ""),
                            "response_model": {
                                "name": response_model_name,
                                "properties": response_model_spec["properties"],
                            },
                        }
                    )
            else:
                if sfdp_endpoint_name != "":
                    endpoints.append(
                        {
                            "method": method,
                            "path": path,
                            "sfdp_endpoint_name": sfdp_endpoint_name,
                            "sfdp_endpoint_path": sfdp_endpoint_path,
                            "name": details["operationId"],
                            "parameters": parameters,
                            "description": details.get("description", ""),
                            "response_model": {
                                "name": response_model_name,
                                "properties": response_model_spec,
                            },
                        }
                    )

    return endpoints
```