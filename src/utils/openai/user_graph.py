import openai
import asyncio
import json
import uuid
from typing import List
from src.utils.llama_index.common import retrieve_relevent_nodes_in_string
from src.utils.common import neo4j_entities
from src.utils.neo4j.common import Neo4jNode
from src.utils.llama_index.chroma import retreive_node_by_id


class UserGraphEntity:
    def __init__(self, type: str, content: str, relation: list):
        self.type = type
        self.content = content
        self.relation = relation

    def __str__(self):
        return f"<UserGraphEntity Type: {self.type}, Content: {self.content}, Relation: {self.relation}>"

    def __repr__(self):
        return f"<UserGraphEntity Type: {self.type}, Content: {self.content}, Relation: {self.relation}>\n"


async def extract_entity_from_user_message(
    user_message: str,
    assistant_message: str,
    attempt_count: int,
) -> List[UserGraphEntity]:
    try:
        base_instruction = """
            [TASK]
            Given the user message, extract following informations.
            - FACT: Factual information or evaluation about the student.
            - EVENT: Episode or event between the student and the picasso.
            - IDEA: Projected opinion or idea by the student.
            Extract at least one for each FACT, EVENT, and IDEA.
            The dialogue is about the painting Guernica. 
            Return in following [FORMAT], DO NOT OMIT
            
            [FORMAT]
            [{"type":"string", "content":"string", "entities": [{"name": "string"}, {"name": "string"}, {"name": "string"}]}]
        """

        example_message_one = """
        picasso: Absolutely. Do you think inclusion of newspaper print has made the painting more impactful?
        student: Yeah, I think so, because right now it's just white and black, so I think it could have a different texture or something like that.
        """

        example_return_one = '[{"type": "EVENT", "content": "student agreed on the idea that inclusion of newspaper increased the impact.", "entities": [{"name": "student"}, {"name": "newspaper"}, {"name": "impact"}]}, {"type": "IDEA", "content": "The Guernica could have a different texture to increase the impact.", "entities": [{"name": "Guernica"}, {"name": "texture"}, {"name": "impact"}]}, {"type": "FACT", "content": "student is likely agree on idea when given specific detail", "entities": [{"name": "idea"}, {"name": "student"}, {"name": "detail"}]}]'

        example_message_two = """
        picasso: Welcome. My name is picasso, a spanish painter. Can you introduce yourself?
        student: I am a 28-year-old graduate student.
        """

        example_return_two = '[{"type": "FACT", "content": "The student is a 28-year-old", "entities": [{"name": "28-year-old"}, {"name": "graduate student"}]}, {"type": "FACT", "content": "The student is a graduate student.", "entities": [{"name": "graduate student"}]}, {"type": "EVENT", "content": "picasso and student exchanged welcoming conversation.", "entities": [{"name": "conversation"}, {"name": "picasso"}, {"name": "student"}]}, {"type": "IDEA", "content": "student identifies as 28 years old", "entities": [{"name": "student"}, {"name": "identification"}]}]'

        example_message_three = """
        picasso: That's an insightful observation. So, would you say that the choice of color, or in this case the lack of it, can have as much impact as the subject matter itself in a painting?
        student: Yes, I think so, and I think it would have been difficult to reveal more of what I was trying to say if I had revealed this distracting picture with something colored.
        """

        example_return_three = '[{"type": "IDEA", "content": "Choice of color can impact the matter of painting, such as meaning", "entities": [{"name": "meaning"}, {"name": "color"}, {"name": "impact"}, {"name": "painting"}]}, {"type": "EVENT", "content": "The student strengthens the view by agreeing to affirming question by picasso", "entities": [{"name": "picasso"}, {"name": "view"}, {"name": "agreement"}, {"name": "student"}]}, {"type": "FACT", "content": "The student can build a hypothesis and imagine the consequence.", "entities": [{"name": "student"}, {"name": "hypothesis"}, {"name": "consequence"}]}]'

        new_message = f"""
        picasso: {assistant_message}
        student: {user_message}
        """

        messages = [
            {"role": "system", "content": base_instruction},
            {"role": "user", "content": example_message_one},
            {"role": "user", "content": example_return_one},
            {"role": "user", "content": example_message_two},
            {"role": "user", "content": example_return_two},
            {"role": "user", "content": example_message_three},
            {"role": "user", "content": example_return_three},
            {"role": "user", "content": new_message},
            {"role": "system", "content": base_instruction},
        ]

        completion = await openai.ChatCompletion.acreate(
            # model="gpt-4",
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0,
        )

        res = completion["choices"][0]["message"]["content"]
        res_json = json.loads(res)
        return_list = []

        for entity_item in res_json:
            entity_item_type = entity_item["type"] if "type" in entity_item else "MISC"
            entity_item_content = (
                entity_item["content"] if "content" in entity_item else "none"
            )
            return_list.append(
                UserGraphEntity(
                    type=entity_item_type,
                    content=entity_item_content,
                    relation=[],
                )
            )
            related_entities = (
                entity_item["entities"] if "entities" in entity_item else []
            )
            for sub_entity_item in related_entities:
                sub_entity_item_type = "ENTITY"
                sub_entity_item_content = (
                    sub_entity_item["name"] if "name" in sub_entity_item else "none"
                )
                sub_entity_item_relations = [
                    entity_item_content,
                    sub_entity_item_content,
                ]

                return_list.append(
                    UserGraphEntity(
                        type=sub_entity_item_type,
                        content=sub_entity_item_content,
                        relation=sub_entity_item_relations,
                    )
                )

        print(
            f"""
■■■■■■■■■[User-Graph-Entity-Extraction]■■■■■■■■■
Extracted {len(return_list)} of entities
              """
        )

        return return_list
    except Exception as e:
        print(
            f"🔥 utils/openai/user_graph: [extract_entity_from_user_message] failed {attempt_count + 1} times🔥",
            e,
        )
        if attempt_count + 1 == 3:
            print(
                "🔥 utils/openai/user_graph: [extract_entity_from_user_message] max error reached🔥"
            )
            return []
        await asyncio.sleep(1)
        return await extract_entity_from_user_message(
            assistant_message=assistant_message,
            attempt_count=attempt_count + 1,
            user_message=user_message,
        )
