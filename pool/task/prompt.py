import tracery
from tracery.modifiers import base_english

# Define a detailed grammar for generating realistic people image prompts
grammar = {
    "subject": [
        "a young woman",
        "an elderly man",
        "a teenager",
        "a child",
        "a middle-aged person",
    ],
    "style": [
        "with realistic facial features",
        "in modern clothing",
        "with a background of a bustling city",
        "posing in a natural setting",
        "with expressive emotions",
    ],
    "emotion": [
        "happy",
        "sad",
        "angry",
        "excited",
        "thoughtful",
    ],
    "accessories": [
        "wearing glasses",
        "with a hat",
        "holding a book",
        "with a backpack",
        "with a pet dog",
    ],
    "setting": [
        "at a park",
        "on a busy street",
        "in a cozy room",
        "at the beach",
        "in a forest",
    ],
    "action": [
        "smiling brightly",
        "looking pensive",
        "laughing with friends",
        "staring into the distance",
        "reading a book",
    ],
    "origin": "Create an image of #subject# #style# that looks #emotion#, #accessories#, #setting#, and #action#.",
}

# Create a tracery grammar
image_prompt_grammar = tracery.Grammar(grammar)
image_prompt_grammar.add_modifiers(base_english)


# Function to generate random image prompts for realistic people
def generate_random_image_prompt():
    try:
        return image_prompt_grammar.flatten("#origin#")
    except Exception as e:
        return f"An error occurred: {e}"
