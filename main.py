from flask import Flask, request, jsonify, render_template
import logging
from dotenv import load_dotenv
from services.translator import TranslationService
from services.data_model import DataModelService

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
translation_service = TranslationService()
data_model_service = DataModelService()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_query():
    try:
        data = request.get_json()
        wolof_query = data.get('query', '')

        if not wolof_query:
            return jsonify({'error': 'No query provided'}), 400

        # Step 1: Translate Wolof to French
        logger.info(f"Translating query from Wolof to French: {wolof_query}")
        french_query = translation_service.translate(
            text=wolof_query,
            source_lang='wo',  # Wolof language code
            target_lang='en'   # French language code
        )

        # Step 2: Process the query with data model
        logger.info(f"Processing French query: {french_query}")
        french_response = data_model_service.process_query(french_query)

        # Step 3: Translate response back to Wolof
        logger.info(f"Translating response to Wolof: {french_response}")
        wolof_response = translation_service.translate(
            text=french_response,
            source_lang='en',  # French language code
            target_lang='wo'   # Wolof language code
        )

        return jsonify({
            'original_query': wolof_query,
            'french_query': french_query,
            'french_response': french_response,
            'wolof_response': wolof_response
        })

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
