import spacy
import json

# Load spaCy English NLP model
nlp = spacy.load("en_core_web_sm")


def extract_nlp_information(text):

    doc = nlp(text)

    result = {
        "original_description": text,
        "sentences": [],
        "entities": [],
        "people": [],
        "locations": [],
        "organizations": [],
        "dates_times": [],
        "objects": [],
        "actions": [],
        "relationships": []
    }

    # --------------------------------------------------
    # 1. SENTENCE EXTRACTION
    # --------------------------------------------------

    for sentence in doc.sents:
        result["sentences"].append(sentence.text.strip())


    # --------------------------------------------------
    # 2. NAMED ENTITY EXTRACTION
    # --------------------------------------------------

    for entity in doc.ents:

        entity_data = {
            "text": entity.text,
            "label": entity.label_
        }

        result["entities"].append(entity_data)

        if entity.label_ in ["PERSON"]:
            result["people"].append(entity.text)

        elif entity.label_ in ["GPE", "LOC", "FAC"]:
            result["locations"].append(entity.text)

        elif entity.label_ in ["ORG"]:
            result["organizations"].append(entity.text)

        elif entity.label_ in ["DATE", "TIME"]:
            result["dates_times"].append(entity.text)


    # --------------------------------------------------
    # 3. NOUNS / OBJECTS
    # --------------------------------------------------

    for token in doc:

        if token.pos_ in ["NOUN", "PROPN"]:

            word = token.text.lower()

            if word not in [
                "scene",
                "crime",
                "incident",
                "person",
                "people"
            ]:

                if word not in result["objects"]:
                    result["objects"].append(word)


    # --------------------------------------------------
    # 4. ACTIONS / VERBS
    # --------------------------------------------------

    for token in doc:

        if token.pos_ == "VERB":

            action = token.lemma_.lower()

            if action not in result["actions"]:
                result["actions"].append(action)


    # --------------------------------------------------
    # 5. RELATIONSHIPS
    # --------------------------------------------------

    for token in doc:

        if token.dep_ in [
            "nsubj",
            "dobj",
            "pobj",
            "iobj"
        ]:

            if token.head.pos_ == "VERB":

                relationship = {
                    "subject_or_object": token.text,
                    "action": token.head.lemma_
                }

                result["relationships"].append(
                    relationship
                )


    return result


# --------------------------------------------------
# TEST PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    text = input(
        "Enter crime scene description:\n"
    )

    result = extract_nlp_information(text)

    print("\n")
    print("==========================================")
    print("       NLP SCENE EXTRACTION")
    print("==========================================")

    print("\nSentences:")
    print(result["sentences"])

    print("\nNamed Entities:")
    print(result["entities"])

    print("\nPeople:")
    print(result["people"])

    print("\nLocations:")
    print(result["locations"])

    print("\nOrganizations:")
    print(result["organizations"])

    print("\nDates / Times:")
    print(result["dates_times"])

    print("\nObjects / Nouns:")
    print(result["objects"])

    print("\nActions:")
    print(result["actions"])

    print("\nRelationships:")
    print(result["relationships"])


    # Save result
    with open(
        "nlp_scene_output.json",
        "w"
    ) as file:

        json.dump(
            result,
            file,
            indent=4
        )

    print(
        "\nNLP information saved to nlp_scene_output.json"
    )