import spacy
import json
import re

nlp = spacy.load("en_core_web_sm")


# --------------------------------------------------
# 1. CRIME TYPE DETECTION
# --------------------------------------------------

def detect_crime_type(text):

    text_lower = text.lower()

    crime_patterns = {
        "Bank Theft": [
            "bank robbery",
            "bank theft",
            "bank robbery",
            "robbed the bank",
            "stole money from the bank"
        ],

        "ATM Theft": [
            "atm theft",
            "atm robbery",
            "robbed an atm",
            "stole money from an atm"
        ],

        "Burglary": [
            "burglary",
            "burglar",
            "broke into",
            "break into",
            "forced entry",
            "house was broken into"
        ],

        "Murder": [
            "murder",
            "murdered",
            "killed",
            "kill",
            "dead body",
            "death"
        ],

        "Shop Theft": [
            "shop theft",
            "store theft",
            "shop robbery",
            "store robbery",
            "robbed the shop",
            "robbed the store"
        ]
    }

    for crime_type, patterns in crime_patterns.items():

        for pattern in patterns:

            if pattern in text_lower:
                return crime_type

    # General theft detection
    theft_words = [
        "stole",
        "steal",
        "stolen",
        "theft",
        "robbed",
        "robbery",
        "rob",
        "took"
    ]

    if any(word in text_lower for word in theft_words):

        return "Theft"

    return "Unknown Crime"


# --------------------------------------------------
# 2. TIME EXTRACTION
# --------------------------------------------------

def extract_time(text):

    text_lower = text.lower()

    time_keywords = [
        "morning",
        "afternoon",
        "evening",
        "night",
        "midnight",
        "noon",
        "dawn",
        "dusk",
        "late night",
        "early morning",
        "daytime"
    ]

    detected_time = []

    for time in time_keywords:

        pattern = r"\b" + re.escape(time) + r"\b"

        if re.search(pattern, text_lower):

            detected_time.append(time)

    return detected_time


# --------------------------------------------------
# 3. PEOPLE EXTRACTION
# --------------------------------------------------

def extract_people(text):

    text_lower = text.lower()

    people_keywords = [
        "man",
        "woman",
        "person",
        "people",
        "suspect",
        "criminal",
        "thief",
        "robber",
        "burglar",
        "cashier",
        "guard",
        "victim",
        "customer",
        "employee",
        "police officer",
        "security guard",
        "driver",
        "witness"
    ]

    detected_people = []

    for person in people_keywords:

        pattern = r"\b" + re.escape(person) + r"\b"

        if re.search(pattern, text_lower):

            detected_people.append(person)

    return detected_people


# --------------------------------------------------
# 4. LOCATION EXTRACTION
# --------------------------------------------------

def extract_locations(text):

    text_lower = text.lower()

    location_keywords = [
        "bank",
        "atm",
        "house",
        "home",
        "office",
        "shop",
        "store",
        "jewelry store",
        "street",
        "road",
        "parking lot",
        "warehouse",
        "hotel",
        "restaurant",
        "school",
        "hospital",
        "apartment",
        "building",
        "mall",
        "supermarket",
        "garage",
        "park"
    ]

    detected_locations = []

    for location in location_keywords:

        pattern = r"\b" + re.escape(location) + r"\b"

        if re.search(pattern, text_lower):

            detected_locations.append(location)

    return detected_locations


# --------------------------------------------------
# 5. OBJECT EXTRACTION
# --------------------------------------------------

def extract_objects(text):

    text_lower = text.lower()

    object_keywords = {

        "weapon": [
            "gun",
            "handgun",
            "knife",
            "pistol",
            "rifle"
        ],

        "money": [
            "cash",
            "money",
            "currency"
        ],

        "electronic_device": [
            "laptop",
            "computer",
            "mobile",
            "phone",
            "smartphone",
            "tablet"
        ],

        "jewelry": [
            "jewelry",
            "jewel",
            "gold",
            "necklace",
            "ring",
            "bracelet"
        ],

        "vehicle": [
            "car",
            "bike",
            "motorcycle",
            "van",
            "truck",
            "vehicle"
        ],

        "entry_point": [
            "door",
            "back door",
            "front door",
            "window",
            "gate",
            "entrance",
            "exit"
        ],

        "property": [
            "cabinet",
            "glass",
            "bag",
            "box",
            "safe",
            "counter",
            "cash register"
        ]
    }

    detected_objects = {}

    for category, keywords in object_keywords.items():

        found = []

        for keyword in keywords:

            pattern = r"\b" + re.escape(keyword) + r"\b"

            if re.search(pattern, text_lower):

                found.append(keyword)

        if found:

            detected_objects[category] = found

    return detected_objects


# --------------------------------------------------
# 6. ACTION EXTRACTION
# --------------------------------------------------

def extract_actions(text):

    text_lower = text.lower()

    action_keywords = {

        "entry": [
            "entered",
            "enter",
            "broke into",
            "approached",
            "came inside",
            "entered through",
            "forced entry"
        ],

        "threat": [
            "threatened",
            "threaten",
            "attacked",
            "pointed",
            "intimidated"
        ],

        "theft": [
            "stole",
            "steal",
            "robbed",
            "rob",
            "took",
            "taken"
        ],

        "damage": [
            "damaged",
            "destroyed",
            "smashed",
            "broke the",
            "damaged the"
        ],

        "escape": [
            "escaped",
            "fled",
            "ran away",
            "left",
            "drove away"
        ]
    }

    detected_actions = {}

    for category, keywords in action_keywords.items():

        found = []

        for keyword in keywords:

            pattern = r"\b" + re.escape(keyword) + r"\b"

            if re.search(pattern, text_lower):

                found.append(keyword)

        if found:

            detected_actions[category] = found

    return detected_actions


# --------------------------------------------------
# 7. COMPLETE SCENE REPRESENTATION
# --------------------------------------------------

def create_scene_representation(text):

    scene = {

        "crime_type": detect_crime_type(text),

        "location": extract_locations(text),

        "time": extract_time(text),

        "people": extract_people(text),

        "objects": extract_objects(text),

        "actions": extract_actions(text),

        "original_description": text
    }

    return scene


# --------------------------------------------------
# 8. TEST PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    text = input(
        "Enter crime scene description:\n"
    )

    result = create_scene_representation(text)

    print("\nCrime Scene Information")
    print("-----------------------")

    print(
        "Crime Type:",
        result["crime_type"]
    )

    print(
        "Locations:",
        result["location"]
    )

    print(
        "Time:",
        result["time"]
    )

    print(
        "People:",
        result["people"]
    )

    print(
        "Objects:",
        result["objects"]
    )

    print(
        "Actions:",
        result["actions"]
    )

    with open(
        "crime_output.json",
        "w"
    ) as file:

        json.dump(
            result,
            file,
            indent=4
        )

    print(
        "\nCrime information saved to crime_output.json"
    )