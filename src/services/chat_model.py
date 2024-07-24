from openai import OpenAI
from src.definitions.credentials import Credentials, EnvVariables
from src.prompts.prompts import SALARY_SYSTEM_PROMPT, JOB_RELEVANCE_SYSTEM_PROMPT

""" 
Tasks: 
1. Process Salary - Determine if target salary (since this is not structured) 
2. Determine if job post is relevant or matches the candidate's qualifications (Use job title and Job description)
"""


class ChatModel:
    def __init__(self):
        self.chat_model = EnvVariables.chat_model()
        self.model = OpenAI(api_key=Credentials.openai_api_key())
        self.max_tokens = 4096

    def check_salary_relevance(self, salary: str):
        value = self.chat(SALARY_SYSTEM_PROMPT, salary)
        salary_relevance, input_salary, parsed_salary, reason = value.split('####')
        return salary_relevance

    def check_job_relevance(self, title: str, description: str):
        user_prompt = f""" 
        {title}
        
        {description} 
        """
        return self.chat(JOB_RELEVANCE_SYSTEM_PROMPT, user_prompt)

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        response = self.model.chat.completions.create(
            model=self.chat_model,
            messages=messages,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content
