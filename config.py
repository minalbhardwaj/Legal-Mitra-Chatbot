import os

class Config:
    # Model configuration
    MODEL_NAME = "paraphrase-MiniLM-L6-v2"
    BATCH_SIZE = 16
    EPOCHS = 3
    WARMUP_STEPS = 100
    
    # Data configuration
    DATASETS = [  
        "kshitij230/Indian-Law",
        # Add your other dataset names here
    ]
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_SAVE_PATH = os.path.join(BASE_DIR, "models", "law_retrieval_model")
    DATA_DIR = os.path.join(BASE_DIR, "data")
    EMBEDDINGS_PATH = os.path.join(DATA_DIR, "embeddings", "corpus_embeddings.npy")
    CORPUS_PATH = os.path.join(DATA_DIR, "processed", "legal_corpus.pkl")
    
    # Chatbot settings
    SIMILARITY_THRESHOLD = 0.6  # Minimum similarity score to return a result
    TOP_K = 3                   # Number of results to return

