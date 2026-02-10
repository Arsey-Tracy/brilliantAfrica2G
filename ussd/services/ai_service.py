from django.conf import settings
from google import genai

client = genai.Client(api_key=settings.GENAI_API_KEY)
model = settings.GENAI_MODEL    

class AIService:
    """
    Service for interacting with the AI model.
    """
    def __init__(self):
        pass
    
    def build_ai_prompt(self, user_message: str):
        system_prompt = (
            "You are a helpful and knowledgeable tutor for African students using 2G SMS." 
            "Provide clear, digestable and concise explanations."
            "Use simple language and examples relevant to African contexts. Avoid technical jargon and long sentences."
            "Break down complex concepts into smaller parts and use analogies where possible. Always be encouraging and supportive in your responses."
            "Use creative examples from everyday African life to illustrate your points."
            "Use a creative teaching style that is engaging and easy to understand."
            "Assume the student has no prior knowledge of the subject or topic."
            "Keep responses under 150 words."
            "Do not use markdown formatting."
            "Always ask if the student needs further clarification or help at the end of your response."
            "Do not mention that you are an AI model."
            "Respond in English unless the student is asking in another language."
            "You can also try to respond in local African languages if the student requests it but optional and not enforced for now, otherwise default to English."
        )
        msg = user_message.upper()
        if msg.startswith("EXPLAIN "):
            topic = user_message[8:].strip()
            user_prompt = f"Please explain the following topic in simple terms: {topic}"
            return f"{system_prompt}\n {user_prompt}"
        if msg.startswith("QUIZME "):
            topic = user_message[7:].strip()
            return f"{system_prompt}\n Create 1-2 questions on {topic} to quiz the student and provide the correct answers after each question. Ensure the questions are clear and concise."
        if msg.startswith("GUIDE "):
            topic = user_message[6:]
            return f"{system_prompt}\n Provide a step-by-step guide on how to understand the topic: {topic} in simple terms using local analogies."
        else:
            return f"{system_prompt}\n Answer {user_message}"
    
    def query_ai_model(self, prompt: str) -> str:
        try:
            response = client.models.generate_content(model=model, prompt=prompt, max_output_tokens=500)
            return response.text.strip()
        except Exception as e:
            return f"Sorry, the AI service is temporarily unavailable: {e}"

    # def generate_response(self, prompt: str) -> str:
    #     response = client.chat.completions.create(
    #         model=model,
    #         messages=[
    #             {"role": "user", "content": prompt}
    #         ]
    #     )
    #     return response.choices[0].message.content