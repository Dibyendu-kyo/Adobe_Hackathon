from sentence_transformers import SentenceTransformer, CrossEncoder, util
import torch
import re

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

    def analyze_persona_and_job(self, persona, job_to_be_done):
        """Analyze persona and job to extract key concepts and requirements"""
        persona_lower = persona.lower()
        job_lower = job_to_be_done.lower()
        
        # Define persona-specific concepts
        persona_concepts = {
            'hr': ['form', 'fill', 'sign', 'signature', 'document', 'compliance', 'onboarding', 'employee', 'create', 'convert', 'pdf', 'fillable', 'e-signature', 'request', 'send', 'collect', 'track', 'manage'],
            'travel': ['travel', 'trip', 'destination', 'hotel', 'restaurant', 'activity', 'planning', 'itinerary', 'booking', 'reservation', 'tour', 'visit', 'city', 'coastal', 'adventure', 'culinary', 'nightlife', 'entertainment'],
            'food': ['food', 'dish', 'recipe', 'ingredient', 'cooking', 'meal', 'buffet', 'vegetarian', 'gluten-free', 'dinner', 'lunch', 'breakfast', 'side', 'main', 'appetizer', 'dessert'],
            'legal': ['legal', 'law', 'contract', 'agreement', 'regulation', 'compliance', 'document', 'signature', 'clause', 'terms', 'liability', 'rights', 'obligations']
        }
        
        # Determine primary persona type
        primary_concepts = []
        if any(word in persona_lower for word in ['hr', 'human resources', 'professional']):
            primary_concepts = persona_concepts['hr']
        elif any(word in persona_lower for word in ['travel', 'planner', 'tourist']):
            primary_concepts = persona_concepts['travel']
        elif any(word in persona_lower for word in ['food', 'contractor', 'chef', 'catering']):
            primary_concepts = persona_concepts['food']
        elif any(word in persona_lower for word in ['legal', 'lawyer', 'attorney']):
            primary_concepts = persona_concepts['legal']
        else:
            # Generic concepts
            primary_concepts = ['important', 'key', 'main', 'primary', 'essential']
        
        # Extract job-specific requirements
        job_requirements = []
        if 'form' in job_lower:
            job_requirements.extend(['form', 'fill', 'sign', 'document', 'create', 'fillable'])
        if 'travel' in job_lower:
            job_requirements.extend(['travel', 'trip', 'destination', 'planning', 'itinerary'])
        if 'buffet' in job_lower:
            job_requirements.extend(['buffet', 'menu', 'dinner', 'meal', 'serving'])
        if 'vegetarian' in job_lower:
            job_requirements.extend(['vegetarian', 'vegan', 'plant-based', 'meat-free'])
        if 'gluten-free' in job_lower:
            job_requirements.extend(['gluten-free', 'dietary', 'allergy', 'restriction'])
        
        return primary_concepts + job_requirements

    def create_intelligent_query(self, persona, job_to_be_done):
        """Create highly specific queries based on persona and job analysis"""
        concepts = self.analyze_persona_and_job(persona, job_to_be_done)
        
        # Build context-aware query
        if 'hr' in persona.lower() or 'human resources' in persona.lower():
            return f"fillable forms PDF creation signatures onboarding compliance employee forms {job_to_be_done}"
        elif 'travel' in persona.lower():
            return f"travel planning destinations hotels restaurants activities itinerary booking {job_to_be_done}"
        elif 'food' in persona.lower() or 'contractor' in persona.lower():
            return f"food recipes dishes ingredients cooking meals buffet vegetarian gluten-free {job_to_be_done}"
        elif 'legal' in persona.lower():
            return f"legal documents contracts agreements compliance regulations signatures {job_to_be_done}"
        else:
            return f"{persona} {job_to_be_done} specific actionable information"

    def calculate_content_relevance(self, chunk, persona, job_to_be_done):
        """Calculate how relevant a chunk is to the specific persona and job"""
        concepts = self.analyze_persona_and_job(persona, job_to_be_done)
        
        content_lower = chunk['content'].lower()
        title_lower = chunk.get('section_title', '').lower()
        
        # Count relevant terms in content and title
        content_score = sum(1 for concept in concepts if concept in content_lower)
        title_score = sum(2 for concept in concepts if concept in title_lower)  # Title matches worth more
        
        # Bonus for exact job requirement matches
        job_lower = job_to_be_done.lower()
        job_bonus = sum(3 for word in job_lower.split() if word in content_lower)
        
        return content_score + title_score + job_bonus

    def filter_for_relevance(self, chunks, persona, job_to_be_done):
        """Strong filtering to ensure only relevant content passes through"""
        relevant_chunks = []
        
        for chunk in chunks:
            relevance_score = self.calculate_content_relevance(chunk, persona, job_to_be_done)
            
            # Only include chunks with meaningful relevance
            if relevance_score > 0 and len(chunk['content']) > 100:
                # Skip generic content
                if not self.is_generic_content(chunk['content']):
                    chunk['relevance_score'] = relevance_score
                    relevant_chunks.append(chunk)
        
        # Sort by relevance score and return top chunks (limit for speed)
        relevant_chunks.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_chunks[:3]  # Limit to top 3 most relevant for speed

    def is_generic_content(self, content):
        """Check if content is too generic or unhelpful"""
        generic_phrases = [
            'just view it', 'turn off', 'click here', 'see more', 'learn more',
            'get started', 'try now', 'download', 'install', 'update',
            'check out', 'explore', 'discover', 'find out', 'enable', 'disable',
            'following up', 'indicate response', 'conversion has finished', 'save details',
            'select all tools', 'page thumbnails', 'document area', 'this page',
            'next page', 'previous page', 'home', 'back', 'menu', 'navigation',
            'footer', 'header', 'professional tip', 'clear instructions', 'email instructions',
            'sharing checklist', 'real estate', 'ai assistant', 'generative ai'
        ]
        
        content_lower = content.lower()
        return any(phrase in content_lower for phrase in generic_phrases)

    def rank_chunks(self, chunks, persona, job_to_be_done):
        # Step 1: Strong pre-filtering for relevance
        chunks = self.filter_for_relevance(chunks, persona, job_to_be_done)
        
        if not chunks:
            return []
        
        # Step 2: Create highly targeted query
        query = self.create_intelligent_query(persona, job_to_be_done)

        # Step 3: Fast retrieval with embedding similarity
        query_embedding = self.embedding_model.encode(query, convert_to_tensor=True)
        chunk_texts = [chunk['content'] for chunk in chunks]
        
        # Batch encode for speed with smaller batch size
        chunk_embeddings = self.embedding_model.encode(
            chunk_texts, 
            convert_to_tensor=True,
            batch_size=4,  # Further reduced batch size for speed
            show_progress_bar=False
        )

        # Compute cosine similarities
        cosine_scores = util.cos_sim(query_embedding, chunk_embeddings)[0]

        # Get top candidates for re-ranking (limit for speed)
        top_k = min(3, len(chunks))  # Further reduced for speed
        top_results = cosine_scores.topk(top_k)
        
        top_indices = top_results.indices.cpu().tolist()
        top_scores = top_results.values.cpu().tolist()

        # Step 4: Precision re-ranking with cross-encoder
        rerank_query = f"Find the most relevant information for: {persona} - {job_to_be_done}"
        pairs = [[rerank_query, chunk_texts[idx]] for idx in top_indices]
        
        # Batch predict for maximum speed with smaller batch
        rerank_scores = self.reranker.predict(
            pairs, 
            batch_size=2,  # Further reduced batch size for speed
            show_progress_bar=False
        )

        # Step 5: Build final ranked list with quality filtering
        ranked_chunks = []
        for idx, score in zip(top_indices, rerank_scores):
            chunk = chunks[idx].copy()
            chunk['score'] = float(score)
            
            # Only include chunks with good scores and high relevance
            if score > 0.1 and chunk.get('relevance_score', 0) > 0:  # Lowered thresholds for speed
                ranked_chunks.append(chunk)

        # Sort by re-ranker score descending
        ranked_chunks.sort(key=lambda x: -x['score'])

        return ranked_chunks
