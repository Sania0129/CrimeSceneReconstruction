from ultralytics import YOLO
import json
import os


# Load pretrained YOLO model
model = YOLO("yolo11n.pt")


def process_image(image_path):

    if not os.path.exists(image_path):
        print("Image file not found:", image_path)
        return []

    print("Processing image...")
    print("Image:", image_path)

    results = model(image_path)

    detected_objects = []

    for result in results:

        for box in result.boxes:

            class_id = int(box.cls[0])
            object_name = model.names[class_id]

            if object_name not in detected_objects:
                detected_objects.append(object_name)

    print("\nDetected Objects:")
    print(detected_objects)

    # Save image processing result
    output = {
        "image_name": os.path.basename(image_path),
        "detected_objects": detected_objects
    }

    # Save output inside image_module
    output_file = os.path.join(
        os.path.dirname(__file__),
        "image_scene_output.json"
    )

    with open(output_file, "w") as file:
        json.dump(output, file, indent=4)

    print("\nImage scene information saved successfully!")

    return detected_objects


if __name__ == "__main__":

    image_path = input("Enter image path: ")

    process_image(image_path)