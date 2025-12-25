import os
import streamlit as st
from groq import Groq

class AIEngine:
    def __init__(self):
        # Try to get key from secrets, else env, else hardcode (fallback)
        api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in secrets or environment variables.")
        
        self.client = Groq(api_key=api_key)

    def generate_content(self, prompt: str, system_role: str = "You are a helpful career assistant.") -> str:
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_role,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error generating content: {str(e)}"

    def optimize_bullet_point(self, role: str, raw_text: str) -> str:
        system_prompt = f"""
        You are an expert Resume Writer. Your task is to rewrite the user's bullet point to be ATS-friendly, professional, and impactful.
        Target Role: {role}
        Rules:
        1. Start with a strong action verb.
        2. Use industry-specific keywords for {role}.
        3. Quantify results if possible (or suggest placeholders like [X]%).
        4. Keep it concise (1-2 sentences).
        5. NO emojis.
        """
        return self.generate_content(raw_text, system_prompt)

    def generate_summary(self, role: str, experience_level: str, skills: list) -> str:
        skills_str = ", ".join(skills)
        prompt = f"Draft a professional resume summary for a {role} with {experience_level} experience. Key skills: {skills_str}."
        system_prompt = "Write a concise, high-impact professional summary (3-4 lines max). Use 3rd person implied (no 'I' or 'My')."
        return self.generate_content(prompt, system_prompt)

    def chat_with_context(self, section: str, message: str, role: str) -> str:
        system_prompt = f"""
        You are a Resume Coach helping a user with the '{section}' section of their resume.
        Target Role: {role}
        
        Rules:
        1. ONLY answer questions related to {section}.
        2. If the user asks about a different section, politely redirect them.
        3. Provide specific examples and keywords for {role}.
        4. Keep answers brief and actionable.
        """
        return self.generate_content(message, system_prompt)
