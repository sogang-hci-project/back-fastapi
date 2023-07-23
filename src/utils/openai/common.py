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
        """
        messages = [{"role": "system", "content": instruction}] + dialogue

        completion = await openai.ChatCompletion.acreate(
            # model="gpt-4", messages=messages
            model="gpt-3.5-turbo", messages=messages
        )

        print(completion)

        return completion["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"🔥 utils/openai/common: [getPicassoAnswerFewShot] failed {attempt_count + 1} times🔥", e)
        if attempt_count > 3: return "I'm sorry can you tell me once more?"
        await asyncio.sleep(1)
        return getPicassoAnswerFewShot(dialogue=dialogue, attempt_count=attempt_count)
