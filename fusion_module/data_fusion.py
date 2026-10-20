import json
import os


def perform_data_fusion(text_file, image_file):

    # Check whether files exist
    if not os.path.exists(text_file):
        print("Text scene file not found:", text_file)
        return

    if not os.path.exists(image_file):
        print("Image scene file not found:", image_file)
        return

    # Read text processing output
    with open(text_file, "r") as file:
        text_scene = json.load(file)

    # Read image processing output
    with open(image_file, "r") as file:
        image_scene = json.load(file)

    # Combine information
    fused_scene = {
        "crime_type": text_scene.get("crime_type"),
        "location": text_scene.get("location"),
        "time": text_scene.get("time"),
        "people": text_scene.get("people"),
        "text_objects": text_scene.get("objects"),
        "actions": text_scene.get("actions"),
        "image_objects": image_scene.get("detected_objects"),
        "original_description": text_scene.get("original_description"),
        "image_name": image_scene.get("image_name")
    }

    # Save fused information inside fusion_module
    output_file = os.path.join(
        os.path.dirname(__file__),
        "fused_scene.json"
    )

    with open(output_file, "w") as file:
        json.dump(fused_scene, file, indent=4)

    print("\nData fusion completed successfully!")

    print("\nFused Crime Scene Information")
    print("-----------------------------")
    print(json.dumps(fused_scene, indent=4))


if __name__ == "__main__":

    text_file = "../text_module/crime_output.json"
    image_file = "../image_module/image_scene_output.json"

    perform_data_fusion(
        text_file,
        image_file
    )