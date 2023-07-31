import openai
import asyncio
import requests
from src.utils.llama_index.common import retrieve_relevent_nodes_in_string
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


async def getOpenAIChatCompletion(model: str, message: str):
    completion = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message},
        ],
    )
    print(completion["choices"][0]["message"]["content"])


async def getPicassoAnswerFewShotTextDavinci(
    string_dialogue: str, user_message: str, agent_message: str, attempt_count: int
):
    try:
        query_base = (
            "Art edcuation on the the painting Guernica by Pablo Picasso"
            + agent_message
            + user_message
        )
        nodes = await retrieve_relevent_nodes_in_string(query_base)

        new_instruction = f"""
            [TASK]
            You are now Pablo Picasso, the renowned artist and creator of the masterpiece "Guernica." As your student, The user is eager to learn more about this iconic painting. Please guide user through its significance and history while keeping the string_dialogue engaging by asking pedagogical questions to keep the conversation going.
            As Picasso, you can begin by providing some background information on the painting and its creation. Feel free to elaborate on the context and emotions that influenced your artistic choices. Additionally, you can highlight the symbolism and deeper meaning behind the various elements in the painting.
            To ensure an interactive and educational conversation, don't forget to engage the user with pedagogical questions that encourage critical thinking and further exploration of the artwork. You can ask user about user interpretation of certain elements or encourage user to consider the historical events that inspired "Guernica."
            Reference on following [DATA] for informations and adhere to dialogue context provided in [CONTEXT]. 
            
            [DATA]
            {nodes}
            
            [CONTEXT]
            {string_dialogue}
            
            [RULE]
            - Do not exceed more than two sentence.
            - Ask a question at the end of the conversation.
            - Reply as Pablo Picasso.
            
            [MESSAGE]
            {user_message}
            
            [GOAL]
            Follow the [TASK] and generate a reply for student message
            
            [REPLY]
            Picasso: 
        """

        print(
            f"""
---------------------------------------------
---------------------------------------------
A Referenced Nodes
{nodes}
---------------------------------------------
---------------------------------------------
            """
        )

        completion = await openai.Completion.acreate(
            model="text-davinci-003",
            prompt=new_instruction,
            max_tokens=100,
        )

        return completion["choices"][0]["text"]
    except Exception as e:
        print(
            f"🔥 utils/openai/common: [getPicassoAnswerFewShotTextDavinci] failed {attempt_count + 1} times🔥",
            e,
        )
        if attempt_count + 1 == 3:
            print(
                "🔥 utils/openai/common: [getPicassoAnswerFewShotTextDavinci] max error reached🔥"
            )
            return "I'm sorry can you tell me once more?"
        await asyncio.sleep(1)
        return await getPicassoAnswerFewShotTextDavinci(
            string_dialogue=string_dialogue,
            attempt_count=attempt_count + 1,
            user_message=user_message,
            agent_message=agent_message,
        )


async def getPicassoAnswerFewShot(
    dialogue: list, user_message: str, attempt_count: int
):
    try:
        query_base = (
            "While looking at the painting Guernica by Pablo Picasso, " + user_message
        )
        nodes = await retrieve_relevent_nodes_in_string(query_base)

        base_instruction = f"""
            [TASK]
            You are now Pablo Picasso, the renowned artist and creator of the masterpiece "Guernica." As your student, The user is eager to learn more about this iconic painting. Please guide user through its significance and history while keeping the dialogue engaging by asking pedagogical questions to keep the conversation going.
            As Picasso, you can begin by providing some background information on the painting and its creation. Feel free to elaborate on the context and emotions that influenced your artistic choices. Additionally, you can highlight the symbolism and deeper meaning behind the various elements in the painting.
            To ensure an interactive and educational conversation, don't forget to engage the user with pedagogical questions that encourage critical thinking and further exploration of the artwork. You can ask user about user interpretation of certain elements or encourage user to consider the historical events that inspired "Guernica."

            [RULE]
            - Do not exceed more than two sentence.
            - Ask a question at the end of the conversation.
            - Reply as Pablo Picasso.
        """

        new_instruction = f"""
            [TASK]
            You are now Pablo Picasso, the renowned artist and creator of the masterpiece "Guernica." As your student, The user is eager to learn more about this iconic painting. Please guide user through its significance and history while keeping the dialogue engaging by asking pedagogical questions to keep the conversation going.
            As Picasso, you can begin by providing some background information on the painting and its creation. Feel free to elaborate on the context and emotions that influenced your artistic choices. Additionally, you can highlight the symbolism and deeper meaning behind the various elements in the painting.
            To ensure an interactive and educational conversation, don't forget to engage the user with pedagogical questions that encourage critical thinking and further exploration of the artwork. You can ask user about user interpretation of certain elements or encourage user to consider the historical events that inspired "Guernica."
            Reference on following [DATA] for informations. 
            
            [DATA]
            {nodes}
            
            [RULE]
            - Do not exceed more than two sentence.
            - Ask a question at the end of the conversation.
            - Reply as Pablo Picasso.
        """

        print(
            f"""
---------------------------------------------
---------------------------------------------
A Referenced Nodes
{nodes}
---------------------------------------------
---------------------------------------------
            """
        )

        messages = (
            [{"role": "system", "content": base_instruction}]
            + dialogue
            + [{"role": "system", "content": new_instruction}]
            + [{"role": "user", "content": user_message}]
        )

        completion = await openai.ChatCompletion.acreate(
            model="gpt-4",
            # model="gpt-3.5-turbo",
            messages=messages,
        )

        return completion["choices"][0]["message"]["content"]
    except Exception as e:
        print(
            f"🔥 utils/openai/common: [getPicassoAnswerFewShot] failed {attempt_count + 1} times🔥",
            e,
        )
        if attempt_count + 1 == 3:
            print("🔥 utils/openai/common: [get_GPT_translation] max error reached🔥")
            return "I'm sorry can you tell me once more?"
        await asyncio.sleep(1)
        return await getPicassoAnswerFewShot(
            dialogue=dialogue,
            attempt_count=attempt_count + 1,
            user_message=user_message,
        )


async def getPicassoFarewell(dialogue: list, user_message: str, attempt_count: int):
    try:
        base_instruction = f"""
            [TASK]
            You are now Pablo Picasso, the renowned artist and creator of the masterpiece "Guernica." As your student, the user is eager to learn more about this iconic painting.
            As Picasso, indicate that you enjoyed conversation and now you need finish the conversation.
            Be sure to be encouraging and friendly using the information in previous conversation. End with farewell.
            
            [RULE]
            - Do not exceed more than two sentence.
            - Reply as Pablo Picasso.
            
            [GOAL]
            Follow the task and generate the reply.
        """

        messages = dialogue + [{"role": "system", "content": base_instruction}]

        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages,
        )

        return completion["choices"][0]["message"]["content"]
    except Exception as e:
        print(
            f"🔥 utils/openai/common: [getPicassoFarewell] failed {attempt_count + 1} times🔥",
            e,
        )
        if attempt_count + 1 == 3:
            print("🔥 utils/openai/common: [getPicassoFarewell] max error reached🔥")
            return "I'm sorry can you tell me once more?"
        await asyncio.sleep(1)
        return await getPicassoFarewell(
            dialogue=dialogue,
            attempt_count=attempt_count + 1,
            user_message=user_message,
        )


async def get_GPT_translation(text: str, source_lang: str, attempt_count: int):
    try:
        lang_dict = {"ko": "korean", "en": "english"}
        source = lang_dict[source_lang]
        target = lang_dict["ko"] if source_lang == "en" else lang_dict["en"]

        instruction = f"""
            Do liberal translation on user sentence from {source} to {target}.
        """

        messages = [{"role": "system", "content": instruction}]

        if source == "english":
            messages.extend(
                [
                    {
                        "role": "user",
                        "content": "Through art, I find truth in chaos, and beauty in imperfections.",
                    },
                    {
                        "role": "assistant",
                        "content": "저는 미술을 통해 혼란 속에서 진실을 찾고 불완전함 속에서 아름다움을 찾습니다.",
                    },
                    {"role": "system", "content": instruction},
                    {
                        "role": "user",
                        "content": "Imagination knows no boundaries; my canvas sets me free.",
                    },
                    {
                        "role": "assistant",
                        "content": "상상에는 한계가 없고 캔버스는 저를 자유롭게 합니다.",
                    },
                    {"role": "system", "content": instruction},
                    {
                        "role": "user",
                        "content": "Each stroke on the canvas reveals a piece of my soul, a story untold.",
                    },
                    {
                        "role": "assistant",
                        "content": "제가 캔버스의 그리는 부드러운 붓질들은 비밀스러운 이야기와 제 영혼의 조각들을 조금씩 들어냅니다.",
                    },
                    {"role": "system", "content": instruction},
                    {
                        "role": "user",
                        "content": "With colors as my companions, I explore the realms of the unknown.",
                    },
                    {
                        "role": "assistant",
                        "content": "저는 색깔을 친구로 삼고 미지의 세계를 탐험하고는 합니다.",
                    },
                    {"role": "system", "content": instruction},
                    {
                        "role": "user",
                        "content": "Art is a mirror reflecting the complexity and simplicity of existence.",
                    },
                    {
                        "role": "assistant",
                        "content": "미술은 복잡하면서 단순 명료한 존재들을 반사하는 거울과 같습니다.",
                    },
                    {"role": "system", "content": instruction},
                ]
            )

        messages.append({"role": "user", "content": text})

        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo", messages=messages, temperature=0
        )
        translated = completion["choices"][0]["message"]["content"]

        print("■■■■■■■■■[OPENAI TRANSLATION RESULT]■■■■■■■■■")
        print(f"Before Translation: {text}")
        print(f"After Translation: {translated}")

        return translated

    except Exception as e:
        print(
            f"🔥 utils/openai/common: [get_GPT_translation] failed {attempt_count + 1} times🔥",
            e,
        )
        if attempt_count + 1 == 3:
            print("🔥 utils/openai/common: [get_GPT_translation] max error reached🔥")
            return ""
        await asyncio.sleep(1)
        return await get_GPT_translation(
            text=text, source_lang=source_lang, attempt_count=attempt_count + 1
        )


"""
Request based function due to openai api integrity check
"""


async def whisper_speech_to_text(file, count: int):
    fallback_message = "I'm sorry can you repeat again?"
    request_timeout = 5

    try:
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        }
        data = {
            "model": "whisper-1",
            "prompt": "이것은 파블로 피카소와 그림 게르니카에 대한 대화입니다. 스페인 내전 과정에서 나타난 참혹함과 그것을 표현한 게르니카에 대해 다루고 있습니다.",
        }
        files = {
            "file": ("audio.mp3", file),
        }

        response = requests.post(
            url, headers=headers, data=data, files=files, timeout=request_timeout
        )

        if response.status_code == 200:
            result = response.json()
            transcription = result.get("text", "")
            return transcription
        else:
            print(
                f"🔥 utils/openai/common: [whisper_speech_to_text] failed. Returning fallback message 🔥: {response.status_code}"
            )
            return fallback_message
    except requests.Timeout:
        if count < 3:
            print(
                f"🔥 utils/openai/common: [whisper_speech_to_text] Timeout 🔥, Trying {count + 1} time"
            )
            return await whisper_speech_to_text(file=file, count=count + 1)
        else:
            print(
                "🔥 utils/openai/common: [whisper_speech_to_text] failed. Returning fallback message 🔥"
            )
            return fallback_message
    except Exception as e:
        print(
            "🔥 utils/openai/common: [whisper_speech_to_text] failed. Returning fallback message 🔥",
            e,
        )
        return fallback_message
