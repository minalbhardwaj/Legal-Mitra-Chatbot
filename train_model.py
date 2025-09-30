import os
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
from data_processing import DataProcessor
from config import Config
import numpy as np
from tqdm import tqdm

class LawRetrievalTrainer:
    def __init__(self):
        self.config = Config()
        self.data_processor = DataProcessor()
        os.makedirs(self.config.MODEL_SAVE_PATH, exist_ok=True)

    def prepare_training_data(self):
        """Prepare training examples from the corpus"""
        dataset = self.data_processor.load_and_combine_datasets()
        corpus = self.data_processor.preprocess_data(dataset)
        self.data_processor.save_corpus(corpus)
        
        # Create training examples (question, positive_answer pairs)
        train_examples = []
        for item in tqdm(corpus, desc="Creating training examples"):
            # Ensure we have both question and answer
            if item['question'] and item['answer']:
                train_examples.append(InputExample(
                    texts=[item['question'], item['answer']]
                ))
        
        if not train_examples:
            raise ValueError("No valid training examples found. Check your dataset structure.")
        
        return train_examples, corpus

    def train(self):
        """Train the retrieval model"""
        try:
            # Prepare data
            train_examples, corpus = self.prepare_training_data()
            print(f"Found {len(train_examples)} valid training examples")
            
            train_dataloader = DataLoader(
                train_examples, 
                shuffle=True, 
                batch_size=self.config.BATCH_SIZE
            )
            
            # Initialize model
            model = SentenceTransformer(self.config.MODEL_NAME)
            
            # Define loss
            train_loss = losses.MultipleNegativesRankingLoss(model)
            
            # Train the model
            print("Starting training...")
            model.fit(
                train_objectives=[(train_dataloader, train_loss)],
                epochs=self.config.EPOCHS,
                warmup_steps=self.config.WARMUP_STEPS,
                show_progress_bar=True,
                output_path=self.config.MODEL_SAVE_PATH
            )
            
            print(f"Model saved to {self.config.MODEL_SAVE_PATH}")
            
            # Generate and save embeddings for the entire corpus
            print("Generating corpus embeddings...")
            answers = [item['answer'] for item in corpus if item['answer']]
            corpus_embeddings = model.encode(answers, show_progress_bar=True)
            self.data_processor.save_embeddings(corpus_embeddings)
            
            return model

        except Exception as e:
            print(f"Error during training: {str(e)}")
            raise

if __name__ == "__main__":
    trainer = LawRetrievalTrainer()
    trainer.train()