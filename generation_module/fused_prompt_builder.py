
import json


def clean_list(items, excluded_terms=None):
    if not items:
        return []

    excluded_terms = excluded_terms or []
    cleaned = []

    for item in items:
        item = str(item).strip()

        if not item:
            continue

        item_lower = item.lower()

        if any(
            excluded.lower() in item_lower
            for excluded in excluded_terms
        ):
            continue

        if item not in cleaned:
            cleaned.append(item)

    return cleaned


def create_fused_prompt(scene):

    # =====================================================
    # EXTRACT BASIC SCENE INFORMATION
    # =====================================================

    event = clean_list(scene.get("event", []))
    time = clean_list(scene.get("time", []))
    people = clean_list(scene.get("people", []))
    locations = clean_list(scene.get("locations", []))
    actions = clean_list(scene.get("actions", []))
    conditions = clean_list(scene.get("conditions", []))
    evidence = clean_list(scene.get("evidence", []))

    relationships = scene.get("relationships", [])
    scene_context = scene.get("scene_context", {})
    visual_context = scene.get("visual_context", [])

    if not isinstance(scene_context, dict):
        scene_context = {}

    # =====================================================
    # CLEAN OBJECTS FROM TEXT AND IMAGE PROCESSING
    # =====================================================

    object_noise = [
        "murder",
        "attack",
        "crime",
        "altercation",
        "location",
        "police",
        "evidence",
        "investigation",
        "part",
        "public area",
        "public street area",
        "nearby buildings",
        "shahbad",
        "dairy"
    ]

    text_objects = clean_list(
        scene.get("text_objects", []),
        object_noise
    )

    common_objects = clean_list(
        scene.get("common_objects", []),
        object_noise
    )

    text_only_objects = clean_list(
        scene.get("text_only_objects", []),
        object_noise
    )

    image_only_objects = clean_list(
        scene.get("image_only_objects", []),
        object_noise
    )

    # =====================================================
    # EXTRACT OBJECTS AND DETAILS FROM IMAGE CONTEXT
    # =====================================================

    visual_objects = []
    visual_details = []

    if isinstance(visual_context, list):
        for item in visual_context:

            if isinstance(item, dict):
                object_name = item.get("object")

                if object_name:
                    object_name = str(object_name).strip()

                    if object_name and object_name not in visual_objects:
                        visual_objects.append(object_name)

                # Preserve additional information if available.
                for key in [
                    "description",
                    "position",
                    "location",
                    "attributes"
                ]:
                    value = item.get(key)

                    if value:
                        if isinstance(value, (list, dict)):
                            value = json.dumps(value)

                        visual_details.append(
                            f"{key}: {value}"
                        )

            elif isinstance(item, str) and item.strip():
                visual_objects.append(item.strip())

    visual_objects = clean_list(
        visual_objects,
        object_noise
    )

    visual_details = clean_list(visual_details)

    # =====================================================
    # COMBINE TEXT AND IMAGE OBJECTS
    # =====================================================

    combined_objects = clean_list(
        text_objects
        + common_objects
        + text_only_objects
        + image_only_objects
        + visual_objects,
        object_noise
    )

    combined_objects_text = (
        ", ".join(combined_objects)
        if combined_objects
        else "No specific objects supplied by the processing modules"
    )

    text_objects_text = (
        ", ".join(text_objects)
        if text_objects
        else "None identified from text"
    )

    image_objects_text = (
        ", ".join(
            clean_list(image_only_objects + visual_objects, object_noise)
        )
        if image_only_objects or visual_objects
        else "None supplied by image processing"
    )

    visual_details_text = (
        "; ".join(visual_details)
        if visual_details
        else "No additional visual details supplied"
    )

    # =====================================================
    # PRIMARY EVENT
    # =====================================================

    primary_event = scene_context.get(
        "primary_event",
        event
    )

    if isinstance(primary_event, list):
        primary_event = ", ".join(clean_list(primary_event))
    else:
        primary_event = str(primary_event or "").strip()

    if not primary_event:
        primary_event = (
            ", ".join(event)
            if event
            else "Crime scene reconstruction"
        )

    # =====================================================
    # ACTIONS
    # =====================================================

    non_visual_actions = [
        "occur",
        "examine",
        "collect",
        "find",
        "investigate"
    ]

    visual_actions = clean_list(
        actions,
        non_visual_actions
    )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    relationship_text = []

    if isinstance(relationships, list):
        for relationship in relationships:

            if not isinstance(relationship, dict):
                continue

            subject = relationship.get("subject")
            action = relationship.get("action")
            obj = relationship.get("object")

            if not action:
                continue

            if str(action).lower() in [
                "examine",
                "collect",
                "investigate"
            ]:
                continue

            if subject and obj:
                relationship_text.append(
                    f"{subject} {action} {obj}"
                )
            elif subject:
                relationship_text.append(
                    f"{subject} {action}"
                )

    # =====================================================
    # FORMATTED VALUES
    # =====================================================

    event_text = ", ".join(event) if event else primary_event
    people_text = ", ".join(people) if people else "Not specified"
    location_text = ", ".join(locations) if locations else "Not specified"
    time_text = ", ".join(time) if time else "Not specified"

    action_text = (
        ", ".join(visual_actions)
        if visual_actions
        else "No specific actions supplied"
    )

    evidence_text = (
        ", ".join(evidence)
        if evidence
        else "No specific forensic evidence supplied"
    )

    condition_text = (
        ", ".join(conditions)
        if conditions
        else "No specific scene conditions supplied"
    )

    relationship_text_final = (
        "; ".join(relationship_text)
        if relationship_text
        else "No explicit physical relationships supplied"
    )

    # =====================================================
    # EVENT-SPECIFIC VISUAL GUIDANCE
    # =====================================================

    event_lower = f"{event_text} {primary_event}".lower()

    if any(word in event_lower for word in [
        "murder", "homicide", "killing", "attack", "assault"
    ]):
        event_guidance = """
Show the described incident as the main visual focus.
Represent people and their positions only when supported by
the supplied information. Use a non-graphic forensic style.
Do not invent a suspect, weapon, injury, or attack in progress.
"""

    elif any(word in event_lower for word in [
        "theft", "robbery", "burglary", "stealing"
    ]):
        event_guidance = """
Make the described theft or burglary visually clear.
Show supported actions, relevant property, and entry or exit
points when specified. Do not invent weapons, extra suspects,
or unsupported actions.
"""

    elif any(word in event_lower for word in [
        "accident", "collision", "crash"
    ]):
        event_guidance = """
Clearly represent the described accident and the positions
of the involved vehicles or people. Do not invent additional
vehicles, damage, injuries, or events.
"""

    else:
        event_guidance = """
Make the specified incident the main visual focus.
Represent supported people, actions, objects, and relationships.
Do not substitute generic scenery for the described event.
"""

    # =====================================================
    # FINAL FUSED IMAGE PROMPT
    # =====================================================

    prompt = f"""
CRIME SCENE RECONSTRUCTION

TASK:
Generate a realistic, non-graphic forensic visualization using
the written incident description and supplied reference image.

CRIME OR INCIDENT:
{event_text}

PRIMARY EVENT:
{primary_event}

LOCATION:
{location_text}

TIME:
{time_text}

PEOPLE FROM TEXT ANALYSIS:
{people_text}

ACTIONS FROM TEXT ANALYSIS:
{action_text}

OBJECTS FROM TEXT ANALYSIS:
{text_objects_text}

OBJECTS FROM IMAGE ANALYSIS:
{image_objects_text}

COMBINED OBJECT LIST:
{combined_objects_text}

ADDITIONAL IMAGE DETAILS:
{visual_details_text}

FORENSIC EVIDENCE:
{evidence_text}

SCENE CONDITIONS:
{condition_text}

PHYSICAL RELATIONSHIPS:
{relationship_text_final}

EVENT REQUIREMENTS:
{event_guidance}

REFERENCE IMAGE INSTRUCTIONS:
Use the uploaded photograph as the visual starting point.
Preserve its recognizable environment, architecture,
background, perspective, and major spatial layout where possible.

Use the written incident description to guide the changes
needed to represent the described event.

Retain relevant objects visible in the original image when
possible. Do not treat an object's presence as proof that it
was involved in the crime.

Do not force objects from the text into the scene if doing so
would contradict the supplied photograph. Represent important
described objects where visually plausible.

COMPOSITION:
Keep the main incident and relevant people visible.
Show meaningful spatial relationships between people and objects.
Include entry and exit points when supported by the inputs.
Avoid replacing the incident with generic scenery.

VISUAL STYLE:
Photorealistic documentary photography, realistic proportions,
believable poses, natural lighting, and clear composition.
Non-graphic forensic presentation.

STRICT CONSTRAINTS:
Do not invent unsupported people, weapons, injuries, actions,
or evidence. Do not add text or watermarks.
This is an AI-generated visualization, not verified evidence.
"""

    return prompt.strip()


# =====================================================
# MAIN PROGRAM
# =====================================================

if __name__ == "__main__":

    input_path = "../fusion_module/fused_scene.json"

    with open(input_path, "r", encoding="utf-8") as file:
        fused_scene = json.load(file)

    final_prompt = create_fused_prompt(fused_scene)

    print("\n==========================================")
    print("          CLEAN FUSED FLUX PROMPT")
    print("==========================================\n")
    print(final_prompt)

    output_path = "final_fused_prompt.txt"

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(final_prompt)

    print(f"\nPrompt saved to {output_path}")
    print("\nPROMPT BUILDER COMPLETED")
