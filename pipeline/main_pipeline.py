import sys
import os
import json

# Add project module paths
sys.path.append("../text_module")
sys.path.append("../image_module")
sys.path.append("../fusion_module")
sys.path.append("../generation_module")

from scene_understanding import understand_scene
from image_processor import process_image
from new_data_fusion import perform_new_data_fusion
from fused_prompt_builder import create_fused_prompt


def run_pipeline(crime_description, image_path):

    print("\n==========================================")
    print("     CRIME SCENE RECONSTRUCTION SYSTEM")
    print("==========================================")

    # -----------------------------------------
    # STEP 1: TEXT PROCESSING
    # -----------------------------------------
    print("\n[1] TEXT SCENE UNDERSTANDING")
    print("------------------------------------------")

    scene = understand_scene(crime_description)

    print("Event:", scene["event"])
    print("Time:", scene["time"])
    print("People:", scene["people"])
    print("Locations:", scene["locations"])
    print("Objects:", scene["objects"])
    print("Actions:", scene["actions"])
    print("Conditions:", scene["conditions"])
    print("Evidence:", scene["evidence"])
    print("Relationships:", scene["relationships"])

    text_output = "../text_module/scene_understanding_output.json"

    with open(text_output, "w") as file:
        json.dump(scene, file, indent=4)

    print("\nText scene information saved.")


    # -----------------------------------------
    # STEP 2: IMAGE PROCESSING
    # -----------------------------------------
    print("\n[2] IMAGE PROCESSING")
    print("------------------------------------------")

    detected_objects = process_image(image_path)

    print("Detected image objects:")
    print(detected_objects)


    # -----------------------------------------
    # STEP 3: DATA FUSION
    # -----------------------------------------
    print("\n[3] DATA FUSION")
    print("------------------------------------------")

    perform_new_data_fusion()

    fusion_file = "../fusion_module/fused_scene.json"

    if not os.path.exists(fusion_file):
        print("\nERROR: fused_scene.json was not created.")
        return

    print("\nText and image information successfully fused.")


    # -----------------------------------------
    # STEP 4: FLUX PROMPT GENERATION
    # -----------------------------------------
    print("\n[4] FLUX PROMPT GENERATION")
    print("------------------------------------------")

    with open(fusion_file, "r") as file:
        fused_scene = json.load(file)

    final_prompt = create_fused_prompt(fused_scene)

    print("\nFINAL FLUX PROMPT")
    print("------------------------------------------")
    print(final_prompt)


    prompt_file = "../generation_module/final_fused_prompt.txt"

    with open(prompt_file, "w") as file:
        file.write(final_prompt)

    print("\nFinal FLUX prompt saved successfully.")
    print("File:", prompt_file)


    # -----------------------------------------
    # PIPELINE COMPLETE
    # -----------------------------------------
    print("\n==========================================")
    print("        LOCAL PIPELINE COMPLETED")
    print("==========================================")

    print("\nReady for FLUX.1-dev generation when GPU is available.")


if __name__ == "__main__":

    crime_description = input(
        "\nEnter crime scene description:\n"
    )

    image_path = input(
        "\nEnter image path:\n"
    )

    run_pipeline(crime_description, image_path)