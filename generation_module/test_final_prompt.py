import json


def load_final_prompt():

    with open(
        "final_fused_prompt.txt",
        "r"
    ) as file:

        prompt = file.read()

    return prompt


if __name__ == "__main__":

    prompt = load_final_prompt()

    print("\n==========================================")
    print("          PROMPT READY FOR FLUX")
    print("==========================================")

    print(prompt)

    print("\nPrompt successfully loaded.")
    print("Ready to send to FLUX.1-dev.")