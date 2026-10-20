import json


def create_flux_prompt(fused_scene):

    crime_type = fused_scene.get("crime_type", "crime scene")

    location = ", ".join(
        fused_scene.get("location", [])
    )

    time = ", ".join(
        fused_scene.get("time", [])
    )

    people = ", ".join(
        fused_scene.get("people", [])
    )

    # Objects from text
    text_objects = []

    for values in fused_scene.get("text_objects", {}).values():
        if isinstance(values, list):
            text_objects.extend(values)

    # Objects from image
    image_objects = fused_scene.get(
        "image_objects", []
    )

    # Combine objects and remove duplicates
    all_objects = list(
        dict.fromkeys(
            text_objects + image_objects
        )
    )

    # Actions from text
    actions = []

    for values in fused_scene.get("actions", {}).values():
        if isinstance(values, list):
            actions.extend(values)

    # Create final FLUX prompt
    prompt = (
        f"Realistic forensic reconstruction of a "
        f"{crime_type}. "

        f"Location: "
        f"{location if location else 'unspecified'}. "

        f"Time: "
        f"{time if time else 'unspecified'}. "

        f"People: "
        f"{people if people else 'unspecified'}. "

        f"Objects detected from text and image: "
        f"{', '.join(all_objects) if all_objects else 'unspecified'}. "

        f"Actions: "
        f"{', '.join(actions) if actions else 'unspecified'}. "

        f"Create a realistic crime scene with "
        f"accurate spatial arrangement, "
        f"realistic environment, "
        f"realistic lighting, "
        f"and forensic reconstruction style."
    )

    return prompt


if __name__ == "__main__":

    # Read fused scene information
    with open(
        "../fusion_module/fused_scene.json",
        "r"
    ) as file:

        fused_scene = json.load(file)

    # Generate FLUX prompt
    final_prompt = create_flux_prompt(
        fused_scene
    )

    print("\nFINAL FLUX PROMPT")
    print("-----------------")
    print(final_prompt)