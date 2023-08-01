import openai
import asyncio


async def get_student_analysis(
    dialogue: list, user_message: str, assistant_message: str, attempt_count: int
):
    try:
        base_instruction = f"""
            [TASK]
            You are now an art education supervisor currently supervising conversation between art educator and student about the painting Guernica. 
            As a supervisor, monitor the progress of the student given [DIALOGUE] with [STUDENT MESSAGE].
            Then make a three point analysis on the student learning status and room for improvement in perspective of art education.
            
            [DIALOGUE]
            {dialogue}
            
            [STUDENT MESSAGE]
            Student: {user_message}
            
            [RULE]
            - Be concise
            
            [GOAL]
            Follow the [TASK] and generate three analysis on the student.
            
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
            As a supervisor, provide directive on how to improve educator reponse based on messages in [LATEST MESSAGE].
            Use anaysis on student provided in [ANALYSIS].
            Make a three point directive for the art educator.
            
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
