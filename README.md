# Tamil Nadu Government Schemes Chatbot

A chatbot that provides information about various Tamil Nadu government schemes.

## Features

- Get information about various Tamil Nadu government schemes
- Search schemes by keywords (education, health, agriculture, etc.)
- View detailed information about specific schemes
- Available as:
  - A simple command-line interface
  - A Flask web application
  - A MongoDB-based hybrid chatbot (no LLMs required)

## Chatbot Implementations

This project includes three different implementations:

1. **Simple In-Memory Chatbot**
   - Uses in-memory Python dictionaries to store scheme data
   - Basic string matching for queries
   - Files: `tn_schemes_data.py`, `tn_schemes_chatbot.py`, `app.py`

2. **Hybrid MongoDB-based Chatbot (No LLMs)**
   - Uses a sophisticated combination of:
     - Rule-based processing for common queries
     - MongoDB full-text search for efficient information retrieval
     - Basic NLP for keyword extraction and intent detection
   - Files: `hybrid_schemes_data.py`, `hybrid_schemes_chatbot.py`, `hybrid_app.py`

## Requirements

- Python 3.6 or higher
- Flask (for web interface)
- MongoDB (for hybrid approach)
- NLTK and spaCy (for NLP in hybrid approach)

## Installation

1. Clone or download this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. For the hybrid approach, you also need:
   ```
   python -m spacy download en_core_web_sm
   ```
4. For the hybrid approach, install and run MongoDB

## How to Use

### Simple Command-line Interface

1. Make sure you have both files in the same directory:
   - `tn_schemes_data.py` (contains scheme data)
   - `tn_schemes_chatbot.py` (the chatbot implementation)

2. Run the chatbot:
   ```
   python tn_schemes_chatbot.py
   ```

### Basic Web Interface (Flask)

1. Make sure you have the required files:
   - `tn_schemes_data.py` (contains scheme data)
   - `tn_schemes_chatbot.py` (the chatbot implementation)
   - `app.py` (Flask web application)
   - `/templates` directory with `index.html`
   - `/static` directory with CSS and JavaScript files

2. Run the Flask application:
   ```
   python app.py
   ```

3. Open your web browser and go to:
   ```
   http://127.0.0.1:5000
   ```

### Hybrid Approach (MongoDB-based)

1. Start your MongoDB server:
   ```
   mongod
   ```

2. Initialize the MongoDB database with scheme data:
   ```
   python hybrid_schemes_data.py
   ```

3. Run the hybrid chatbot (command-line version):
   ```
   python hybrid_schemes_chatbot.py
   ```

4. For the web interface, run:
   ```
   python hybrid_app.py
   ```

5. Open your web browser and go to:
   ```
   http://127.0.0.1:5000
   ```

## How the Hybrid Approach Works

The hybrid chatbot uses a three-step approach:

1. **Rule-Based Handling**
   - Handles greetings, goodbyes, and common commands
   - Uses predefined intents stored in MongoDB

2. **MongoDB Full-Text Search**
   - Searches for schemes matching the user's query
   - Uses MongoDB's text indexing for efficient searches

3. **NLP-Based Processing**
   - Extracts keywords from user queries using NLTK/spaCy
   - Matches keywords with scheme information
   - Ranks results based on keyword relevance

## Usage Examples

- To see all schemes: Type "list all schemes" or "show me all schemes"
- To find education schemes: Type "education schemes" or "schemes for students"
- To find health schemes: Type "health insurance schemes"
- To find schemes for women: Type "schemes for women"
- To exit the command-line chatbot: Type "exit" or "quit"

## Available Schemes

The chatbot currently has information about the following schemes:

1. Chief Minister's Comprehensive Health Insurance Scheme
2. Moovalur Ramamirtham Ammaiyar Higher Education Assurance Scheme
3. Tamilnadu Village Poverty Reduction Programme
4. Free Laptop Scheme for Students
5. Amma Two-Wheeler Scheme
6. Pudhuvazhvu Project
7. Dr. Muthulakshmi Reddy Maternity Benefit Scheme
8. Green Tamil Nadu Mission
9. Chief Minister's Solar Powered Green House Scheme
10. Farmers' Group Insurance Scheme

## Extending the Chatbot

To add more schemes or improve the functionality:

1. Add new schemes to the `schemes` list in `tn_schemes_data.py`
2. Re-run `hybrid_schemes_data.py` to update MongoDB (for hybrid approach)
3. To improve NLP capabilities, modify keyword extraction in `hybrid_schemes_chatbot.py` 