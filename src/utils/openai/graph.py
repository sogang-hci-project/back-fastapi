import openai
import asyncio


async def get_instructor_comment(
    dialogue: list, user_message: str, assistant_message: str, attempt_count: int
):
    try:
        base_instruction = f"""
            [TASK]
            You are now an art education supervisor currently supervising conversation between art educator and student about the painting Guernica. 
            As a supervisor, monitor the progress of the student given [DIALOGUE] with [LATEST MESSAGE] and offer constructive guideline to the art educator. 
            Please ensure that the art educator encourages a supportive and nurturing environment during the session. Offer pedagogic strategies based on the current student's state. 
            Promote an open dialogue with self-expression and feedback based on emotional understanding. 

            [DIALOGUE]
            {dialogue}
            
            [LATEST MESSAGE]
            Student: {user_message}
            Educator: {assistant_message}
            
            [RULE]
            - Do not exceed more than five sentence.
            
            [GOAL]
            Follow the [TASK] and offer a guideline to the art educator.
            
            Art Education Supervisor:
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
              ■■■■■■■■■[SUPERVISOR COMMENT]■■■■■■■■■
              {res}
              """
        )

        return res
    except Exception as e:
        print(
            f"🔥 utils/openai/graph: [get_instructor_comment] failed {attempt_count + 1} times🔥",
            e,
        )
        if attempt_count + 1 == 3:
            print("🔥 utils/openai/graph: [get_instructor_comment] max error reached🔥")
            return "I'm sorry can you tell me once more?"
        await asyncio.sleep(1)
        return await get_instructor_comment(
            dialogue=dialogue,
            attempt_count=attempt_count + 1,
            user_message=user_message,
        )
