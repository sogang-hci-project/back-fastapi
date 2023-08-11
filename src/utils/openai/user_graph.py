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
    def __init__(self, id: str, type: str, content: str, relation: list):
        self.id = id
        self.type = type
        self.content = content
        self.relation = relation

    def __str__(self):
        return f"<UserGraphEntity Id: {self.id}, Type: {self.type}, Content: {self.content}, Relation: {self.relation}>"

    def __repr__(self):
        return f"<UserGraphEntity Id: {self.id}, Type: {self.type}, Content: {self.content}, Relation: {self.relation}>\n"


async def extract_entity_from_user_message(
    user_message: str,
    assistant_message: str,
    attempt_count: int,
) -> List[UserGraphEntity]:
    try:
        base_instruction = """
            [TASK]
            Given the user message, extract following information.
            - FACT: Factual idea about the Student.
            - EVENT: Episode or event between the Student and the Pablo Picasso.
            - IDEA: Projected opinion or idea by the Student.
            The dialogue is about the painting Guernica. 
            Return in following [FORMAT], DO NOT OMIT
            
            [FORMAT]
            [{"type":"string", "content":"string", "entities": [{"name": "string"}, {"name": "string"}, {"name": "string"}]}]
        """

        example_message_one = """
        Pablo Picasso: Absolutely. Do you think inclusion of newspaper print has made the painting more impactful?
        Student: Yeah, I think so, because right now it's just white and black, so I think it could have a different texture or something like that.
        """

        example_return_one = '[{"type": "EVENT", "content": "Student agreed on the idea that inclusion of newspaper increased the impact.", "entities": [{"name": "Student"}, {"name": "newspaper"}, {"name": "impact"}]}, {"type": "IDEA", "content": "The Guernica could have a different texture to increase the impact.", "entities": [{"name": "Guernica"}, {"name": "texture"}, {"name": "impact"}]}]'

        example_message_two = """
        Pablo Picasso: Welcome. My name is Pablo Picasso, a spanish painter. Can you introduce yourself?
        Student: I am a 28-year-old graduate student.
        """

        example_return_two = '[{"type":"FACT","content":"The student is a 28-year-old","entities":[{"name":"28-year-old"},{"name":"graduate student"}]}, {"type":"FACT","content":"The student is a graduate student.","entities":[{"name":"graduate student"}]}]'

        new_message = f"""
        Pablo Picasso: {assistant_message}
        Student: {user_message}
        """

        messages = [
            {"role": "system", "content": base_instruction},
            {"role": "user", "content": example_message_one},
            {"role": "user", "content": example_return_one},
            {"role": "user", "content": example_message_two},
            {"role": "user", "content": example_return_two},
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
            entity_item_id = str(uuid.uuid4())
            entity_item_type = entity_item["type"] if "type" in entity_item else "MISC"
            entity_item_content = (
                entity_item["content"] if "content" in entity_item else "none"
            )
            return_list.append(
                UserGraphEntity(
                    id=entity_item_id,
                    type=entity_item_type,
                    content=entity_item_content,
                    relation=[],
                )
            )
            related_entities = (
                entity_item["entities"] if "entities" in entity_item else []
            )
            for sub_entity_item in related_entities:
                sub_entity_item_id = str(uuid.uuid4())
                sub_entity_item_type = "ENTITY"
                sub_entity_item_content = (
                    sub_entity_item["name"] if "name" in sub_entity_item else "none"
                )
                sub_entity_item_relations = [entity_item_id, sub_entity_item_id]

                return_list.append(
                    UserGraphEntity(
                        id=sub_entity_item_id,
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
