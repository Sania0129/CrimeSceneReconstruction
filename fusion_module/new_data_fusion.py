import json
import os
import re


# =====================================================
# OBJECT NORMALIZATION
# =====================================================

def normalize_object_name(name):
    """
    Normalize object names so that simple naming variations
    can still be compared during text-image fusion.
    """

    if not name:
        return ""

    name = str(name).strip().lower()

    # Remove common articles
    name = re.sub(
        r"^(a|an|the)\s+",
        "",
        name
    )

    # Normalize spaces
    name = re.sub(
        r"\s+",
        " ",
        name
    )

    # Simple equivalent terms
    aliases = {
        "hand gun": "handgun",
        "pistol": "handgun",
        "automobile": "car",
        "vehicle": "car",
        "motorbike": "motorcycle",
        "bike": "motorcycle"
    }

    return aliases.get(
        name,
        name
    )


# =====================================================
# CLEAN OBJECT LIST
# =====================================================

def clean_object_list(objects):

    cleaned = []

    if not isinstance(objects, list):
        return cleaned

    for obj in objects:

        if not obj:
            continue

        obj = str(obj).strip().lower()

        if obj and obj not in cleaned:
            cleaned.append(obj)

    return cleaned


# =====================================================
# FIND COMMON OBJECTS
# =====================================================

def find_common_objects(
    text_objects,
    image_objects
):

    common_objects = []

    image_normalized = {
        normalize_object_name(obj): obj
        for obj in image_objects
    }

    for text_obj in text_objects:

        normalized_text = normalize_object_name(
            text_obj
        )

        if normalized_text in image_normalized:

            add_value = text_obj

            if add_value not in common_objects:
                common_objects.append(
                    add_value
                )

    return common_objects


# =====================================================
# FIND TEXT-ONLY OBJECTS
# =====================================================

def find_text_only_objects(
    text_objects,
    image_objects
):

    text_only_objects = []

    image_normalized = {
        normalize_object_name(obj)
        for obj in image_objects
    }

    for text_obj in text_objects:

        normalized_text = normalize_object_name(
            text_obj
        )

        if normalized_text not in image_normalized:

            if text_obj not in text_only_objects:

                text_only_objects.append(
                    text_obj
                )

    return text_only_objects


# =====================================================
# FIND IMAGE-ONLY OBJECTS
# =====================================================

def find_image_only_objects(
    text_objects,
    image_objects
):

    image_only_objects = []

    text_normalized = {
        normalize_object_name(obj)
        for obj in text_objects
    }

    for image_obj in image_objects:

        normalized_image = normalize_object_name(
            image_obj
        )

        if normalized_image not in text_normalized:

            if image_obj not in image_only_objects:

                image_only_objects.append(
                    image_obj
                )

    return image_only_objects


# =====================================================
# BUILD VISUAL CONTEXT
# =====================================================

def build_visual_context(
    image_objects,
    common_objects,
    image_only_objects
):

    visual_context = []

    # Objects detected by both sources
    for obj in common_objects:

        visual_context.append(
            {
                "object": obj,
                "source": "text_and_image",
                "status": "supported_by_both_sources"
            }
        )

    # Objects detected only by image
    for obj in image_only_objects:

        visual_context.append(
            {
                "object": obj,
                "source": "image",
                "status": "visual_context_only"
            }
        )

    return visual_context


# =====================================================
# BUILD SCENE CONTEXT
# =====================================================

def build_scene_context(
    text_scene,
    common_objects,
    text_only_objects,
    image_only_objects
):

    scene_context = {

        "primary_event":
            text_scene.get(
                "event",
                []
            ),

        "time":
            text_scene.get(
                "time",
                []
            ),

        "locations":
            text_scene.get(
                "locations",
                []
            ),

        "people":
            text_scene.get(
                "people",
                []
            ),

        "actions":
            text_scene.get(
                "actions",
                []
            ),

        "conditions":
            text_scene.get(
                "conditions",
                []
            ),

        "evidence":
            text_scene.get(
                "evidence",
                []
            ),

        "relationships":
            text_scene.get(
                "relationships",
                []
            ),

        "crime_description":
            text_scene.get(
                "description",
                text_scene.get(
                    "original_description",
                    ""
                )
            ),

        "described_objects":
            text_scene.get(
                "objects",
                []
            ),

        "objects_supported_by_image":
            common_objects,

        "objects_described_but_not_detected":
            text_only_objects,

        "visual_context_objects":
            image_only_objects
    }

    return scene_context


# =====================================================
# MAIN DATA FUSION
# =====================================================

def perform_new_data_fusion():

    # =============================================
    # FILE PATHS
    # =============================================

    text_file = (
        "../text_module/"
        "scene_understanding_output.json"
    )

    image_file = (
        "../image_module/"
        "image_scene_output.json"
    )

    output_file = (
        "../fusion_module/"
        "fused_scene.json"
    )


    # =============================================
    # CHECK INPUT FILES
    # =============================================

    if not os.path.exists(text_file):

        print(
            "Text scene file not found:"
        )

        print(text_file)

        return


    if not os.path.exists(image_file):

        print(
            "Image scene file not found:"
        )

        print(image_file)

        return


    # =============================================
    # LOAD TEXT INFORMATION
    # =============================================

    with open(
        text_file,
        "r"
    ) as file:

        text_scene = json.load(file)


    # =============================================
    # LOAD IMAGE INFORMATION
    # =============================================

    with open(
        image_file,
        "r"
    ) as file:

        image_scene = json.load(file)


    # =============================================
    # GET TEXT OBJECTS
    # =============================================

    text_objects = clean_object_list(
        text_scene.get(
            "objects",
            []
        )
    )


    # =============================================
    # GET IMAGE OBJECTS
    # =============================================

    image_objects = clean_object_list(
        image_scene.get(
            "detected_objects",
            []
        )
    )


    # =============================================
    # OBJECT FUSION
    # =============================================

    common_objects = find_common_objects(
        text_objects,
        image_objects
    )

    text_only_objects = find_text_only_objects(
        text_objects,
        image_objects
    )

    image_only_objects = find_image_only_objects(
        text_objects,
        image_objects
    )


    # =============================================
    # VISUAL CONTEXT
    # =============================================

    visual_context = build_visual_context(
        image_objects,
        common_objects,
        image_only_objects
    )


    # =============================================
    # SCENE CONTEXT
    # =============================================

    scene_context = build_scene_context(
        text_scene,
        common_objects,
        text_only_objects,
        image_only_objects
    )


    # =============================================
    # CREATE FUSED SCENE
    # =============================================

    fused_scene = {

        # -----------------------------------------
        # Original information
        # -----------------------------------------

        "original_description":
            text_scene.get(
                "description",
                text_scene.get(
                    "original_description",
                    ""
                )
            ),

        "scene_summary":
            text_scene.get(
                "scene_summary",
                ""
            ),

        # -----------------------------------------
        # Main scene information
        # -----------------------------------------

        "event":
            text_scene.get(
                "event",
                []
            ),

        "time":
            text_scene.get(
                "time",
                []
            ),

        "people":
            text_scene.get(
                "people",
                []
            ),

        "locations":
            text_scene.get(
                "locations",
                []
            ),

        "actions":
            text_scene.get(
                "actions",
                []
            ),

        "conditions":
            text_scene.get(
                "conditions",
                []
            ),

        "evidence":
            text_scene.get(
                "evidence",
                []
            ),

        "relationships":
            text_scene.get(
                "relationships",
                []
            ),

        # -----------------------------------------
        # Object information
        # -----------------------------------------

        "text_objects":
            text_objects,

        "image_objects":
            image_objects,

        "common_objects":
            common_objects,

        "text_only_objects":
            text_only_objects,

        "image_only_objects":
            image_only_objects,

        # -----------------------------------------
        # Visual context
        # -----------------------------------------

        "visual_context":
            visual_context,

        # -----------------------------------------
        # Structured scene context
        # -----------------------------------------

        "scene_context":
            scene_context,

        # -----------------------------------------
        # Image information
        # -----------------------------------------

        "image_name":
            image_scene.get(
                "image_name",
                ""
            )
    }


    # =============================================
    # SAVE FUSED SCENE
    # =============================================

    with open(
        output_file,
        "w"
    ) as file:

        json.dump(
            fused_scene,
            file,
            indent=4
        )


    # =============================================
    # DISPLAY FUSION RESULT
    # =============================================

    print("\n==========================================")
    print("        UPGRADED DATA FUSION")
    print("==========================================")


    print("\nEvent:")
    print(
        fused_scene["event"]
    )


    print("\nTime:")
    print(
        fused_scene["time"]
    )


    print("\nPeople:")
    print(
        fused_scene["people"]
    )


    print("\nLocations:")
    print(
        fused_scene["locations"]
    )


    print("\nActions:")
    print(
        fused_scene["actions"]
    )


    print("\nConditions:")
    print(
        fused_scene["conditions"]
    )


    print("\nEvidence:")
    print(
        fused_scene["evidence"]
    )


    print("\nText Objects:")
    print(
        fused_scene["text_objects"]
    )


    print("\nImage Objects:")
    print(
        fused_scene["image_objects"]
    )


    print("\nCommon Objects:")
    print(
        fused_scene["common_objects"]
    )


    print("\nText-Only Objects:")
    print(
        fused_scene["text_only_objects"]
    )


    print("\nImage-Only Objects:")
    print(
        fused_scene["image_only_objects"]
    )


    print("\nVisual Context:")
    print(
        fused_scene["visual_context"]
    )


    print("\nScene Context:")
    print(
        json.dumps(
            fused_scene["scene_context"],
            indent=4
        )
    )


    print(
        "\nFused scene saved to:"
    )

    print(output_file)

    print(
        "\n=========================================="
    )

    print(
        "       DATA FUSION COMPLETED"
    )

    print(
        "=========================================="
    )


# =============================================
# MAIN PROGRAM
# =============================================

if __name__ == "__main__":

    perform_new_data_fusion()