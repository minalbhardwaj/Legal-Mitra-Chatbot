import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from flask import Flask, request, jsonify, render_template
from config import Config
from data_processing import DataProcessor
import os

app = Flask(__name__)
config = Config()
data_processor = DataProcessor()

class LawChatbot:
    def __init__(self):
        self.model = None
        self.corpus = None
        self.corpus_embeddings = None
        self.load_models()

    def load_models(self):
        """Load the trained model and embeddings"""
        if os.path.exists(config.MODEL_SAVE_PATH):
            self.model = SentenceTransformer(config.MODEL_SAVE_PATH)
        else:
            raise FileNotFoundError(f"Model not found at {config.MODEL_SAVE_PATH}")
        
        if os.path.exists(config.CORPUS_PATH):
            self.corpus = data_processor.load_corpus()
        else:
            raise FileNotFoundError(f"Corpus not found at {config.CORPUS_PATH}")
        
        if os.path.exists(config.EMBEDDINGS_PATH):
            self.corpus_embeddings = data_processor.load_embeddings()
        else:
            raise FileNotFoundError(f"Embeddings not found at {config.EMBEDDINGS_PATH}")


    def get_most_relevant_laws(self, query):
        """Retrieve the single most relevant law for a query"""
        query_embedding = self.model.encode(query)

        # Compute similarities
        similarities = np.dot(query_embedding, self.corpus_embeddings.T)
        most_relevant_index = int(np.argmax(similarities))  # single highest

        if similarities[most_relevant_index] > config.SIMILARITY_THRESHOLD:
            return [{
                'answer': self.corpus[most_relevant_index]['answer'],
                'source': self.corpus[most_relevant_index]['source'],
                'similarity': float(similarities[most_relevant_index]),
                'metadata': self.corpus[most_relevant_index]['metadata']
            }]
        else:
            return [{
                'answer': "I couldn't find a sufficiently relevant legal reference for your query.",
                'source': 'System',
                'similarity': 0.0,
                'metadata': {}
            }]
    # def get_most_relevant_laws(self, query):
    #     """Retrieve most relevant laws for a query"""
    #     query_embedding = self.model.encode(query)
        
    #     # Compute similarities
    #     similarities = np.dot(query_embedding, self.corpus_embeddings.T)
    #     most_relevant_indices = np.argsort(similarities)[-config.TOP_K:][::-1]
        
    #     results = []
    #     for idx in most_relevant_indices:
    #         if similarities[idx] > config.SIMILARITY_THRESHOLD:
    #             results.append({
    #                 'answer': self.corpus[idx]['answer'],
    #                 'source': self.corpus[idx]['source'],
    #                 'similarity': float(similarities[idx]),
    #                 'metadata': self.corpus[idx]['metadata']
    #             })
        
    #     return results if results else [{
    #         'answer': "I couldn't find a sufficiently relevant legal reference for your query.",
    #         'source': 'System',
    #         'similarity': 0.0,
    #         'metadata': {}
    #     }]

# Initialize chatbot
try:
    chatbot = LawChatbot()
except Exception as e:
    print(f"Error initializing chatbot: {e}")
    chatbot = None



#send user query and interact with model
def generate_response(user_query):
    if not chatbot:
        return jsonify({'error': 'Chatbot not initialized'}), 500
    
    # data = request.get_json()
    # user_query = data.get('query', '')
    
    if not user_query:
        return jsonify({'error': 'Empty query'}), 400
    
    results = chatbot.get_most_relevant_laws(user_query)
    formatted_response = []
    for result in results:
        formatted_response.append(
            {
                "Source": result['source'],
                "Confidence": result['similarity'],
                "answer": result['answer'],
            }
            # {"Source: {result['source']}\n"
            # f"Confidence: {result['similarity']*100:.1f}%\n"
            # f"{result['answer']}\n"
            # f"{'-'*50}"
        )
    # response_text = "\n".join(formatted_response)
    # print(response_text)
    return formatted_response
    # return jsonify({'results': results})


# def request(state: State, prompt: str) -> str:
#     """
#     Returns a static response instead of calling GPT API.
#     """
#     response = generate_response(prompt)
#     print(response.get('results'))
#     return "Hi my name is himanshu  "


# @app.route('/')
# def home():
#     return render_template('chat.html')

# @app.route('/api/chat', methods=['POST'])
# def chat():
#     if not chatbot:
#         return jsonify({'error': 'Chatbot not initialized'}), 500
    
#     data = request.get_json()
#     user_query = data.get('query', '')
    
#     if not user_query:
#         return jsonify({'error': 'Empty query'}), 400
    
#     results = chatbot.get_most_relevant_laws(user_query)
#     return jsonify({'results': results})

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=7000, debug=True)