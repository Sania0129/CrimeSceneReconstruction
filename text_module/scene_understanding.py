import spacy
import re
import json


# =====================================================
# LOAD SPACY MODEL
# =====================================================

nlp = spacy.load("en_core_web_sm")


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def add_unique(items, value):
    """Add a cleaned value only if it is not already present."""

    if value is None:
        return

    value = str(value).strip().lower()

    if value and value not in items:
        items.append(value)


def clean_phrase(text):
    """Clean unnecessary articles and spaces."""

    if not text:
        return ""

    text = text.strip().lower()

    text = re.sub(
        r"^(a|an|the|some|several|many|few)\s+",
        "",
        text
    )

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =====================================================
# TIME EXTRACTION
# =====================================================

def extract_time(doc):

    times = []

    # spaCy recognized time/date entities
    for ent in doc.ents:

        if ent.label_ in ["TIME", "DATE"]:
            add_unique(times, ent.text)

    # Crime-scene time expressions
    time_patterns = [
        r"\b\d{1,2}\s?(?:am|pm)\b",
        r"\b\d{1,2}:\d{2}\s?(?:am|pm)?\b",
        r"\bmidnight\b",
        r"\bnoon\b",
        r"\bnight\b",
        r"\bmorning\b",
        r"\bevening\b",
        r"\bafternoon\b",
        r"\bdawn\b",
        r"\bdusk\b"
    ]

    text = doc.text.lower()

    for pattern in time_patterns:

        matches = re.findall(pattern, text)

        for match in matches:
            add_unique(times, match)

    return times


# =====================================================
# PEOPLE EXTRACTION
# =====================================================

def extract_people(doc):

    people = []

    person_roles = {
        "person",
        "man",
        "woman",
        "boy",
        "girl",
        "child",
        "thief",
        "robber",
        "suspect",
        "victim",
        "criminal",
        "offender",
        "driver",
        "passenger",
        "guard",
        "security guard",
        "cashier",
        "shopkeeper",
        "owner",
        "employee",
        "customer",
        "witness",
        "police officer",
        "officer",
        "detective",
        "attacker",
        "intruder",
        "burglar",
        "hacker",
        "killer",
        "motorcyclist",
        "pedestrian",
        "rider",
        "driver"
    }

    # Named people recognized by spaCy
    for ent in doc.ents:

        if ent.label_ == "PERSON":
            add_unique(people, ent.text)

    # Individual role words
    for token in doc:

        word = token.text.lower()

        if word in person_roles:
            add_unique(people, word)

    # Multi-word roles
    text = doc.text.lower()

    multi_word_roles = [
        "security guard",
        "police officer",
        "shop owner",
        "bank employee",
        "bank manager"
    ]

    for role in multi_word_roles:

        if role in text:
            add_unique(people, role)

    return people


# =====================================================
# LOCATION EXTRACTION
# =====================================================

def extract_locations(doc):

    locations = []

    location_words = {
        "bank",
        "atm",
        "house",
        "home",
        "room",
        "bedroom",
        "kitchen",
        "building",
        "store",
        "shop",
        "jewelry store",
        "mall",
        "office",
        "road",
        "street",
        "highway",
        "parking lot",
        "warehouse",
        "hotel",
        "school",
        "college",
        "hospital",
        "restaurant",
        "station",
        "airport",
        "entrance",
        "exit",
        "door",
        "back door",
        "front door",
        "city",
        "village",
        "park",
        "roadside",
        "intersection"
    }

    # spaCy locations
    for ent in doc.ents:

        if ent.label_ in ["GPE", "LOC", "FAC"]:
            add_unique(locations, ent.text)

    text = doc.text.lower()

    # Longer phrases first
    sorted_locations = sorted(
        location_words,
        key=len,
        reverse=True
    )

    for location in sorted_locations:

        if location in text:
            add_unique(locations, location)

    return locations


# =====================================================
# ACTION EXTRACTION
# =====================================================

def extract_actions(doc):

    actions = []

    useful_actions = {
        "attack",
        "escape",
        "enter",
        "leave",
        "run",
        "walk",
        "drive",
        "take",
        "steal",
        "remove",
        "break",
        "damage",
        "threaten",
        "demand",
        "carry",
        "approach",
        "capture",
        "find",
        "shoot",
        "kill",
        "hide",
        "open",
        "close",
        "destroy",
        "hit",
        "fight",
        "rob",
        "grab",
        "drop",
        "wait",
        "flee",
        "search",
        "enter",
        "exit",
        "collide",
        "crash",
        "fall",
        "ride",
        "park",
        "drive",
        "approach",
        "break",
        "damage",
        "escape",
        "threaten",
        "carry",
        "steal",
        "take"
    }

    for token in doc:

        # Normal verbs
        if token.pos_ == "VERB":

            add_unique(
                actions,
                token.lemma_
            )

        # Useful action keywords
        elif token.lemma_.lower() in useful_actions:

            add_unique(
                actions,
                token.lemma_
            )

    return actions


# =====================================================
# OBJECT EXTRACTION
# =====================================================

def extract_objects(
    doc,
    people,
    locations,
    times
):

    objects = []

    excluded_words = {
        "person",
        "people",
        "man",
        "woman",
        "security",
        "boy",
        "girl",
        "child",
        "thief",
        "robber",
        "suspect",
        "victim",
        "criminal",
        "offender",
        "driver",
        "passenger",
        "guard",
        "cashier",
        "shopkeeper",
        "owner",
        "employee",
        "customer",
        "witness",
        "officer",
        "detective",
        "attacker",
        "intruder",
        "burglar",
        "killer",
        "hacker",
        "scene",
        "incident",
        "event",
        "thing",
        "time",
        "he",
        "she",
        "him",
        "her",
        "his",
        "their",
        "they",
        "them"
    }

    time_words = {
        "am",
        "pm",
        "night",
        "morning",
        "afternoon",
        "evening",
        "midnight",
        "noon",
        "dawn",
        "dusk"
    }

    # -------------------------------------------------
    # Noun phrases
    # -------------------------------------------------

    phrases = []

    for chunk in doc.noun_chunks:

        phrase = clean_phrase(chunk.text)

        if not phrase:
            continue

        if phrase in people:
            continue

        if phrase in locations:
            continue

        if phrase in times:
            continue

        words = phrase.split()

        # Ignore phrases consisting only of people/time words
        if all(
            word in excluded_words
            or word in time_words
            for word in words
        ):
            continue

        # Remove phrases that are mainly time expressions
        if any(
            word in time_words
            for word in words
        ):
            continue

        add_unique(
            phrases,
            phrase
        )

    # -------------------------------------------------
    # Clean phrases
    # -------------------------------------------------

    cleaned_phrases = []

    for phrase in phrases:

        words = phrase.split()

        if any(
            word in excluded_words
            for word in words
        ):
            continue

        add_unique(
            cleaned_phrases,
            phrase
        )

    # -------------------------------------------------
    # Prefer descriptive phrases
    # -------------------------------------------------

    cleaned_phrases.sort(
        key=lambda x: len(x.split()),
        reverse=True
    )

    for phrase in cleaned_phrases:

        already_inside = False

        for existing in objects:

            if phrase in existing:
                already_inside = True
                break

        if not already_inside:
            add_unique(
                objects,
                phrase
            )

    # -------------------------------------------------
    # Add important individual nouns
    # -------------------------------------------------

    for token in doc:

        if token.pos_ not in ["NOUN", "PROPN"]:
            continue

        word = token.text.strip().lower()

        if not word:
            continue

        if word in excluded_words:
            continue

        if word in time_words:
            continue

        if word in people:
            continue

        if word in locations:
            continue

        if any(
            word in phrase.split()
            for phrase in objects
        ):
            continue

        add_unique(
            objects,
            word
        )

    return objects


# =====================================================
# CONDITIONS
# =====================================================

def extract_conditions(doc):

    condition_words = [
        "broken",
        "damaged",
        "open",
        "closed",
        "locked",
        "unlocked",
        "burned",
        "burnt",
        "destroyed",
        "injured",
        "dead",
        "unconscious",
        "missing",
        "wet",
        "dark",
        "crowded",
        "empty",
        "abandoned",
        "scattered",
        "visible",
        "masked"
    ]

    conditions = []

    text = doc.text.lower()

    for word in condition_words:

        if word in text:

            add_unique(
                conditions,
                word
            )

    return conditions


# =====================================================
# EVIDENCE
# =====================================================

def extract_evidence(doc):

    evidence_words = [
        "cctv",
        "camera",
        "footage",
        "fingerprint",
        "fingerprints",
        "blood",
        "bloodstain",
        "weapon",
        "gun",
        "handgun",
        "knife",
        "bullet",
        "shell",
        "shells",
        "glass",
        "broken glass",
        "tire mark",
        "tire marks",
        "footprint",
        "footprints",
        "dna",
        "fiber",
        "fibers",
        "document",
        "phone",
        "computer",
        "laptop",
        "jewelry",
        "weapon"
    ]

    evidence = []

    text = doc.text.lower()

    # Check longer phrases first
    sorted_evidence = sorted(
        evidence_words,
        key=len,
        reverse=True
    )

    for word in sorted_evidence:

        if word in text:

            add_unique(
                evidence,
                word
            )

    return evidence


# =====================================================
# EVENT / CRIME TYPE
# =====================================================

def extract_event(doc):

    events = []

    event_words = {
        "theft",
        "robbery",
        "burglary",
        "murder",
        "homicide",
        "assault",
        "attack",
        "kidnapping",
        "abduction",
        "arson",
        "fraud",
        "vandalism",
        "accident",
        "collision",
        "crash",
        "trespassing",
        "shoplifting",
        "cybercrime",
        "hacking",
        "stabbing",
        "shooting",
        "rape",
        "break-in",
        "breakin"
    }

    text = doc.text.lower()

    for event in event_words:

        if event in text:

            add_unique(
                events,
                event
            )

    # -------------------------------------------------
    # Context-based event detection
    # -------------------------------------------------

    # Burglary-like description
    burglary_terms = [
        "entered a house",
        "entered the house",
        "broke into",
        "break into",
        "forced entry",
        "damaged window",
        "intruder entered",
        "burglar entered"
    ]

    if any(term in text for term in burglary_terms):
        add_unique(events, "burglary")

    # Theft-like description
    theft_terms = [
        "took cash",
        "took money",
        "stole cash",
        "stole money",
        "stole a",
        "stole the",
        "took the",
        "took a"
    ]

    if any(term in text for term in theft_terms):
        add_unique(events, "theft")

    # Robbery-like description
    robbery_terms = [
        "threatened the cashier",
        "threatened the guard",
        "threatened a guard",
        "demanded money",
        "threatened with a gun",
        "threatened with a handgun"
    ]

    if any(term in text for term in robbery_terms):
        add_unique(events, "robbery")

    # Road accident
    accident_terms = [
        "car collided",
        "vehicle collided",
        "road accident",
        "traffic accident",
        "vehicle crash",
        "car crash",
        "motorcycle crash"
    ]

    if any(term in text for term in accident_terms):
        add_unique(events, "accident")

    return events


# =====================================================
# RELATIONSHIPS
# =====================================================

def extract_relationships(doc):

    relationships = []

    for token in doc:

        if token.pos_ != "VERB":
            continue

        subject = None
        object_word = None

        # ---------------------------------------------
        # Find grammatical subject
        # ---------------------------------------------

        for child in token.children:

            if child.dep_ in [
                "nsubj",
                "nsubjpass",
                "csubj"
            ]:

                subject = child.text.lower()

                # Try to use compound subject
                compounds = [
                    c.text.lower()
                    for c in child.children
                    if c.dep_ == "compound"
                ]

                if compounds:
                    subject = " ".join(
                        compounds + [subject]
                    )

            # -----------------------------------------
            # Find direct/prepositional object
            # -----------------------------------------

            if child.dep_ in [
                "dobj",
                "obj"
            ]:

                object_word = child.text.lower()

            elif child.dep_ == "prep":

                for prep_child in child.children:

                    if prep_child.dep_ == "pobj":

                        object_word = (
                            prep_child.text.lower()
                        )

        # ---------------------------------------------
        # Save only meaningful relationships
        # ---------------------------------------------

        if subject or object_word:

            relationships.append(
                {
                    "action": token.lemma_.lower(),
                    "subject": subject,
                    "object": object_word
                }
            )

    return relationships


# =====================================================
# SCENE SUMMARY
# =====================================================

def create_scene_summary(scene):

    event_text = ", ".join(
        scene["event"]
    ) if scene["event"] else "unspecified event"

    location_text = ", ".join(
        scene["locations"]
    ) if scene["locations"] else "unspecified location"

    time_text = ", ".join(
        scene["time"]
    ) if scene["time"] else "unspecified time"

    return (
        f"Event: {event_text}. "
        f"Location: {location_text}. "
        f"Time: {time_text}. "
        f"People: {', '.join(scene['people']) if scene['people'] else 'none identified'}. "
        f"Objects: {', '.join(scene['objects']) if scene['objects'] else 'none identified'}. "
        f"Actions: {', '.join(scene['actions']) if scene['actions'] else 'none identified'}. "
        f"Conditions: {', '.join(scene['conditions']) if scene['conditions'] else 'none identified'}. "
        f"Evidence: {', '.join(scene['evidence']) if scene['evidence'] else 'none identified'}."
    )


# =====================================================
# MAIN SCENE UNDERSTANDING
# =====================================================

def understand_scene(description):

    doc = nlp(description)

    times = extract_time(doc)

    people = extract_people(doc)

    locations = extract_locations(doc)

    actions = extract_actions(doc)

    objects = extract_objects(
        doc,
        people,
        locations,
        times
    )

    conditions = extract_conditions(doc)

    evidence = extract_evidence(doc)

    events = extract_event(doc)

    relationships = extract_relationships(doc)

    scene = {

        "description": description,

        "event": events,

        "time": times,

        "people": people,

        "locations": locations,

        "objects": objects,

        "actions": actions,

        "conditions": conditions,

        "evidence": evidence,

        "relationships": relationships
    }

    # Additional human-readable summary
    scene["scene_summary"] = create_scene_summary(
        scene
    )

    return scene


# =====================================================
# RUN PROGRAM
# =====================================================

if __name__ == "__main__":

    print("\n==========================================")
    print("       UPGRADED SCENE UNDERSTANDING")
    print("==========================================")

    crime_description = input(
        "\nEnter crime scene description:\n"
    )

    scene = understand_scene(
        crime_description
    )

    print("\n------------------------------------------")
    print("EVENT")
    print("------------------------------------------")
    print(scene["event"])

    print("\n------------------------------------------")
    print("TIME")
    print("------------------------------------------")
    print(scene["time"])

    print("\n------------------------------------------")
    print("PEOPLE")
    print("------------------------------------------")
    print(scene["people"])

    print("\n------------------------------------------")
    print("LOCATIONS")
    print("------------------------------------------")
    print(scene["locations"])

    print("\n------------------------------------------")
    print("OBJECTS")
    print("------------------------------------------")
    print(scene["objects"])

    print("\n------------------------------------------")
    print("ACTIONS")
    print("------------------------------------------")
    print(scene["actions"])

    print("\n------------------------------------------")
    print("CONDITIONS")
    print("------------------------------------------")
    print(scene["conditions"])

    print("\n------------------------------------------")
    print("EVIDENCE")
    print("------------------------------------------")
    print(scene["evidence"])

    print("\n------------------------------------------")
    print("RELATIONSHIPS")
    print("------------------------------------------")
    print(scene["relationships"])

    print("\n------------------------------------------")
    print("SCENE SUMMARY")
    print("------------------------------------------")
    print(scene["scene_summary"])

    output_file = "scene_understanding_output.json"

    with open(
        output_file,
        "w"
    ) as file:

        json.dump(
            scene,
            file,
            indent=4
        )

    print(
        "\nScene information saved to "
        "scene_understanding_output.json"
    )
