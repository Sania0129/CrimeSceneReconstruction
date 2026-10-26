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
            excluded in item_lower
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

    event = clean_list(
        scene.get("event", [])
    )

    time = clean_list(
        scene.get("time", [])
    )

    people = clean_list(
        scene.get("people", [])
    )

    locations = clean_list(
        scene.get("locations", [])
    )

    actions = clean_list(
        scene.get("actions", [])
    )

    conditions = clean_list(
        scene.get("conditions", [])
    )

    evidence = clean_list(
        scene.get("evidence", [])
    )

    relationships = scene.get(
        "relationships",
        []
    )

    scene_context = scene.get(
        "scene_context",
        {}
    )

    visual_context = scene.get(
        "visual_context",
        []
    )


    # =====================================================
    # REMOVE NLP NOISE FROM VISUAL OBJECTS
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
    # VISUAL CONTEXT
    # =====================================================

    visual_objects = []

    for item in visual_context:

        if not isinstance(item, dict):
            continue

        object_name = item.get("object")

        if object_name:
            object_name = str(object_name).strip()

            if object_name and object_name not in visual_objects:
                visual_objects.append(object_name)


    # =====================================================
    # PRIMARY EVENT
    # =====================================================

    primary_event = scene_context.get(
        "primary_event",
        event
    )

    if isinstance(primary_event, list):

        primary_event = clean_list(
            primary_event
        )

        primary_event = ", ".join(
            primary_event
        )

    else:

        primary_event = str(
            primary_event
        ).strip()


    if not primary_event:
        primary_event = (
            ", ".join(event)
            if event
            else "crime scene"
        )


    # =====================================================
    # CORE ACTIONS
    # =====================================================

    # These actions are useful for understanding the event
    # but should not dominate the visual generation.
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

    for relationship in relationships:

        if not isinstance(
            relationship,
            dict
        ):
            continue

        subject = relationship.get(
            "subject"
        )

        action = relationship.get(
            "action"
        )

        obj = relationship.get(
            "object"
        )

        if not action:
            continue

        # Ignore administrative/investigative relationships
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

    event_text = (
        ", ".join(event)
        if event
        else primary_event
    )

    people_text = (
        ", ".join(people)
        if people
        else "people described in the scene"
    )

    location_text = (
        ", ".join(locations)
        if locations
        else "the described location"
    )

    time_text = (
        ", ".join(time)
        if time
        else "the described time"
    )

    action_text = (
        ", ".join(visual_actions)
        if visual_actions
        else "interaction between the described people"
    )

    object_text = (
        ", ".join(text_objects)
        if text_objects
        else "no specific physical objects identified"
    )

    evidence_text = (
        ", ".join(evidence)
        if evidence
        else "no specific forensic evidence identified"
    )

    condition_text = (
        ", ".join(conditions)
        if conditions
        else "no specific conditions identified"
    )

    visual_text = (
        ", ".join(visual_objects)
        if visual_objects
        else "none"
    )

    relationship_text_final = (
        "; ".join(relationship_text)
        if relationship_text
        else "No specific physical relationship identified."
    )


    # =====================================================
    # EVENT-SPECIFIC VISUAL GUIDANCE
    # =====================================================

    event_lower = (
        event_text + " " + primary_event
    ).lower()

    if any(word in event_lower for word in [
        "murder", "homicide", "killing", "attack", "assault"
    ]):
        event_guidance = """
The central subject is the described violent incident.
Clearly show the victim and suspect, if both are supported
by the input. Make their positions and interaction visible.
Show the victim's position and the surrounding scene clearly.
Use a non-graphic forensic reconstruction. No blood, gore,
or explicit injuries unless specifically described.
Do not add extra people or invent an attack in progress
if the source does not establish it.
"""

    elif any(word in event_lower for word in [
        "theft", "robbery", "burglary", "stealing"
    ]):
        event_guidance = """
Make the described theft or burglary the main visual event.
Show the suspect, relevant property, entry or exit points,
and the actions supported by the input. Make the incident
visually clear rather than depicting only the environment.
Do not invent weapons, extra suspects, or unsupported actions.
"""

    elif any(word in event_lower for word in [
        "accident", "collision", "crash"
    ]):
        event_guidance = """
Make the described accident the main visual event.
Clearly show the vehicles or people involved and their
positions, using only details supported by the input.
Keep the reconstruction realistic and non-graphic.
"""

    else:
        event_guidance = """
Make the specific event described in the input the
main visual focus. Clearly represent the supported people,
actions, objects, and spatial relationships. Do not replace
the event with generic scenery.
"""

    # =====================================================
    # FINAL IMAGE PROMPT
    # =====================================================

    prompt = f"""
FORENSIC SCENE RECONSTRUCTION — MAIN EVENT FIRST

Reconstruct this specific incident as a realistic,
photographic, non-graphic forensic visualization.

CRIME OR INCIDENT:
{event_text}

PRIMARY EVENT:
{primary_event}

LOCATION:
{location_text}

TIME:
{time_text}

PEOPLE:
{people_text}

ACTIONS:
{action_text}

IMPORTANT PHYSICAL OBJECTS:
{text_objects}

OTHER OBJECTS:
{common_objects}

FORENSIC EVIDENCE:
{evidence_text}

SCENE CONDITIONS:
{condition_text}

PHYSICAL RELATIONSHIPS:
{relationship_text_final}

REFERENCE IMAGE OBJECTS:
{visual_text}

EVENT REQUIREMENTS:
{event_guidance}

COMPOSITION:
Keep the main incident and described people clearly visible.
Show relevant objects and their positions in relation to
the people. Include the entrance, exit, and surroundings
when supported by the input. Keep the environment secondary
to the main incident.

REFERENCE IMAGE:
When an image is provided to the generation model, preserve
its relevant environment, architecture, perspective, and
spatial layout where possible. Follow the written incident
description for the event. Do not treat detected objects as
confirmed evidence or invent events from the image alone.

VISUAL STYLE:
Realistic documentary photography, natural proportions,
believable poses, clear composition, realistic lighting,
and a non-graphic forensic presentation.

STRICT CONSTRAINTS:
Do not produce generic scenery instead of the incident.
Do not invent people, weapons, injuries, actions, or evidence.
Do not show graphic violence. Do not add text or watermarks.
This is an AI-generated visualization, not verified evidence
of what actually happened.
"""

    return prompt.strip()

# =========================================================
# MAIN PROGRAM
# =========================================================

if __name__ == "__main__":

    with open(
        "../fusion_module/fused_scene.json",
        "r"
    ) as file:

        fused_scene = json.load(file)


    final_prompt = create_fused_prompt(
        fused_scene
    )


    print(
        "\n=========================================="
    )

    print(
        "          CLEAN FLUX PROMPT"
    )

    print(
        "=========================================="
    )

    print(final_prompt)


    with open(
        "final_fused_prompt.txt",
        "w"
    ) as file:

        file.write(final_prompt)


    print(
        "\nPrompt saved to final_fused_prompt.txt"
    )

    print(
        "\n=========================================="
    )

    print(
        "       PROMPT BUILDER COMPLETED"
    )

    print(
        "=========================================="
    )
