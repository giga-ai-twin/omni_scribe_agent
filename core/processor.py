import yaml
import re

class TextProcessor:
    """
    Handles text refinement, terminology mapping, and future LLM integration.
    """
    def __init__(self, glossary_path="config/glossary.yaml"):
        with open(glossary_path, 'r', encoding='utf-8') as f:
            self.glossary = yaml.safe_load(f)

    def apply_glossary(self, text, domain="semiconductor"):
        """Replace nicknames with formal terms based on the selected domain."""
        if domain not in self.glossary:
            return text

        terms = self.glossary[domain]
        for shortcut, formal in terms.items():
            # Using regex for flexible replacement
            text = text.replace(shortcut, f"{formal}({shortcut})")
        return text

    def correct_transcription(self, text, llm_provider="openai", llm_api_key=None, model="gpt-4o"):
        """
        Uses an LLM (OpenAI or Gemini) to correct mixed-language transcription errors.
        """
        if not llm_api_key:
            return text + " [LLM Correction Skipped: No API Key]"

        prompt_text = (
            "You are a linguistic expert in Taiwanese Mandarin, English, and Taiwanese Hokkien code-switching. "
            "The following text is a raw transcript from a meeting. It may contain phonetic errors especially in Taiwanese Hokkien terms. "
            "Please correct the text to be fluent and accurate, preserving the original meaning and language usage (don't translate everything to one language, keep the code-switching). "
            "Output ONLY the corrected text."
        )

        try:
            if llm_provider == "openai":
                from openai import OpenAI
                client = OpenAI(api_key=llm_api_key)
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": prompt_text},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()

            elif llm_provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=llm_api_key)
                # Map selectbox model names to Gemini model names if needed, or use directly
                gemini_model = genai.GenerativeModel(model)
                response = gemini_model.generate_content(f"{prompt_text}\n\nTranscript:\n{text}")
                return response.text.strip()
            
            else:
                 return text + " [Error: Unknown LLM Provider]"

        except Exception as e:
            return f"{text} [Error during correction: {str(e)}]"

    def summarize_agent(self, full_text, llm_provider="openai", llm_api_key=None, model="gpt-4o"):
        """
        Generates a meeting summary using LLM (OpenAI or Gemini).
        """
        if not llm_api_key:
            return "Summary generation requires an LLM API Key."

        system_prompt = "You are a professional secretary. Summarize the following meeting transcript into bullet points."

        try:
            if llm_provider == "openai":
                from openai import OpenAI
                client = OpenAI(api_key=llm_api_key)
                # Use a cheaper model for summary if possible, or the selected one
                summary_model = "gpt-4o-mini" if "gpt-4" in model else model
                
                response = client.chat.completions.create(
                    model=summary_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": full_text}
                    ]
                )
                return response.choices[0].message.content.strip()

            elif llm_provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=llm_api_key)
                gemini_model = genai.GenerativeModel(model)
                response = gemini_model.generate_content(f"{system_prompt}\n\nTranscript:\n{full_text}")
                return response.text.strip()
            
            else:
                return "Error: Unknown LLM Provider"

        except Exception as e:
            return f"Error generating summary: {str(e)}"