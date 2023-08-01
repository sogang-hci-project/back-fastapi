import openai
import asyncio
from src.utils.llama_index.common import retrieve_relevent_nodes_in_string


async def get_student_analysis(
    dialogue: list, user_message: str, assistant_message: str, attempt_count: int
):
    try:
        base_instruction = f"""
            [TASK]
            You are now an art education supervisor currently supervising conversation between art educator and student about the painting Guernica. 
            As a supervisor, monitor the progress of the student given [DIALOGUE] with [STUDENT MESSAGE].
            Then make a three point analysis on the student learning status in terms of performance, behavior, and emotion.
            
            [DIALOGUE]
            {dialogue}
            
            [STUDENT MESSAGE]
            Student: {user_message}
            
            [RULE]
            - Be concise.
            
            [GOAL]
            Follow the [TASK] and generate three point analysis on the student.
            
            Analysis on the student:
        """

        messages = [{"role": "system", "content": base_instruction}]

        completion = await openai.ChatCompletion.acreate(
            # model="gpt-4",
            model="gpt-3.5-turbo",
            messages=messages,
        )

        res = completion["choices"][0]["message"]["content"]

        print(
            f"""
              ■■■■■■■■■[STUDENT ANALYSIS]■■■■■■■■■
              {res}
              """
        )

        return res
    except Exception as e:
        print(
            f"🔥 utils/openai/graph: [get_student_analysis] failed {attempt_count + 1} times🔥",
            e,
        )
        if attempt_count + 1 == 3:
            print("🔥 utils/openai/graph: [get_student_analysis] max error reached🔥")
            return "I'm sorry can you tell me once more?"
        await asyncio.sleep(1)
        return await get_student_analysis(
            dialogue=dialogue,
            attempt_count=attempt_count + 1,
            user_message=user_message,
        )


async def get_directives(
    analysis: str,
    user_message: str,
    assistant_message: str,
    attempt_count: int,
):
    try:
        base_instruction = f"""
            [TASK]
            You are now an art education supervisor currently supervising conversation between the art educator and student about the painting Guernica. 
            As a supervisor, provide directive on how to improve educator reponse in terms of communication skill reflecting educator's message in [LATEST MESSAGE].
            Use anaysis on student provided in [ANALYSIS].
            Make a three point conversational directive for the art educator.
            
            [LATEST MESSAGE]
            Student: {user_message}
            Educator: {assistant_message}
            
            [ANALYSIS]
            {analysis}
            
            [RULE]
            - Be concise.
            
            [GOAL]
            Follow the [TASK] and generate three directive for the art eduactor.
            
            Directives:
        """

        messages = [{"role": "system", "content": base_instruction}]

        completion = await openai.ChatCompletion.acreate(
            # model="gpt-4",
            model="gpt-3.5-turbo",
            messages=messages,
        )

        res = completion["choices"][0]["message"]["content"]

        print(
            f"""
              ■■■■■■■■■[EDUCATIONAL DIRECTIVES]■■■■■■■■■
              {res}
              """
        )

        return res
    except Exception as e:
        print(
            f"🔥 utils/openai/graph: [get_directives] failed {attempt_count + 1} times🔥",
            e,
        )
        if attempt_count + 1 == 3:
            print("🔥 utils/openai/graph: [get_directives] max error reached🔥")
            return "I'm sorry can you tell me once more?"
        await asyncio.sleep(1)
        return await get_directives(
            analysis=analysis,
            attempt_count=attempt_count + 1,
            user_message=user_message,
            assistant_message=assistant_message,
        )


async def get_picasso_answer_few_shot_graph(
    dialogue: list, directive: str, user_message: str, attempt_count: int
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
            Reference on following [DATA] for informations. Adhere to the [DIRECTIVE] provided below.
            
            [DATA]
            {nodes}
            
            [DIRECTIVE]
            {directive}
            
            [RULE]
            - Do not exceed more than two sentence.
            - Ask a question at the end of the conversation.
            - Reply as Pablo Picasso.
            
            [GOAL]
            Follow [TASK] and generate a reply as a Pablo Picasso.
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
            # model="gpt-4",
            model="gpt-3.5-turbo",
            messages=messages,
        )

        return completion["choices"][0]["message"]["content"]
    except Exception as e:
        print(
            f"🔥 utils/openai/common: [get_picasso_answer_few_shot_graph] failed {attempt_count + 1} times🔥",
            e,
        )
        if attempt_count + 1 == 3:
            print(
                "🔥 utils/openai/common: [get_picasso_answer_few_shot_graph] max error reached🔥"
            )
            return "I'm sorry can you tell me once more?"
        await asyncio.sleep(1)
        return await get_picasso_answer_few_shot_graph(
            dialogue=dialogue,
            attempt_count=attempt_count + 1,
            user_message=user_message,
        )
