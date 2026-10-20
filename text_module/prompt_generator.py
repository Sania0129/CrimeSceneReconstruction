import json


def generate_image_prompt(scene):

    crime_type = scene.get("crime_type", "crime scene")

    location = ", ".join(scene.get("location", []))

    time = ", ".join(scene.get("time", []))

    people = ", ".join(scene.get("people", []))

    actions = []

    for category, action_list in scene.get("actions", {}).items():
        actions.extend(action_list)

    actions_text = ", ".join(actions)

    objects = []

    for category, object_list in scene.get("objects", {}).items():
        objects.extend(object_list)

    objects_text = ", ".join(objects)

    prompt = (
        f"A realistic forensic reconstruction of a {crime_type}. "
        f"The scene is located in {location if location else 'an unidentified location'}. "
        f"The incident occurred during {time if time else 'an unspecified time'}. "
        f"People present: {people if people else 'unspecified people'}. "
        f"Objects present: {objects_text if objects_text else 'relevant crime-scene objects'}. "
        f"Actions involved: {actions_text if actions_text else 'an unspecified criminal action'}. "
        f"Detailed environment, realistic lighting, accurate spatial arrangement, "
        f"forensic crime-scene reconstruction style."
    )

    return prompt


# Load the structured crime information
with open("crime_output.json", "r") as file:

    scene_data = json.load(file)


# Generate image prompt
image_prompt = generate_image_prompt(scene_data)


print("\nGenerated Image Prompt")
print("----------------------")
print(image_prompt)