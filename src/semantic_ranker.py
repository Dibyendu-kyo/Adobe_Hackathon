from sentence_transformers import SentenceTransformer, CrossEncoder, util
import torch

class SemanticRanker:
    def __init__(self):
        # Load embedding model for retrieval (optimized for speed)
        self.embedding_model = SentenceTransformer('./models/all-MiniLM-L6-v2')
        
        # Load cross-encoder for re-ranking (highest accuracy)
        self.reranker = CrossEncoder('./models/cross-encoder-ms-marco-MiniLM-L6-v2')
        
        # Enable GPU if available for maximum speed
        if torch.cuda.is_available():
            self.embedding_model = self.embedding_model.cuda()
            self.reranker.model = self.reranker.model.cuda()

    def rank_chunks(self, chunks, persona, job_to_be_done):
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
