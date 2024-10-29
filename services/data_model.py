import logging
import os
from groq import Groq

logger = logging.getLogger(__name__)

class DataModelService:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ API key not found in environment variables")

        self.client = Groq(api_key=self.api_key)
        self.model_name = "llama3-8b-8192"  # Replace with specific model name if necessary

    def query_model(self, prompt: str) -> str:
        """
        Envoie le prompt au modèle Ollama via l'API GROQ et retourne la réponse.

        Args:
            prompt (str): Le prompt à envoyer au modèle
        Returns:
            str: La réponse du modèle
        Raises:
            Exception: Si la requête échoue
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
            )

            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error querying Ollama model: {str(e)}")
            raise Exception("Failed to query the model.")

    def process_query(self, query: str) -> str:
        """
        Process a query and return a response using the model from Ollama via GROQ API.

        Args:
            query (str): The query

        Returns:
            str: The response

        Raises:
            ValueError: If the query is empty or invalid
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        try:
            # Clean up the query by removing extra spaces and normalizing
            cleaned_query = query.strip()

            # Use the Ollama model to process the query
            response = self.query_model(cleaned_query)
            logger.info(f"Model response for query: {query}")
            return response

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise Exception(f"Query processing failed: {str(e)}")