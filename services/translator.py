import requests
import os
from typing import Optional, Dict, Any
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class TranslationError(Exception):
    """Custom exception for translation-related errors"""
    pass

class TranslationService:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_TRANSLATE_API_KEY')
        if not self.api_key:
            raise ValueError("Google Translate API key not found in environment variables")
        
        self.base_url = "https://translation.googleapis.com/language/translate/v2"
        self.supported_languages = {'wo': 'Wolof', 'en': 'English'}
        
        # Configure logging for request/response tracking
        self.request_id = 0

    def get_request_id(self) -> str:
        """Generate a unique request ID for tracking"""
        self.request_id += 1
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"{timestamp}-{self.request_id}"

    def validate_language_codes(self, source_lang: str, target_lang: str) -> None:
        """
        Validate the language codes
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
            
        Raises:
            TranslationError: If language codes are invalid
        """
        if source_lang not in self.supported_languages:
            logger.error(f"Unsupported source language: {source_lang}")
            raise TranslationError(f"Unsupported source language: {source_lang}")
        if target_lang not in self.supported_languages:
            logger.error(f"Unsupported target language: {target_lang}")
            raise TranslationError(f"Unsupported target language: {target_lang}")

    def validate_translation_response(self, response_data: Dict[str, Any]) -> None:
        """
        Validate the translation API response format
        
        Args:
            response_data: Response data from translation API
            
        Raises:
            TranslationError: If response format is invalid
        """
        if not isinstance(response_data, dict):
            raise TranslationError("Invalid response type from translation service")
            
        if 'data' not in response_data:
            raise TranslationError("Missing 'data' in translation response")
            
        if 'translations' not in response_data['data']:
            raise TranslationError("Missing 'translations' in translation response")
            
        translations = response_data['data']['translations']
        if not translations or not isinstance(translations, list):
            raise TranslationError("Invalid translations format in response")
            
        if 'translatedText' not in translations[0]:
            raise TranslationError("Missing translated text in response")

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text using Google Cloud Translation API
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            str: Translated text
            
        Raises:
            TranslationError: If translation fails or validation fails
            ValueError: If input parameters are invalid
        """
        if not text or not isinstance(text, str):
            logger.error("Invalid input: text must be a non-empty string")
            raise ValueError("Text must be a non-empty string")

        request_id = self.get_request_id()
        logger.info(f"[{request_id}] Starting translation request")
        logger.info(f"[{request_id}] From {self.supported_languages[source_lang]} to {self.supported_languages[target_lang]}")
        logger.info(f"[{request_id}] Input text: {text[:100]}{'...' if len(text) > 100 else ''}")

        try:
            # Validate language codes
            self.validate_language_codes(source_lang, target_lang)
            
            # Clean up input text
            text = text.strip()
            
            params = {
                "q": text,
                "source": source_lang,
                "target": target_lang,
                "key": self.api_key
            }
            
            logger.info(f"[{request_id}] Sending request to translation API")
            
            response = requests.post(self.base_url, params=params, timeout=10)
            
            logger.info(f"[{request_id}] Received response with status code: {response.status_code}")
            
            if response.status_code == 400:
                error_data = response.json().get('error', {})
                error_message = error_data.get('message', 'Invalid request')
                logger.error(f"[{request_id}] Translation API validation error: {error_message}")
                raise TranslationError(f"Translation request invalid: {error_message}")
                
            elif response.status_code == 403:
                logger.error(f"[{request_id}] Translation API authentication failed")
                raise TranslationError("Authentication failed. Please check your API key.")
                
            elif response.status_code != 200:
                logger.error(f"[{request_id}] Translation API error: Status {response.status_code}")
                raise TranslationError(f"Translation service error: HTTP {response.status_code}")
            
            try:
                result = response.json()
                self.validate_translation_response(result)
                
                translation = result['data']['translations'][0]['translatedText']
                if not translation:
                    logger.error(f"[{request_id}] Empty translation received")
                    raise TranslationError("Empty translation received")
                
                logger.info(f"[{request_id}] Successfully translated text")
                logger.info(f"[{request_id}] Translation result: {translation[:100]}{'...' if len(translation) > 100 else ''}")
                return translation
                
            except json.JSONDecodeError as e:
                logger.error(f"[{request_id}] Failed to parse translation response: {str(e)}")
                raise TranslationError("Invalid response format from translation service")

        except requests.exceptions.Timeout:
            logger.error(f"[{request_id}] Translation request timed out")
            raise TranslationError("Translation service timeout. Please try again.")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[{request_id}] Translation request failed: {str(e)}")
            raise TranslationError(f"Translation service error: {str(e)}")
            
        except Exception as e:
            logger.error(f"[{request_id}] Unexpected error during translation: {str(e)}")
            raise TranslationError(f"Translation failed: {str(e)}")
