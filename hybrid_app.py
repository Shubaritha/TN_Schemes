from flask import Flask, request, jsonify, render_template
from hybrid_schemes_chatbot import HybridSchemesChatbot
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError
import ssl
import os

app = Flask(__name__)

def get_chatbot():
    if not hasattr(app, 'chatbot'):
        try:
            app.chatbot = HybridSchemesChatbot()
        except (ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError) as e:
            print(f"MongoDB Connection Error: {str(e)}")
            # Implement fallback or error handling
            raise
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise
    return app.chatbot

@app.route('/')
def home():
    try:
        # Test database connection on home page load
        chatbot = get_chatbot()
        return render_template('index.html')
    except Exception as e:
        return f"Error connecting to database: {str(e)}", 500

@app.route('/get_response', methods=['POST'])
def get_bot_response():
    try:
        user_message = request.json.get('message', '').strip()
        if not user_message:
            return jsonify({'response': 'Please enter a message.'})
        
        chatbot = get_chatbot()
        response = chatbot.get_response(user_message)
        
        if not response:
            response = "I'm sorry, I couldn't understand your query. Please try asking about specific schemes or use commands like 'list all schemes' or 'help'."
        
        return jsonify({'response': response})
        
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({
            'response': 'Sorry, there was an error processing your request. Please try again.'
        }), 500

@app.route('/get_suggestions', methods=['GET'])
def get_suggestions():
    """Return common suggestion categories for the chatbot"""
    suggestions = [
        {"text": "List all schemes", "query": "List all schemes"},
        {"text": "Education schemes", "query": "Education schemes"},
        {"text": "Health schemes", "query": "Health schemes"},
        {"text": "Schemes for women", "query": "Schemes for women"},
        {"text": "Agriculture schemes", "query": "Agriculture schemes"},
        {"text": "Housing schemes", "query": "Housing schemes"},
        {"text": "Help", "query": "Help"}
    ]
    return jsonify(suggestions)

@app.teardown_appcontext
def close_db_connection(error):
    """Close the MongoDB connection when the app context tears down"""
    if hasattr(app, 'chatbot'):
        app.chatbot.close()
        delattr(app, 'chatbot')

if __name__ == '__main__':
    # Initialize chatbot to ensure intents are loaded
    with app.app_context():
        chatbot = get_chatbot()
    app.run(debug=True) 