import json

from text_processor import create_scene_representation


# Load test cases
with open("test_cases.json", "r") as file:
    data = json.load(file)


# Process every test case
for test_case in data["test_cases"]:

    print("\n===================================")
    print("Test Case:", test_case["id"])
    print("Expected Crime:", test_case["crime"])
    print("===================================")

    description = test_case["description"]

    result = create_scene_representation(description)

    print("Detected Crime:", result["crime_type"])
    print("Location:", result["location"])
    print("Time:", result["time"])
    print("People:", result["people"])
    print("Objects:", result["objects"])
    print("Actions:", result["actions"])