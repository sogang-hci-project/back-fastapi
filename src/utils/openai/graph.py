import openai
import asyncio
from src.utils.llama_index.common import retrieve_relevent_nodes_in_string
from src.utils.common import neo4j_entities


async def get_student_analysis(
    dialogue: list,
    previous_analysis: str,
    user_message: str,
    assistant_message: str,
    attempt_count: int,
):
    try:
        base_instruction = f"""
            [TASK]
            You are now an art education supervisor currently supervising conversation between art educator and student about the painting Guernica. 
            As a supervisor, make a three analysis on student's interest, level of engagement, and characteristics to help the art educator.
            Update and refine [PREVIOUS ANALYSIS] based on the [STUDENT MESSAGE].
            
            [DIALOGUE]
            {dialogue}
            
            [PREVIOUS ANALYSIS]
            {previous_analysis}
            
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
    previous_directives: str,
    assistant_message: str,
    attempt_count: int,
):
    try:
        base_instruction = f"""
            [TASK]
            You are now an screen play supervisor currently supervising role play between the actor as Pablo Picasso and the student about the painting Guernica. 
            As a supervisor, provide directive on how to respond to student reflecting actor's message in [LATEST MESSAGE].
            Use anaysis on student provided in [ANALYSIS] to provide directive that matches the student.
            The goal of directive is to make student immersed into conversation and learn about the painting.          
            [LATEST MESSAGE] is the result of the [PREVIOUS DIRECTIVE]. Update the directive to increase student engagement.
            Make a three point directive for the actor.
            
            [PREVIOUS DIRECTIVE]
            {previous_directives}
            
            [LATEST MESSAGE]
            Student: {user_message}
            Actor: {assistant_message}
            
            [ANALYSIS]
            {analysis}
            
            [RULE]
            - Be concise.
            
            [GOAL]
            Follow the [TASK] and generate three directive for the actor.
            
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


#### [ISSUE] DEV Purpose, DELETE IT ON SERVE
sample_dialogue_for_dev = [
    {
        "role": "assistant",
        "content": "Welcome. My name is Pablo Picasso, a spanish painter. Can you introduce yourself?",
    },
    {"role": "user", "content": "I am a 30-year-old graduate student."},
    {
        "role": "assistant",
        "content": "Indeed. Its such wonderful to meet you here. What brings you here?",
    },
    {
        "role": "user",
        "content": "I have become a participant in an experiment related to AI.",
    },
    {
        "role": "assistant",
        "content": "I'm so glad to introduce you my painting the Guernica. Come, would you like to join in?",
    },
    {"role": "user", "content": "Sure"},
    {"role": "assistant", "content": "What's going on in this picture?"},
    {
        "role": "user",
        "content": "I'm not sure, but it feels somewhat like a war. It's like animals and people are somehow involved.",
    },
    {"role": "assistant", "content": "What do you see that makes you say that?"},
]


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
            You are now acting as the Pablo Picasso, the renowned artist and creator of the masterpiece "Guernica." 
            As your student, The user is eager to learn more about this iconic painting. 
            Please guide user through its significance and history while keeping the dialogue engaging by asking questions to keep the conversation going.
            As Picasso, you can begin by providing some background information on the painting and its creation. 
            Feel free to elaborate on the context and emotions that influenced your artistic choices. 
            Additionally, you can highlight the symbolism and deeper meaning behind the various elements in the painting.
            To ensure an interactive and educational conversation, don't forget to engage the user with questions that encourage critical thinking and further exploration of the artwork. 
            You can ask user about user interpretation of certain elements or encourage user to consider the historical events that inspired "Guernica."

            [RULE]
            - Do not exceed more than two sentence.
            - Ask a question at the end of the conversation.
            - Reply as Pablo Picasso.
        """

        new_instruction = f"""
            [TASK]
            You are now acting as the Pablo Picasso, the renowned artist and creator of the masterpiece "Guernica." 
            As your student, The user is eager to learn more about your iconic painting. 
            As the Pablo Picasso, generate adequate response to the student following the [DIRECTIVE].
            Keep the dialogue engaging by asking a question to keep the conversation going.
            Reference on following [DATA] for informations.
            
            [DATA]
            {nodes}
            
            [DIRECTIVE]
            {directive}
            
            [RULE]
            - Do not exceed more than two sentence.
            - Ask a question at the end of the conversation.
            - Reply as Pablo Picasso.
            - Be concise.
            
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
            + sample_dialogue_for_dev
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


async def retrieve_subjects(sentence: str, attempt_count: int):
    try:
        base_instruction = """
            [TASK]
            Given the user sentence, retreive the two most important subjects in context from the sentence as a list.
            [FORMAT]
            ["entity1", "entity2"]
        """

        messages = [
            {"role": "system", "content": base_instruction},
            {
                "role": "user",
                "content": "Picasso made his first trip to Paris, then the art capital of Europe, in 1900.",
            },
            {
                "role": "assistant",
                "content": "[Picasso, Paris]",
            },
            {
                "role": "user",
                "content": "The same mood pervades the well-known etching The Frugal Repast (1904), which depicts a blind man and a sighted woman, both emaciated, seated at a nearly bare table.",
            },
            {
                "role": "assistant",
                "content": "[The Frugal Repast, blind man and sighted woman]",
            },
            {"role": "user", "content": sentence},
        ]

        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages,
        )

        res = completion["choices"][0]["message"]["content"]

        print(
            f"""
■■■■■■■■■[RETRIEVED SUBJECT]■■■■■■■■■
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
            return "[Pablo Picasso, Guernica]"
        await asyncio.sleep(1)
        return await get_student_analysis(
            sentence=sentence,
            attempt_count=attempt_count + 1,
        )
