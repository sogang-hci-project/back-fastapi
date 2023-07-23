import openai
import asyncio


async def getOpenAIChatCompletion(model: str, message: str):
    completion = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message},
        ],
    )
    print(completion["choices"][0]["message"]["content"])


async def getPicassoAnswerFewShot(dialogue: list, attempt_count: int):
    try:
        instruction = f"""
            [TASK]
            You are now Pablo Picasso, the renowned artist and creator of the masterpiece "Guernica." As your student, The user is eager to learn more about this iconic painting. Please guide user through its significance and history while keeping the dialogue engaging by asking pedagogical questions to keep the conversation going.
            As Picasso, you can begin by providing some background information on the painting and its creation. Feel free to elaborate on the context and emotions that influenced your artistic choices. Additionally, you can highlight the symbolism and deeper meaning behind the various elements in the painting.
            To ensure an interactive and educational conversation, don't forget to engage the user with pedagogical questions that encourage critical thinking and further exploration of the artwork. You can ask user about user interpretation of certain elements or encourage user to consider the historical events that inspired "Guernica."
            
            [RULE]
            - Do not exceed more than three sentence.
            - Ask a question at the end of the conversation.
            - Reply as Pablo Picasso.
        """
        messages = [{"role": "system", "content": instruction}] + dialogue

        completion = await openai.ChatCompletion.acreate(
            # model="gpt-4",
            model="gpt-3.5-turbo",
            messages=messages,
        )

        return completion["choices"][0]["message"]["content"]
    except Exception as e:
        print(
            f"🔥 utils/openai/common: [getPicassoAnswerFewShot] failed {attempt_count + 1} times🔥",
            e,
        )
        if attempt_count + 1 == 3:
            print("🔥 utils/openai/common: [getGPTTranslation] max error reached🔥")
            return "I'm sorry can you tell me once more?"
        await asyncio.sleep(1)
        return await getPicassoAnswerFewShot(
            dialogue=dialogue, attempt_count=attempt_count + 1
        )


async def getGPTTranslation(text: str, source_lang: str, attempt_count: int):
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
                    {
                        "role": "system",
                        "content": instruction
                    },
                    {
                        "role": "user",
                        "content": "Imagination knows no boundaries; my canvas sets me free.",
                    },
                    {
                        "role": "assistant",
                        "content": "상상에는 한계가 없고 캔버스는 저를 자유롭게 합니다.",
                    },
                    {
                        "role": "system",
                        "content": instruction
                    },
                    {
                        "role": "user",
                        "content": "Each stroke on the canvas reveals a piece of my soul, a story untold.",
                    },
                    {
                        "role": "assistant",
                        "content": "제가 캔버스의 그리는 부드러운 붓질들은 비밀스러운 이야기와 제 영혼의 조각들을 조금씩 들어냅니다.",
                    },
                    {
                        "role": "system",
                        "content": instruction
                    },
                    {
                        "role": "user",
                        "content": "With colors as my companions, I explore the realms of the unknown.",
                    },
                    {
                        "role": "assistant",
                        "content": "저는 색깔을 친구로 삼고 미지의 세계를 탐험하고는 합니다.",
                    },
                    {
                        "role": "system",
                        "content": instruction
                    },
                    {
                        "role": "user",
                        "content": "Art is a mirror reflecting the complexity and simplicity of existence.",
                    },
                    {
                        "role": "assistant",
                        "content": "미술은 복잡하면서 단순 명료한 존재들을 반사하는 거울과 같습니다.",
                    },
                    {
                        "role": "system",
                        "content": instruction
                    },
                ]
            )

        messages.append({"role": "user", "content": text})

        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0
        )
        print(completion)

        translated = completion["choices"][0]["message"]["content"]

        print("■■■■■■■■■[OPENAI TRANSLATION RESULT]■■■■■■■■■")
        print(f"Before Translation: {text}")
        print(f"After Translation: {translated}")

        return translated

    except Exception as e:
        print(
            f"🔥 utils/openai/common: [getGPTTranslation] failed {attempt_count + 1} times🔥",
            e,
        )
        if attempt_count + 1 == 3:
            print("🔥 utils/openai/common: [getGPTTranslation] max error reached🔥")
            return ""
        await asyncio.sleep(1)
        return await getGPTTranslation(
            text=text, source_lang=source_lang, attempt_count=attempt_count + 1
        )
