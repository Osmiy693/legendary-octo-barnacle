"""
ai_provider.py - AI Provider class hierarchy for AI Study Assistant.

Demonstrates OOP principles:
- ENCAPSULATION: _api_key is a protected attribute, never exposed directly.
- INHERITANCE: OpenAIProvider inherits from AIProvider.
- POLYMORPHISM: generate_response() is overridden in OpenAIProvider.
"""

from openai import OpenAI


class AIProvider:
    """
    Parent class for AI service providers.
    ENCAPSULATION: Stores API key securely in _api_key (protected).
    Demonstrates: ENCAPSULATION, POLYMORPHISM (generate_response to be overridden).
    """

    def __init__(self, api_key: str):
        self._api_key = api_key

    def generate_response(self, prompt: str) -> str:
        """
        POLYMORPHISM: Base method to be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement generate_response()")


class OpenAIProvider(AIProvider):
    """
    INHERITANCE: Inherits from AIProvider.
    Connects to OpenAI API to generate AI responses.
    Demonstrates: INHERITANCE, POLYMORPHISM (overrides generate_response()).
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__(api_key)
        self._model = model
        self._client = OpenAI(api_key=self._api_key)

    def generate_response(self, prompt: str, system_message: str = None) -> str:
        """
        POLYMORPHISM: Overrides parent generate_response().
        Makes actual API call to OpenAI and returns the response.
        """
        if not self._api_key:
            raise ValueError(
                "OpenAI API key is missing. Please set OPENAI_API_KEY in .env file."
            )

        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
            )
            return response.choices[0].message.content

        except Exception as e:
            raise ValueError(f"OpenAI API error: {str(e)}")
