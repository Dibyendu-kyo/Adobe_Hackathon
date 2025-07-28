import os
import json
import fitz  # PyMuPDF
import re
from typing import List, Dict, Optional
from collections import defaultdict

class AdvancedChunkingEngine:
    def __init__(self):
        self.content_patterns = {
            'section_boundaries': [
                r'^\d+\.\s+[A-Z]',  # Numbered sections
                r'^[A-Z]\.[A-Z\s]+$',  # Letter sections
                r'^Chapter\s+\d+',  # Chapter headings
                r'^Section\s+\d+',  # Section headings
                r'^[IVX]+\.\s+[A-Z]',  # Roman numerals
            ],
            'content_indicators': [
                'procedure', 'step', 'instruction', 'guide', 'tutorial',
                'example', 'note', 'tip', 'warning', 'important',
                'method', 'process', 'technique', 'approach'
            ],
            'quality_indicators': [
                'detailed', 'comprehensive', 'complete', 'thorough',
                'specific', 'concrete', 'practical', 'actionable'
            ]
        }
        
        # Ultra-aggressive limits for speed
        self.min_chunk_length = 80  # Further reduced
        self.max_chunk_length = 800  # Further reduced
        self.quality_threshold = 0.3  # Further reduced

    def create_semantic_chunks(self, pdf_path: str, outline_json: str) -> List[Dict]:
        """
        Advanced semantic chunking with intelligent content extraction.
        """
        try:
            # Load outline from JSON string
            outline_data = json.loads(outline_json)
            outline = outline_data.get('outline', [])

            # Extract document name
            doc_name = os.path.basename(pdf_path)

            # Get comprehensive text extraction
            document = fitz.open(pdf_path)
            full_text_by_page = self._extract_full_text_by_page(document)
            document.close()

            # Create intelligent chunks
            chunks = self._create_intelligent_chunks(outline, full_text_by_page, doc_name)
            
            # Quality filtering
            chunks = self._filter_chunks_by_quality(chunks)
            
            return chunks
            
        except Exception as e:
            print(f"Error in chunking for {pdf_path}: {e}")
            return []

    def _extract_full_text_by_page(self, document: fitz.Document) -> Dict[int, str]:
        """Extract full text with detailed positioning information."""
        full_text_by_page = {}
        
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            
            # Get detailed text extraction
            text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
            page_text = ""
            
            # Extract text with positioning
            for block in text_dict.get("blocks", []):
                if block['type'] == 0:  # text block
                    for line in block.get("lines", []):
                        line_text = "".join(span['text'] for span in line['spans'])
                        if line_text.strip():
                            page_text += line_text + "\n"
            
            full_text_by_page[page_num + 1] = page_text.strip()
        
        return full_text_by_page

    def _create_intelligent_chunks(self, outline: List[Dict], 
                                 full_text_by_page: Dict[int, str], 
                                 doc_name: str) -> List[Dict]:
        """Create intelligent chunks based on outline structure."""
        chunks = []
        
        for i, heading in enumerate(outline):
            section_title = heading['text']
            page_num = heading['page']
            
            # Get comprehensive content for this section
            content = self._extract_section_content(
                section_title, page_num, full_text_by_page, outline, i
            )
            
            if content and len(content.strip()) >= self.min_chunk_length:
                chunk = {
                    'doc_name': doc_name,
                    'section_title': section_title,
                    'page_number': page_num,
                    'content': content,
                    'quality_score': self._calculate_content_quality(content, section_title)
                }
                chunks.append(chunk)
        
        return chunks

    def _extract_section_content(self, section_title: str, page_num: int,
                                full_text_by_page: Dict[int, str],
                                outline: List[Dict], heading_index: int) -> str:
        """Extract comprehensive content for a section."""
        
        # Get text from current page only for speed
        current_page_text = full_text_by_page.get(page_num, '')
        
        # Find section boundaries
        section_content = self._extract_content_between_headings(
            current_page_text, section_title, outline, heading_index
        )
        
        # If no specific content found, use intelligent extraction
        if not section_content or len(section_content.strip()) < 50:  # Reduced threshold
            section_content = self._extract_intelligent_content(
                current_page_text, section_title, page_num
            )
        
        return section_content

    def _extract_content_between_headings(self, text: str, current_heading: str,
                                        outline: List[Dict], heading_index: int) -> str:
        """Extract content between current heading and next heading."""
        lines = text.split('\n')
        content_lines = []
        found_current_heading = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if we found the current heading
            if current_heading.lower() in line.lower() and not found_current_heading:
                found_current_heading = True
                continue
            
            # If we found the current heading, start collecting content
            if found_current_heading:
                # Check if we've reached the next heading
                if self._is_next_heading(line, outline, heading_index):
                    break
                
                # Check if line looks like a heading
                if self._looks_like_heading(line):
                    break
                
                content_lines.append(line)
                
                # Limit content length for speed
                if len(' '.join(content_lines)) > 300:  # Further reduced limit
                    break
        
        return ' '.join(content_lines).strip()

    def _is_next_heading(self, line: str, outline: List[Dict], current_index: int) -> bool:
        """Check if line is the next heading in the outline."""
        if current_index + 1 >= len(outline):
            return False
        
        next_heading = outline[current_index + 1]['text']
        return next_heading.lower() in line.lower()

    def _looks_like_heading(self, line: str) -> bool:
        """Check if line looks like a heading."""
        # Check for heading patterns
        for pattern in self.content_patterns['section_boundaries']:
            if re.match(pattern, line):
                return True
        
        # Check for all caps (potential heading)
        if line.isupper() and len(line.split()) <= 8:
            return True
        
        # Check for short, bold-looking text
        if len(line.split()) <= 5 and not line.endswith('.'):
            return True
        
        return False

    def _extract_intelligent_content(self, text: str, section_title: str, page_num: int) -> str:
        """Extract intelligent content when specific section boundaries aren't clear."""
        lines = text.split('\n')
        content_lines = []
        found_section = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for section title
            if section_title.lower() in line.lower() and not found_section:
                found_section = True
                continue
            
            # Collect content after finding section
            if found_section:
                # Stop at obvious section boundaries
                if self._looks_like_heading(line):
                    break
                
                # Stop at very short lines that might be navigation
                if len(line) < 10 and not line.endswith('.'):
                    continue
                
                content_lines.append(line)
                
                # Limit content length for speed
                if len(' '.join(content_lines)) > 300:  # Further reduced limit
                    break
        
        # If no specific content found, get meaningful text from the page
        if not content_lines:
            content_lines = self._extract_meaningful_page_content(text, page_num)
        
        return ' '.join(content_lines).strip()

    def _extract_meaningful_page_content(self, text: str, page_num: int) -> List[str]:
        """Extract meaningful content from page text."""
        lines = text.split('\n')
        meaningful_lines = []
        
        for line in lines[:15]:  # Further reduced from 25
            line = line.strip()
            if line and len(line) > 15:  # Further reduced from 20
                # Skip navigation and generic content
                if not self._is_generic_content(line):
                    meaningful_lines.append(line)
                    if len(meaningful_lines) >= 5:  # Further reduced from 10
                        break
        
        return meaningful_lines

    def _is_generic_content(self, text: str) -> bool:
        """Check if text is generic or unhelpful."""
        generic_phrases = [
            'click here', 'see more', 'learn more', 'get started', 'try now',
            'download', 'install', 'update', 'check out', 'explore', 'discover',
            'find out', 'just view it', 'turn off', 'enable', 'disable',
            'this page', 'next page', 'previous page', 'home', 'back',
            'menu', 'navigation', 'footer', 'header', 'following up',
            'indicate response', 'conversion has finished', 'save details',
            'select all tools', 'page thumbnails', 'document area',
            'professional tip', 'clear instructions', 'email instructions',
            'sharing checklist', 'real estate', 'ai assistant', 'generative ai',
            'turn off ai', 'enable ai', 'disable ai', 'ai toggle'
        ]
        
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in generic_phrases)

    def _calculate_content_quality(self, content: str, section_title: str) -> float:
        """Calculate quality score for content."""
        if not content or len(content) < self.min_chunk_length:
            return 0.0
        
        quality_score = 0.0
        
        # Length quality
        if len(content) >= 120:  # Further reduced from 150
            quality_score += 0.2
        elif len(content) >= 80:  # Further reduced from 100
            quality_score += 0.1
        
        # Content relevance
        content_lower = content.lower()
        title_lower = section_title.lower()
        
        # Check for content indicators
        for indicator in self.content_patterns['content_indicators']:
            if indicator in content_lower:
                quality_score += 0.1
        
        # Check for quality indicators
        for indicator in self.content_patterns['quality_indicators']:
            if indicator in content_lower:
                quality_score += 0.1
        
        # Title-content alignment
        title_words = set(title_lower.split())
        content_words = set(content_lower.split())
        if title_words.intersection(content_words):
            quality_score += 0.2
        
        # Avoid generic content penalty
        if self._is_generic_content(content):
            quality_score -= 0.3
        
        return max(0.0, min(1.0, quality_score))

    def _filter_chunks_by_quality(self, chunks: List[Dict]) -> List[Dict]:
        """Filter chunks based on quality score."""
        quality_chunks = []
        
        for chunk in chunks:
            if chunk.get('quality_score', 0) >= self.quality_threshold:
                quality_chunks.append(chunk)
        
        # Sort by quality score
        quality_chunks.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
        
        return quality_chunks

# Legacy function for backward compatibility
def create_semantic_chunks(pdf_path: str, outline_json: str) -> List[Dict]:
    """Legacy function that uses the advanced chunking engine."""
    engine = AdvancedChunkingEngine()
    return engine.create_semantic_chunks(pdf_path, outline_json)
