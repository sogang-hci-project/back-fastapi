from src.utils.api import papago_translate, deepl_translate
import json
import asyncio
import numpy as np


def print_project_initialization():
    art = """
     __   __   __     ______     ______   __  __     ______     __         
    /\ \ / /  /\ \   /\  == \   /\__  _\ /\ \/\ \   /\  __ \   /\ \        
    \ \ \\'/   \ \ \  \ \  __<   \/_/\ \/ \ \ \_\ \  \ \  __ \  \ \ \____   
     \ \__|    \ \_\  \ \_\ \_\    \ \_\  \ \_____\  \ \_\ \_\  \ \_____\  
      \/_/      \/_/   \/_/ /_/     \/_/   \/_____/   \/_/\/_/   \/_____/  
                                                                          
     ______   __     ______     ______     ______     ______     ______    
    /\  == \ /\ \   /\  ___\   /\  __ \   /\  ___\   /\  ___\   /\  __ \   
    \ \  _-/ \ \ \  \ \ \____  \ \  __ \  \ \___  \  \ \___  \  \ \ \/\ \  
     \ \_\    \ \_\  \ \_____\  \ \_\ \_\  \/\_____\  \/\_____\  \ \_____\ 
      \/_/     \/_/   \/_____/   \/_/\/_/   \/_____/   \/_____/   \/_____/ 
    
    ✨ Welcome to Virtual Picasso. "Everyting You Can Imagine Is Real" - Pablo Picasso                                             
    """
    print(art)


class CustomError(Exception):
    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(message)


def throw_exception(message: str, code: int):
    raise CustomError(message=message, code=code)


async def server_translate(text: str, source_lang: str):
    try:
        res = await deepl_translate(text=text, source_lang=source_lang)
        print("■■■■■■■■■[DEEPL TRANSLATION RESULT]■■■■■■■■■")
        print(f"Before Translation: {text}")
        print(f"After Translation: {res['translatedText']}")
        return res["translatedText"]
    except Exception as deepl_e:
        try:
            res = await papago_translate(text=text, source_lang=source_lang)
            print("■■■■■■■■■[PAPAGO TRANSLATION RESULT]■■■■■■■■■")
            print(f"Before Translation: {text}")
            print(f"After Translation: {res['translatedText']}")
            return res["translatedText"]
        except Exception as papago_e:
            print("🔥 utils/commmon: [server_translate] failed 🔥")
            print("DeepL Error", deepl_e)
            print("Papago Error", papago_e)


def run_task_in_background(task):
    loop = asyncio.get_running_loop()
    loop.create_task(task)


def replace_entity_to_picasso(input_string: str):
    replacements = {
        "You": "Picasso",
        "you": "Picasso",
        "your": "Picasso",
        "Your": "Picasso",
        "art educator": "Picasso",
        "Picasso": "you",
        "Picasso's": "your",
    }

    for old_str, new_str in replacements.items():
        input_string = input_string.replace(old_str, new_str)

    return input_string


neo4j_entities = []


def load_neo4j_entities():
    try:
        global neo4j_entities
        with open("src/representations/entities.json", "r") as json_file:
            neo4j_entities.extend(json.load(json_file))
        print(f"Loaded [entities_json] with {len(neo4j_entities)} entities")

    except Exception as e:
        print("🔥 startup: [common/load_neo4j_entities] failed 🔥", e)


def cosine_similarity(a, b):
    dot_product = np.dot(a, b)
    magnitude_a = np.linalg.norm(a)
    magnitude_b = np.linalg.norm(b)
    return dot_product / (magnitude_a * magnitude_b)
