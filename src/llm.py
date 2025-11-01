"""
LLM Module

This module provides a wrapper for Google Gemini API optimized for RAG applications.
"""

import os
import time
from dotenv import load_dotenv
import google.generativeai as genai


class GeminiLLM:
    """Wrapper for Google Gemini API optimized for RAG"""

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        temperature: float = 0.1,
        max_output_tokens: int = 500,
        top_p: float = 0.95,
        top_k: int = 40,
        api_key: str = None
    ):
        """
        Initialize the Gemini LLM

        Args:
            model_name: Name of the Gemini model to use
            temperature: Sampling temperature (0.0-1.0)
            max_output_tokens: Maximum tokens in generated response
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            api_key: Google AI API key (if None, loads from environment)
        """
        self.model_name = model_name

        # Load API key from environment if not provided
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "GEMINI_API_KEY not found. Please set it in .env file or pass as argument"
                )

        # Configure Gemini API
        genai.configure(api_key=api_key)

        # Generation config optimized for factual Q&A
        self.generation_config = {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_output_tokens": max_output_tokens,
        }

        # Safety settings
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )

        print(f"✅ GeminiLLM initialized with {self.model_name}")
        print(f"   Temperature: {temperature}, Max tokens: {max_output_tokens}")

    def generate(self, prompt: str, max_retries: int = 3) -> str:
        """
        Generate response with retry logic

        Args:
            prompt: The input prompt
            max_retries: Number of retry attempts on failure

        Returns:
            Generated text response
        """
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"⚠️  Attempt {attempt + 1} failed: {e}")
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ All {max_retries} attempts failed")
                    raise

    @staticmethod
    def list_available_models():
        """List all available Gemini models that support content generation"""
        print("Available Gemini models:")
        print("-" * 80)
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"Model: {model.name}")
                print(f"  Display name: {model.display_name}")
                print(f"  Supported methods: {model.supported_generation_methods}")
                print()
