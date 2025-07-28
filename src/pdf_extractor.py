import fitz  # PyMuPDF
import json
import re
import os
from collections import Counter, defaultdict
import numpy as np
from typing import Dict, List, Tuple, Optional

class AdvancedPDFExtractor:
    def __init__(self):
        self.font_analysis_cache = {}
        self.structure_patterns = {
            'heading_patterns': [
                r'^[A-Z][A-Z\s]+$',  # ALL CAPS
                r'^\d+\.\s+[A-Z]',   # Numbered headings
                r'^[IVX]+\.\s+[A-Z]', # Roman numerals
                r'^[A-Z]\.[A-Z\s]+$', # Letter headings
                r'^Chapter\s+\d+',    # Chapter headings
                r'^Section\s+\d+',    # Section headings
            ],
            'content_indicators': [
                'procedure', 'step', 'instruction', 'guide', 'tutorial',
                'example', 'note', 'tip', 'warning', 'important'
            ]
        }

    def extract_document_structure(self, pdf_path: str) -> Tuple[Dict, Optional[fitz.Document]]:
        """
        Advanced document structure extraction using multiple analysis techniques.
        """
        try:
            doc = fitz.open(pdf_path)
            if not doc:
                return {"title": "Document Not Found", "outline": []}, None

            # Multi-stage analysis
            text_blocks = self._extract_text_blocks(doc)
            font_analysis = self._analyze_font_hierarchy(doc)
            layout_analysis = self._analyze_layout_structure(doc)
            semantic_analysis = self._analyze_semantic_structure(text_blocks)
            
            # Combine analyses for robust heading detection
            headings = self._detect_headings_advanced(
                text_blocks, font_analysis, layout_analysis, semantic_analysis
            )
            
            # Extract title using multiple methods
            title = self._extract_title_advanced(doc, headings)
            
            # Build structured outline
            outline = self._build_structured_outline(headings, doc)
            
            result = {
                "title": title,
                "outline": outline,
                "metadata": {
                    "total_pages": len(doc),
                    "detected_headings": len(headings),
                    "font_hierarchy_levels": len(font_analysis.get('hierarchy', [])),
                    "extraction_method": "advanced_multi_analysis"
                }
            }
            
            return result, doc
            
        except Exception as e:
            print(f"Error extracting structure from {pdf_path}: {e}")
            return {"title": "Extraction Error", "outline": []}, None

    def _extract_text_blocks(self, doc: fitz.Document) -> List[Dict]:
        """Extract text blocks with detailed positioning and formatting information."""
        text_blocks = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
            
            for block in text_dict.get("blocks", []):
                if block['type'] == 0:  # text block
                    for line in block.get("lines", []):
                        line_text = "".join(span['text'] for span in line['spans'])
                        if line_text.strip():
                            # Get detailed span information
                            spans_info = []
                            for span in line['spans']:
                                spans_info.append({
                                    'text': span['text'],
                                    'font': span['font'],
                                    'size': span['size'],
                                    'flags': span['flags'],
                                    'bbox': span.get('bbox', [0, 0, 0, 0])
                                })
                            
                            text_blocks.append({
                                'text': line_text.strip(),
                                'page': page_num + 1,
                                'bbox': line.get('bbox', [0, 0, 0, 0]),
                                'spans': spans_info,
                                'font_info': self._extract_font_info(spans_info)
                            })
        
        return text_blocks

    def _extract_font_info(self, spans: List[Dict]) -> Dict:
        """Extract comprehensive font information from spans."""
        if not spans:
            return {}
        
        # Aggregate font information
        fonts = [span['font'] for span in spans]
        sizes = [span['size'] for span in spans]
        flags = [span['flags'] for span in spans]
        
        return {
            'primary_font': max(set(fonts), key=fonts.count) if fonts else '',
            'font_size': np.mean(sizes) if sizes else 0,
            'max_size': max(sizes) if sizes else 0,
            'min_size': min(sizes) if sizes else 0,
            'is_bold': any(flag & 16 for flag in flags),
            'is_italic': any(flag & 2 for flag in flags),
            'font_variety': len(set(fonts)),
            'size_variety': len(set(sizes))
        }

    def _analyze_font_hierarchy(self, doc: fitz.Document) -> Dict:
        """Analyze font hierarchy to identify heading levels."""
        all_fonts = []
        font_sizes = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
            
            for block in text_dict.get("blocks", []):
                if block['type'] == 0:
                    for line in block.get("lines", []):
                        for span in line['spans']:
                            all_fonts.append(span['font'])
                            font_sizes.append(span['size'])
        
        # Analyze font distribution
        font_counter = Counter(all_fonts)
        size_counter = Counter(font_sizes)
        
        # Determine hierarchy levels
        sorted_sizes = sorted(size_counter.keys(), reverse=True)
        hierarchy = []
        
        for i, size in enumerate(sorted_sizes[:5]):  # Top 5 sizes
            level = f"H{i+1}" if i < 3 else "H3"
            hierarchy.append({
                'level': level,
                'size': size,
                'frequency': size_counter[size]
            })
        
        return {
            'hierarchy': hierarchy,
            'most_common_font': font_counter.most_common(1)[0] if font_counter else ('', 0),
            'size_distribution': dict(size_counter),
            'font_distribution': dict(font_counter)
        }

    def _analyze_layout_structure(self, doc: fitz.Document) -> Dict:
        """Analyze document layout to identify structural elements."""
        layout_info = {
            'page_dimensions': [],
            'text_regions': [],
            'margins': [],
            'column_info': []
        }
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            rect = page.rect
            
            layout_info['page_dimensions'].append({
                'page': page_num + 1,
                'width': rect.width,
                'height': rect.height
            })
            
            # Analyze text positioning
            text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
            text_positions = []
            
            for block in text_dict.get("blocks", []):
                if block['type'] == 0:
                    for line in block.get("lines", []):
                        bbox = line.get('bbox', [0, 0, 0, 0])
                        text_positions.append({
                            'x': bbox[0],
                            'y': bbox[1],
                            'width': bbox[2] - bbox[0],
                            'height': bbox[3] - bbox[1]
                        })
            
            if text_positions:
                layout_info['text_regions'].append({
                    'page': page_num + 1,
                    'positions': text_positions
                })
        
        return layout_info

    def _analyze_semantic_structure(self, text_blocks: List[Dict]) -> Dict:
        """Analyze semantic structure of the document."""
        semantic_info = {
            'potential_headings': [],
            'content_sections': [],
            'structural_patterns': []
        }
        
        for block in text_blocks:
            text = block['text']
            font_info = block['font_info']
            
            # Check for heading patterns
            is_heading = self._is_potential_heading(text, font_info)
            
            if is_heading:
                semantic_info['potential_headings'].append({
                    'text': text,
                    'page': block['page'],
                    'font_info': font_info,
                    'confidence': self._calculate_heading_confidence(text, font_info)
                })
            else:
                semantic_info['content_sections'].append({
                    'text': text[:200],  # Truncate for analysis
                    'page': block['page'],
                    'font_info': font_info
                })
        
        return semantic_info

    def _is_potential_heading(self, text: str, font_info: Dict) -> bool:
        """Advanced heading detection using multiple criteria."""
        if not text or len(text.strip()) < 2:
            return False
        
        text_clean = text.strip()
        
        # Multiple heading indicators
        indicators = 0
        
        # 1. Font size indicator
        if font_info.get('font_size', 0) > 12:  # Larger than body text
            indicators += 1
        
        # 2. Bold text indicator
        if font_info.get('is_bold', False):
            indicators += 2
        
        # 3. Pattern matching
        for pattern in self.structure_patterns['heading_patterns']:
            if re.match(pattern, text_clean):
                indicators += 2
                break
        
        # 4. Length indicator (headings are typically short)
        if 3 <= len(text_clean.split()) <= 15:
            indicators += 1
        
        # 5. Case indicator
        if text_clean.isupper() and len(text_clean) > 3:
            indicators += 1
        
        # 6. Content indicator
        for indicator in self.structure_patterns['content_indicators']:
            if indicator.lower() in text_clean.lower():
                indicators -= 1  # Content words reduce heading likelihood
                break
        
        return indicators >= 2

    def _calculate_heading_confidence(self, text: str, font_info: Dict) -> float:
        """Calculate confidence score for heading detection."""
        confidence = 0.0
        
        # Font size confidence
        size = font_info.get('font_size', 0)
        if size > 16:
            confidence += 0.3
        elif size > 12:
            confidence += 0.2
        
        # Bold text confidence
        if font_info.get('is_bold', False):
            confidence += 0.3
        
        # Pattern confidence
        for pattern in self.structure_patterns['heading_patterns']:
            if re.match(pattern, text.strip()):
                confidence += 0.2
                break
        
        # Length confidence
        word_count = len(text.split())
        if 2 <= word_count <= 8:
            confidence += 0.1
        
        return min(confidence, 1.0)

    def _detect_headings_advanced(self, text_blocks: List[Dict], 
                                 font_analysis: Dict, 
                                 layout_analysis: Dict, 
                                 semantic_analysis: Dict) -> List[Dict]:
        """Advanced heading detection combining multiple analyses."""
        headings = []
        
        # Get font hierarchy for level assignment
        font_hierarchy = font_analysis.get('hierarchy', [])
        size_to_level = {item['size']: item['level'] for item in font_hierarchy}
        
        for block in text_blocks:
            text = block['text']
            font_info = block['font_info']
            
            if self._is_potential_heading(text, font_info):
                # Determine heading level
                size = font_info.get('font_size', 0)
                level = size_to_level.get(size, "H3")
                
                # Calculate comprehensive confidence
                confidence = self._calculate_heading_confidence(text, font_info)
                
                if confidence > 0.3:  # Only include confident headings
                    headings.append({
                        'text': text,
                        'level': level,
                        'page': block['page'],
                        'confidence': confidence,
                        'font_info': font_info
                    })
        
        # Sort by page and confidence
        headings.sort(key=lambda x: (x['page'], -x['confidence']))
        
        return headings

    def _extract_title_advanced(self, doc: fitz.Document, headings: List[Dict]) -> str:
        """Extract document title using multiple methods."""
        title_candidates = []
        
        # Method 1: PDF metadata
        try:
            metadata = doc.metadata
            if metadata and metadata.get('title') and metadata['title'].strip():
                title_candidates.append(('metadata', metadata['title'].strip(), 1.0))
        except:
            pass
        
        # Method 2: First page headings
        first_page_headings = [h for h in headings if h['page'] == 1]
        if first_page_headings:
            best_heading = max(first_page_headings, key=lambda x: x['confidence'])
            title_candidates.append(('first_heading', best_heading['text'], best_heading['confidence']))
        
        # Method 3: Largest font on first page
        try:
            page = doc.load_page(0)
            text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
            
            largest_text = ""
            largest_size = 0
            
            for block in text_dict.get("blocks", []):
                if block['type'] == 0:
                    for line in block.get("lines", []):
                        for span in line['spans']:
                            if span['size'] > largest_size and len(span['text'].strip()) > 3:
                                largest_size = span['size']
                                largest_text = span['text'].strip()
            
            if largest_text:
                title_candidates.append(('largest_font', largest_text, 0.8))
        except:
            pass
        
        # Select best title
        if title_candidates:
            best_candidate = max(title_candidates, key=lambda x: x[2])
            return best_candidate[1]
        
        return "Untitled Document"

    def _build_structured_outline(self, headings: List[Dict], doc: fitz.Document) -> List[Dict]:
        """Build structured outline from detected headings."""
        outline = []
        
        for heading in headings:
            outline.append({
                "level": heading['level'],
                "text": heading['text'],
                "page": heading['page'],
                "confidence": heading['confidence']
            })
        
        return outline

# Main execution function
if __name__ == "__main__":
    extractor = AdvancedPDFExtractor()
    
    # Example usage
    pdf_path = "sample.pdf"
    if os.path.exists(pdf_path):
        structure, doc = extractor.extract_document_structure(pdf_path)
        print(json.dumps(structure, indent=2))
        if doc:
            doc.close()
    else:
        print(f"PDF file not found: {pdf_path}")