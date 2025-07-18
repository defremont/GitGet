from typing import List, Dict, Any, Optional
import json
import glob
import os
from datetime import datetime


class DataProcessor:
    """Utility class for processing and cleaning portfolio data"""
    
    def __init__(self, max_commits_per_project: Optional[int] = None):
        self.max_commits_per_project = max_commits_per_project
    
    def clean_project_data(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Clean project data by removing unwanted attributes and simplifying user_commits"""
        cleaned_project = project.copy()
        
        # Remove unwanted attributes and large data structures
        attrs_to_remove = [
            'files',  # Remove file lists (can be very large)
            'meets_commit_threshold',
            'topics',
            'is_fork',
            'is_private',
            'size',
            'recent_commits'
        ]
        
        for attr in attrs_to_remove:
            cleaned_project.pop(attr, None)
        
        # Simplify folder_structure to reduce JSON size
        self._simplify_folder_structure(cleaned_project)
        
        # Clean user_commits with optional size reduction for JSON
        self._clean_user_commits(cleaned_project)
        
        return cleaned_project
    
    def _simplify_folder_structure(self, project: Dict[str, Any]) -> None:
        """Simplify folder structure to reduce JSON size"""
        if 'folder_structure' in project and isinstance(project['folder_structure'], dict):
            folder_structure = project['folder_structure']
            
            # Remove folders list (can be very large)
            folder_structure.pop('folders', None)
            
            # Limit file_types to top 5 most common
            if 'file_types' in folder_structure and isinstance(folder_structure['file_types'], dict):
                file_types = folder_structure['file_types']
                # Keep only top 5 file types
                sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:5]
                folder_structure['file_types'] = dict(sorted_types)
    
    def _clean_user_commits(self, project: Dict[str, Any]) -> None:
        """Clean user commits with optional size reduction"""
        if 'user_commits' in project and isinstance(project['user_commits'], list):
            cleaned_commits = []
            seen_messages = set()  # Track seen messages to filter duplicates
            
            # Sort commits by date (most recent first)
            commits_list = project['user_commits']
            if commits_list:
                try:
                    commits_list = sorted(commits_list, key=lambda x: x.get('date', ''), reverse=True)
                except:
                    pass  # If sorting fails, use original order
                
                # Apply user-specified commit limit if set
                if self.max_commits_per_project is not None:
                    commits_list = commits_list[:self.max_commits_per_project]
                    print(f"    DEBUG: Limited to {self.max_commits_per_project} most recent commits per user request")
            
            for commit in commits_list:
                if isinstance(commit, dict):
                    message = commit.get('message', '').strip()
                    
                    # Only include if message hasn't been seen (duplicate filtering for JSON size)
                    if message not in seen_messages:
                        seen_messages.add(message)
                        cleaned_commit = {
                            'message': message,
                            'date': commit.get('date', '')
                        }
                        cleaned_commits.append(cleaned_commit)
            
            project['user_commits'] = cleaned_commits
            
            # Update counts
            original_count = project.get('user_commits_count', 0)
            deduplicated_count = len(cleaned_commits)
            
            # Add debug info about filtering
            if original_count > deduplicated_count:
                print(f"    DEBUG: Filtered {original_count - deduplicated_count} duplicate commit messages for JSON output")
            
            # Keep original count for threshold logic, but note deduplicated count
            project['user_commits_count'] = original_count
            project['user_commits_deduplicated_count'] = deduplicated_count
    
    def estimate_json_size(self, projects: List[Dict[str, Any]]) -> int:
        """Estimate JSON size in characters (approximates tokens)"""
        try:
            json_str = json.dumps(projects, indent=2)
            return len(json_str)
        except:
            return 0
    
    def reduce_json_size_further(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Further reduce JSON size if it's still too large by simplifying folder structure"""
        print("    WARNING: JSON size is still large. Simplifying folder structure only.")
        print("    Consider using --max-commits option to limit commits per project.")
        
        for project in projects:
            # Only reduce folder structure, respect user preferences for commits/README/languages
            if 'folder_structure' in project:
                # Keep only essential info
                folder_structure = project['folder_structure']
                if isinstance(folder_structure, dict):
                    essential_structure = {
                        'project_type': folder_structure.get('project_type', 'general'),
                        'total_files': folder_structure.get('total_files', 0)
                    }
                    # Keep only top 3 file types
                    if 'file_types' in folder_structure:
                        file_types = folder_structure['file_types']
                        if isinstance(file_types, dict) and file_types:
                            sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:3]
                            essential_structure['file_types'] = dict(sorted_types)
                    project['folder_structure'] = essential_structure
        
        return projects
    
    def load_latest_portfolio_data(self) -> Optional[List[Dict[str, Any]]]:
        """Load the most recent portfolio data file"""
        try:
            # Find the most recent portfolio data file
            data_files = glob.glob('portfolio_data_*.json')
            if not data_files:
                print("No existing portfolio data files found")
                return None
            
            # Sort by modification time, get the most recent
            latest_file = max(data_files, key=os.path.getmtime)
            print(f"Loading existing portfolio data from: {latest_file}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"Loaded {len(data)} projects from existing data")
            return data
            
        except Exception as e:
            print(f"Error loading portfolio data: {e}")
            return None
    
    def save_results(self, projects: List[Dict[str, Any]], summary: str) -> str:
        """Save results to files and return the timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save raw project data
        data_filename = f'portfolio_data_{timestamp}.json'
        with open(data_filename, 'w', encoding='utf-8') as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)
        
        # Save portfolio summary
        summary_filename = f'portfolio_summary_{timestamp}.md'
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Results saved:")
        print(f"- Raw data: {data_filename}")
        print(f"- Portfolio summary: {summary_filename}")
        
        return timestamp