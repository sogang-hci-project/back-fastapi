import requests
import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

NAVER_CLOUD_PAPAGO_ID_KEY = os.environ.get("NAVER_CLOUD_PAPAGO_ID_KEY")
NAVER_CLOUD_PAPAGO_SECRET_KEY = os.environ.get("NAVER_CLOUD_PAPAGO_SECRET_KEY")
DEEPL_API_KEY = os.environ.get("DEEPL_API_KEY")
NAVER_CLOUD_CLOVA_ID_KEY = os.environ.get("NAVER_CLOUD_CLOVA_ID_KEY")
NAVER_CLOUD_CLOVA_SECRET_KEY = os.environ.get("NAVER_CLOUD_CLOVA_SECERT_KEY")


async def papago_translate(text: str, source_lang: str) -> Dict[str, str]:
    try:
        target_lang = "ko" if source_lang == "en" else "en"

        headers = {
            "X-NCP-APIGW-API-KEY-ID": NAVER_CLOUD_PAPAGO_ID_KEY,
            "X-NCP-APIGW-API-KEY": NAVER_CLOUD_PAPAGO_SECRET_KEY,
        }

        data = {
            "source": source_lang,
            "target": target_lang,
            "text": text,
        }

        url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"

        response = requests.post(url, data=data, headers=headers)
        response_data = response.json()
        translated_text = response_data["message"]["result"]["translatedText"]

        return {"translatedText": translated_text}
    except Exception as e:
        print("🔥 utils/api: [papago_translate] failed 🔥", e)


async def deepl_translate(text: str, source_lang: str) -> Dict[str, str]:
    try:
        target_lang = "KO" if source_lang == "en" else "EN"

        data = {
            "text": text,
            "target_lang": target_lang,
        }

        headers = {
            "Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        url = "https://api-free.deepl.com/v2/translate"

        response = requests.post(url, data=data, headers=headers)
        response_data = response.json()
        translated_text = response_data.get("translations", [])[0].get("text", None)

        return {"translatedText": translated_text}
    except Exception as e:
        print("🔥 utils/api: [deepl_translate] failed 🔥", e)


async def clova_text_to_speech(text: str, voice: str):
    try:
        headers = {
            "X-NCP-APIGW-API-KEY-ID": NAVER_CLOUD_CLOVA_ID_KEY,
            "X-NCP-APIGW-API-KEY": NAVER_CLOUD_CLOVA_SECRET_KEY,
        }

        request_data = {
            "volume": "0",
            "speed": "-1",
            "pitch": "0",
            "end-pitch": "-2",
            "speaker": voice,
            "text": text,
        }

        url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"

        response = requests.post(url, data=request_data, headers=headers)
        return response.content
    except Exception as e:
        print("🔥 utils/api: [clova_text_to_speech] failed 🔥", e)
