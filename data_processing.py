import os
import pickle
import numpy as np
from datasets import load_dataset, concatenate_datasets
from config import Config
from tqdm import tqdm

class DataProcessor:
    def __init__(self):
        self.config = Config()
        os.makedirs(os.path.dirname(self.config.CORPUS_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(self.config.EMBEDDINGS_PATH), exist_ok=True)

    def load_and_combine_datasets(self):
        """Load and combine multiple datasets"""
        combined_dataset = None
        
        for dataset_name in self.config.DATASETS:
            try:
                dataset = load_dataset(dataset_name)
                train_data = dataset['train']
                
                if combined_dataset is None:
                    combined_dataset = train_data
                else:
                    combined_dataset = concatenate_datasets([combined_dataset, train_data])
            except Exception as e:
                print(f"Error loading dataset {dataset_name}: {str(e)}")
                continue
        
        if combined_dataset is None:
            raise ValueError("No datasets were successfully loaded.")
        
        return combined_dataset

    def preprocess_data(self, dataset):
        """Process dataset into question-answer pairs"""
        corpus = []
        
        # Handle the specific structure of the Indian-Law dataset
        for example in tqdm(dataset, desc="Processing data"):
            # For Indian-Law dataset, we'll use 'title' as question and 'text' as answer
            if 'title' in example and 'text' in example:
                corpus.append({
                    'question': example['title'],
                    'answer': example['text'],
                    'source': example.get('act', 'Unknown Act'),
                    'metadata': {
                        'section': example.get('section', ''),
                        'url': example.get('url', '')
                    }
                })
            # Add other dataset structures here if needed
            elif 'question' in example and 'answer' in example:
                corpus.append({
                    'question': example['question'],
                    'answer': example['answer'],
                    'source': example.get('source', 'Unknown'),
                    'metadata': example.get('metadata', {})
                })
            elif 'Instruction' in example and 'Response' in example:
                    corpus.append({
                        'question': example['Instruction'],
                        'answer': example['Response'],
                        'source': example.get('source', 'Unknown'),
                        'metadata': example.get('metadata', {})
                    })
            
        if not corpus:
            raise ValueError("No valid question-answer pairs found in the dataset.")
        
        return corpus

    def save_corpus(self, corpus):
        """Save processed corpus to disk"""
        with open(self.config.CORPUS_PATH, 'wb') as f:
            pickle.dump(corpus, f)

    def load_corpus(self):
        """Load processed corpus from disk"""
        with open(self.config.CORPUS_PATH, 'rb') as f:
            return pickle.load(f)

    def save_embeddings(self, embeddings):
        """Save embeddings to disk"""
        np.save(self.config.EMBEDDINGS_PATH, embeddings)

    def load_embeddings(self):
        """Load embeddings from disk"""
        return np.load(self.config.EMBEDDINGS_PATH)