"""
Hybrid approach chatbot for Tamil Nadu government schemes using:
1. Rule-based processing
2. MongoDB full-text search
3. Basic NLP for keyword extraction and intent detection
"""
import re
import random
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.errors import ConnectionFailure, OperationFailure
import spacy
from urllib.parse import quote_plus

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Initialize spaCy for better NLP processing
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Spacy model not found. You can install it with: python -m spacy download en_core_web_sm")
    # Fall back to NLTK if spaCy model is not available
    nlp = None

class HybridSchemesChatbot:
    def __init__(self, mongodb_uri="mongodb+srv://shubaritha02:Shubbi%4016@cluster0.aed8zs1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"):
        # Connect to MongoDB Atlas with explicit TLS settings
        try:
            self.client = MongoClient(
                mongodb_uri,
                tls=True,
                tlsAllowInvalidCertificates=True,  # Only for development/testing
                serverSelectionTimeoutMS=5000
            )
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client.TamilNaduSchemesDB
            
            # Initialize our collections
            self.schemes_collection = self.db.Schemes
            self.intents_collection = self.db.Intents
            self.user_queries_collection = self.db.User_Query
            
            # Create text indexes if they don't exist
            self._ensure_indexes()
            
            # Initialize NLTK tools
            self.stop_words = set(stopwords.words('english'))
            self.stemmer = PorterStemmer()
            
            # Check if collections exist and have data
            if self.schemes_collection.count_documents({}) == 0:
                print("Warning: Schemes collection is empty. Please ensure data is uploaded to MongoDB Atlas.")
            if self.intents_collection.count_documents({}) == 0:
                print("Warning: Intents collection is empty. Please ensure intents are uploaded to MongoDB Atlas.")
            
        except (ConnectionFailure, OperationFailure) as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise

    def _ensure_indexes(self):
        """Create necessary indexes if they don't exist"""
        try:
            # Create text index for schemes collection
            self.schemes_collection.create_index([
                ("name", TEXT),
                ("description", TEXT),
                ("eligibility", TEXT),
                ("benefits", TEXT),
                ("keywords", TEXT)
            ])
            
            # Create text index for intents collection
            self.intents_collection.create_index([
                ("patterns", TEXT),
                ("intent", TEXT)
            ])
            
        except OperationFailure as e:
            print(f"Warning: Failed to create index: {e}")
            pass

    def preprocess_text(self, text):
        """Preprocess the text by converting to lowercase, tokenizing, and stemming"""
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^\w\s]', '', text.lower())
        
        # Tokenize and remove stop words
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if word not in self.stop_words]
        
        # Stem words
        stemmed_tokens = [self.stemmer.stem(word) for word in tokens]
        
        return {
            'original': text,
            'tokens': tokens,
            'stemmed': stemmed_tokens
        }
    
    def extract_keywords(self, text):
        """Extract keywords using NLTK"""
        # Process the text
        processed = self.preprocess_text(text)
        
        # Return the tokens (already filtered for stop words)
        return processed['tokens']
    
    def check_rule_based(self, user_input):
        """Check if the input matches any intent patterns from database"""
        try:
            user_input = user_input.lower().strip()
            
            # Search for matching intents using text search
            matching_intents = self.intents_collection.find(
                {"$text": {"$search": user_input}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})])
            
            for intent in matching_intents:
                patterns = intent.get('patterns', [])
                
                # Use exact matches for short commands
                if any(pattern == user_input for pattern in patterns):
                    if intent.get('intent') == 'list_all':
                        response = intent.get('responses', ["Here are all schemes:"])[0] + "\n\n"
                        schemes = self.schemes_collection.find({}, {"name": 1})
                        for i, scheme in enumerate(schemes, 1):
                            response += f"{i}. {scheme.get('name', 'Unnamed Scheme')}\n"
                        return response
                    else:
                        return random.choice(intent.get('responses', []))
                
                # Use partial matching for longer queries
                elif any(pattern in user_input for pattern in patterns):
                    return random.choice(intent.get('responses', []))
            
            return None
            
        except Exception as e:
            print(f"Error in rule-based checking: {e}")
            return None
    
    def search_schemes_db(self, query):
        """Search schemes using MongoDB full-text search"""
        try:
            # Try an exact phrase match first
            results = list(self.schemes_collection.find(
                {"$text": {"$search": f"\"{query}\""}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(3))
            
            # If no exact phrase matches, try a general text search
            if not results:
                results = list(self.schemes_collection.find(
                    {"$text": {"$search": query}},
                    {"score": {"$meta": "textScore"}}
                ).sort([("score", {"$meta": "textScore"})]).limit(3))
            
            return results
        except OperationFailure as e:
            print(f"Search failed: {e}")
            # Fallback to keyword-based search if text search fails
            return self.keyword_based_search(self.extract_keywords(query))
    
    def keyword_based_search(self, keywords):
        """Search schemes based on extracted keywords"""
        if not keywords:
            return []
            
        # Search for schemes that have these keywords
        pipeline = [
            {"$match": {"keywords": {"$in": keywords}}},
            {"$addFields": {
                "matchCount": {"$size": {"$setIntersection": ["$keywords", keywords]}}
            }},
            {"$sort": {"matchCount": -1}},
            {"$limit": 3}
        ]
        
        results = list(self.schemes_collection.aggregate(pipeline))
        return results
    
    def format_scheme_details(self, scheme):
        """Format a scheme's details for display to the user"""
        details = [
            f"Name: {scheme['name']}",
            f"Description: {scheme['description']}",
            f"Eligibility: {scheme['eligibility']}",
            f"Benefits: {scheme['benefits']}",
            f"Documents Required: {', '.join(scheme['documents_required'])}",
            f"Application Process: {scheme['application_process']}"
        ]
        return "\n".join(details)
    
    def format_search_results(self, results):
        """Format the search results for display"""
        if not results:
            return None
            
        # If only one result with good confidence, return detailed info
        if len(results) == 1:
            return f"I found a scheme that might interest you:\n\n{self.format_scheme_details(results[0])}"
        
        # Multiple results, list them
        response = f"I found {len(results)} schemes that match your query:\n\n"
        for i, scheme in enumerate(results, 1):
            response += f"{i}. {scheme['name']}\n"
        response += "\nFor more details, please ask about a specific scheme."
        
        return response
    
    def log_user_query(self, query, processed_text, response):
        """Log user query for future analysis and improvement"""
        log_entry = {
            "query": query,
            "processed_tokens": processed_text['tokens'],
            "response": response
        }
        self.user_queries_collection.insert_one(log_entry)
    
    def get_response(self, user_input):
        """Main method to get a response based on user input"""
        if not user_input.strip():
            return "Please ask me about Tamil Nadu government schemes."
        
        # Track the source of the response for logging
        response_source = "default"
        
        # Step 1: Check if input matches rule-based patterns
        rule_response = self.check_rule_based(user_input)
        if rule_response:
            response_source = "rule_based"
            self.log_user_query(user_input, self.preprocess_text(user_input), rule_response)
            return rule_response
        
        # Step 2: Preprocess the input text
        processed_text = self.preprocess_text(user_input)
        
        # Step 3: Perform MongoDB full-text search
        search_results = self.search_schemes_db(user_input)
        if search_results:
            response = self.format_search_results(search_results)
            response_source = "full_text_search"
            self.log_user_query(user_input, processed_text, response)
            return response
        
        # Step 4: Extract keywords using NLTK and try keyword-based search
        keywords = self.extract_keywords(user_input)
        keyword_results = self.keyword_based_search(keywords)
        
        if keyword_results:
            response = self.format_search_results(keyword_results)
            response_source = "keyword_search"
            self.log_user_query(user_input, processed_text, response)
            return response
        
        # Step 5: Fallback response if no matches were found
        fallback_response = (
            "I couldn't find any schemes matching your query. "
            "You can try asking about specific categories like education, "
            "health, agriculture, women, etc., or ask to 'list all schemes'."
        )
        self.log_user_query(user_input, processed_text, fallback_response)
        return fallback_response

    def close(self):
        """Close the MongoDB connection"""
        self.client.close() 