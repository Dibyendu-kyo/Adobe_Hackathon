"""
Semantic Ranking Module for Round 1B
Uses sentence transformers and cross-encoders to rank document chunks by relevance.
"""

from sentence_transformers import SentenceTransformer, CrossEncoder, util
import torch
import os


class SemanticRanker:
    """
    Semantic ranker that uses embedding models for retrieval and cross-encoders for re-ranking.
    """
    
    def __init__(self, model_dir="/app/models"):
        """
        Initialize the semantic ranker with pre-downloaded models.
        
        Args:
            model_dir (str): Directory containing the pre-downloaded models
        """
        # Load embedding model for retrieval (optimized for speed)
        embedding_model_path = os.path.join(model_dir, 'all-MiniLM-L6-v2')
        self.embedding_model = SentenceTransformer(embedding_model_path)
        
        # Load cross-encoder for re-ranking (highest accuracy)
        reranker_model_path = os.path.join(model_dir, 'cross-encoder-ms-marco-MiniLM-L6-v2')
        self.reranker = CrossEncoder(reranker_model_path)
        
        # Enable GPU if available for maximum speed
        if torch.cuda.is_available():
            self.embedding_model = self.embedding_model.cuda()
            self.reranker.model = self.reranker.model.cuda()

    def rank_chunks(self, chunks, persona, job_to_be_done):
        """
        Rank document chunks based on relevance to persona and job-to-be-done.
        
        Args:
            chunks (list): List of document chunks to rank
            persona (str): Description of the user's role and expertise
            job_to_be_done (str): Specific task the user needs to accomplish
            
        Returns:
            list: Ranked list of chunks with relevance scores
        """
        if not chunks:
            return []
        
        # Step 1: Build rich query string
        query = f"{persona}. Task: {job_to_be_done}"

        # Step 2: Fast retrieval with embedding similarity
        query_embedding = self.embedding_model.encode(query, convert_to_tensor=True)
        chunk_texts = [chunk['content'] for chunk in chunks]
        
        # Batch encode for speed
        chunk_embeddings = self.embedding_model.encode(
            chunk_texts, 
            convert_to_tensor=True,
            batch_size=32,  # Optimized batch size
            show_progress_bar=False
        )

        # Compute cosine similarities
        cosine_scores = util.cos_sim(query_embedding, chunk_embeddings)[0]

        # Get top 50 candidates for re-ranking (balance speed vs accuracy)
        top_k = min(50, len(chunks))
        top_results = cosine_scores.topk(top_k)
        
        top_indices = top_results.indices.cpu().tolist()
        top_scores = top_results.values.cpu().tolist()

        # Step 3: Precision re-ranking with cross-encoder
        pairs = [[query, chunk_texts[idx]] for idx in top_indices]
        
        # Batch predict for maximum speed
        rerank_scores = self.reranker.predict(
            pairs, 
            batch_size=16,  # Optimized for cross-encoder
            show_progress_bar=False
        )

        # Step 4: Build final ranked list
        ranked_chunks = []
        for idx, score in zip(top_indices, rerank_scores):
            chunk = chunks[idx].copy()
            chunk['score'] = float(score)
            ranked_chunks.append(chunk)

        # Sort by re-ranker score descending
        ranked_chunks.sort(key=lambda x: -x['score'])

        return ranked_chunks