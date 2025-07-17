import sys
import json
import argparse
import os
from pathlib import Path

sys.path.append('src')
from pdf_extractor import extract_pdf_outline
from chunking import create_semantic_chunks
from semantic_ranker import SemanticRanker

class PersonaTester:
    def __init__(self, config_path="personas_config.json"):
        """Initialize with configuration file"""
        self.config = self.load_config(config_path)
        self.ranker = None
    
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {config_path} not found. Using default settings.")
            return self.get_default_config()
    
    def get_default_config(self):
        """Fallback default configuration"""
        return {
            "test_scenarios": [],
            "output_settings": {
                "top_results": 3,
                "show_scores": True,
                "preview_length": 150,
                "score_threshold": -10.0
            }
        }
    
    def test_persona_ranking(self, pdf_path, persona, job_to_be_done, scenario_name="Custom"):
        """Test semantic ranking with a specific persona"""
        settings = self.config["output_settings"]
        
        print(f"\n{'='*70}")
        print(f"SCENARIO: {scenario_name}")
        print(f"PERSONA: {persona}")
        print(f"JOB: {job_to_be_done}")
        print(f"{'='*70}")
        
        # Initialize ranker if not already done
        if self.ranker is None:
            print("Loading semantic models...")
            self.ranker = SemanticRanker()
        
        # Extract and process
        outline_json = extract_pdf_outline(pdf_path)
        chunks = create_semantic_chunks(pdf_path, outline_json)
        
        # Rank with persona
        ranked = self.ranker.rank_chunks(chunks, persona, job_to_be_done)
        
        # Filter by score threshold if specified
        if settings.get("score_threshold"):
            ranked = [chunk for chunk in ranked if chunk['score'] >= settings["score_threshold"]]
        
        # Show top results
        top_n = settings.get("top_results", 3)
        print(f"\nTop {top_n} most relevant sections:")
        
        for i, chunk in enumerate(ranked[:top_n], 1):
            print(f"\n#{i}", end="")
            if settings.get("show_scores", True):
                print(f" (Score: {chunk['score']:.4f})", end="")
            print()
            print(f"Section: {chunk['section_title']}")
            print(f"Page: {chunk['page_num']}")
            
            preview_len = settings.get("preview_length", 150)
            content_preview = chunk['content'][:preview_len]
            if len(chunk['content']) > preview_len:
                content_preview += "..."
            print(f"Preview: {content_preview}")
        
        return ranked
    
    def run_all_scenarios(self, pdf_path):
        """Run all configured test scenarios"""
        scenarios = self.config.get("test_scenarios", [])
        
        if not scenarios:
            print("No test scenarios found in configuration.")
            return
        
        results = {}
        for scenario in scenarios:
            try:
                ranked = self.test_persona_ranking(
                    pdf_path,
                    scenario["persona"],
                    scenario["job_to_be_done"],
                    scenario["name"]
                )
                results[scenario["name"]] = ranked
            except Exception as e:
                print(f"Error in scenario '{scenario['name']}': {e}")
        
        return results
    
    def run_custom_scenario(self, pdf_path, persona, job_to_be_done):
        """Run a single custom scenario"""
        return self.test_persona_ranking(pdf_path, persona, job_to_be_done, "Custom")
    
    def add_scenario(self, name, persona, job_to_be_done, expected_keywords=None):
        """Add a new scenario to the configuration"""
        new_scenario = {
            "name": name,
            "persona": persona,
            "job_to_be_done": job_to_be_done
        }
        if expected_keywords:
            new_scenario["expected_keywords"] = expected_keywords
        
        self.config["test_scenarios"].append(new_scenario)
    
    def save_config(self, config_path="personas_config.json"):
        """Save current configuration to file"""
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Test PDF semantic ranking with different personas")
    parser.add_argument("pdf_path", nargs='?', default="sample.pdf", help="Path to PDF file to analyze")
    parser.add_argument("--config", default="personas_config.json", help="Configuration file path")
    parser.add_argument("--persona", help="Custom persona description")
    parser.add_argument("--job", help="Custom job-to-be-done description")
    parser.add_argument("--scenario", help="Run specific scenario by name")
    
    args = parser.parse_args()
    
    # Check if PDF exists
    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file '{args.pdf_path}' not found.")
        return
    
    # Initialize tester
    tester = PersonaTester(args.config)
    
    # Run based on arguments
    if args.persona and args.job:
        # Custom scenario
        tester.run_custom_scenario(args.pdf_path, args.persona, args.job)
    elif args.scenario:
        # Specific scenario
        scenarios = {s["name"]: s for s in tester.config.get("test_scenarios", [])}
        if args.scenario in scenarios:
            scenario = scenarios[args.scenario]
            tester.test_persona_ranking(
                args.pdf_path,
                scenario["persona"],
                scenario["job_to_be_done"],
                scenario["name"]
            )
        else:
            print(f"Scenario '{args.scenario}' not found.")
            print("Available scenarios:", list(scenarios.keys()))
    else:
        # Run all scenarios
        tester.run_all_scenarios(args.pdf_path)

if __name__ == "__main__":
    main()