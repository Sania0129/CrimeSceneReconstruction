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

    event_lower = event_text.lower()

    if (
        "murder" in event_lower
        or "attack" in event_lower
        or "assault" in event_lower
    ):

        event_guidance = """
Show the victim and suspect as the main subjects.
Place them close enough to clearly communicate a
confrontation or physical attack.

Use realistic body positioning, facial direction,
distance, gestures and orientation to make the
interaction understandable at first glance.

The suspect should be visibly confronting the victim.
The victim should be clearly distinguishable from
the suspect.

Keep the depiction non-graphic. Do not show blood,
gore or explicit injuries unless specifically described
in the source information.
"""

    elif (
        "theft" in event_lower
        or "robbery" in event_lower
        or "burglary" in event_lower
    ):

        event_guidance = """
Show the suspect and the important physical objects
associated with the theft.

Use body positioning and movement to communicate
entering, searching, taking property or escaping.

Make the theft activity visually obvious rather than
showing only an empty environment.
"""

    elif "accident" in event_lower or "collision" in event_lower:

        event_guidance = """
Show the vehicles involved in the collision clearly.

Use their positions, damage and surrounding road
environment to communicate that a collision occurred.

Keep the accident realistic and non-graphic.
"""

    else:

        event_guidance = """
Clearly show the people, actions and physical
relationships described in the crime scene information.

The main event must be visually understandable.
"""


    # =====================================================
    # FINAL IMAGE PROMPT
    # =====================================================

    prompt = f"""
Create a realistic documentary-style forensic
reconstruction of the described crime scene.

MAIN EVENT
{event_text}

LOCATION
{location_text}

TIME
{time_text}

PEOPLE
{people_text}

PHYSICAL OBJECTS
{object_text}

ACTIONS
{action_text}

RELATIONSHIPS
{relationship_text_final}

FORENSIC EVIDENCE
{evidence_text}

SCENE CONDITIONS
{condition_text}

REFERENCE IMAGE CONTEXT
The uploaded reference image provides the physical
environment, perspective, architecture, spatial layout
and compatible visual context.

Objects visible in the reference image:
{visual_text}

Use the reference image as the environmental foundation,
but reconstruct the scene according to the written crime
description.

EVENT VISUALIZATION
{event_guidance}

SCENE COMPOSITION

Foreground:
Clearly show the main people and the main crime event.

Middle ground:
Show the interaction between people and relevant
physical objects.

Background:
Show the surrounding location, buildings, road,
architecture and environmental context from the
reference image.

The crime event must remain the visual focus.

STYLE

Realistic forensic reconstruction.
Documentary photography appearance.
Natural human proportions.
Realistic human poses.
Realistic perspective.
Natural nighttime lighting where appropriate.
Detailed Indian residential/environmental setting where
supported by the location.
Believable spatial relationships.
Non-graphic presentation.

Do not create a generic empty environment.
Do not make scenery more prominent than the crime event.
Do not invent additional suspects, victims, weapons,
major events or unsupported evidence.
Do not treat objects detected only by computer vision
as confirmed forensic evidence.

The result is an AI-generated visualization based on
available crime-scene information and is not a verified
record of what actually happened.
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