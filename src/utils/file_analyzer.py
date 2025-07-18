from typing import List, Dict, Any
from collections import Counter


class FileAnalyzer:
    """Utility class for analyzing file structures and languages"""
    
    @staticmethod
    def analyze_folder_structure(files: List[str]) -> Dict[str, Any]:
        """Analyze folder structure from file paths"""
        folders = set()
        file_types = Counter()
        
        for file_path in files:
            # Extract folders (limit to 4 depth levels)
            parts = file_path.split('/')
            for i in range(min(len(parts) - 1, 4)):
                folder = '/'.join(parts[:i+1])
                folders.add(folder)
            
            # Extract file extensions
            if '.' in parts[-1]:
                ext = parts[-1].split('.')[-1].lower()
                file_types[ext] += 1
        
        # Identify project type based on files
        project_type = FileAnalyzer._identify_project_type(file_types)
        
        return {
            'folders': sorted(list(folders))[:20],  # Limit to 20 folders
            'file_types': dict(file_types.most_common(10)),
            'project_type': project_type,
            'total_files': len(files)
        }
    
    @staticmethod
    def _identify_project_type(file_types: Counter) -> str:
        """Identify project type based on file extensions"""
        project_indicators = {
            'web': ['html', 'css', 'js', 'jsx', 'ts', 'tsx', 'vue', 'angular'],
            'mobile': ['swift', 'kt', 'java', 'dart', 'xaml'],
            'backend': ['py', 'java', 'cs', 'go', 'rb', 'php', 'rs'],
            'data': ['ipynb', 'r', 'sql', 'parquet', 'csv'],
            'devops': ['yml', 'yaml', 'tf', 'dockerfile', 'sh']
        }
        
        project_type = 'general'
        max_score = 0
        
        for ptype, extensions in project_indicators.items():
            score = sum(file_types.get(ext, 0) for ext in extensions)
            if score > max_score:
                max_score = score
                project_type = ptype
        
        return project_type
    
    @staticmethod
    def detect_languages_from_files(files: List[str]) -> Dict[str, int]:
        """Detect programming languages from file extensions"""
        extension_map = {
            'py': 'Python', 'js': 'JavaScript', 'ts': 'TypeScript', 'java': 'Java',
            'cpp': 'C++', 'c': 'C', 'cs': 'C#', 'php': 'PHP', 'rb': 'Ruby',
            'go': 'Go', 'rs': 'Rust', 'swift': 'Swift', 'kt': 'Kotlin',
            'html': 'HTML', 'css': 'CSS', 'scss': 'SCSS', 'sass': 'Sass',
            'vue': 'Vue', 'jsx': 'React', 'tsx': 'React TypeScript',
            'sql': 'SQL', 'r': 'R', 'matlab': 'MATLAB', 'sh': 'Shell',
            'yml': 'YAML', 'yaml': 'YAML', 'json': 'JSON', 'xml': 'XML'
        }
        
        languages = Counter()
        for file_path in files:
            if '.' in file_path:
                ext = file_path.split('.')[-1].lower()
                if ext in extension_map:
                    languages[extension_map[ext]] += 1
        
        return dict(languages)
    
    @staticmethod
    def estimate_lines_of_code(projects: List[Dict[str, Any]]) -> Dict[str, int]:
        """Estimate lines of code based on file extensions and project structure"""
        # Average lines per file by extension (rough estimates)
        lines_per_file = {
            'py': 150, 'js': 120, 'ts': 120, 'java': 200, 'cpp': 180, 'c': 160,
            'cs': 180, 'php': 140, 'rb': 120, 'go': 140, 'rs': 160, 'swift': 140,
            'kt': 160, 'html': 80, 'css': 60, 'scss': 70, 'sass': 70, 'vue': 100,
            'jsx': 120, 'tsx': 120, 'sql': 30, 'r': 100, 'matlab': 120, 'sh': 40,
            'yml': 20, 'yaml': 20, 'json': 15, 'xml': 25, 'md': 50, 'txt': 25
        }
        
        total_lines = 0
        language_lines = {}
        
        for project in projects:
            if 'languages' in project:
                for lang, byte_count in project['languages'].items():
                    # Rough conversion: bytes to lines (assuming avg 60 chars per line)
                    estimated_lines = max(1, byte_count // 60)
                    language_lines[lang] = language_lines.get(lang, 0) + estimated_lines
                    total_lines += estimated_lines
            elif 'folder_structure' in project and 'file_types' in project['folder_structure']:
                # Fallback: estimate from file types
                file_types = project['folder_structure']['file_types']
                for ext, count in file_types.items():
                    if ext in lines_per_file:
                        estimated_lines = count * lines_per_file[ext]
                        # Map extension to language
                        lang_mapping = {
                            'py': 'Python', 'js': 'JavaScript', 'ts': 'TypeScript',
                            'java': 'Java', 'cpp': 'C++', 'c': 'C', 'cs': 'C#',
                            'php': 'PHP', 'rb': 'Ruby', 'go': 'Go', 'rs': 'Rust',
                            'swift': 'Swift', 'kt': 'Kotlin', 'html': 'HTML',
                            'css': 'CSS', 'scss': 'SCSS', 'sass': 'Sass',
                            'vue': 'Vue', 'jsx': 'React', 'tsx': 'React TypeScript'
                        }
                        lang = lang_mapping.get(ext, ext.upper())
                        language_lines[lang] = language_lines.get(lang, 0) + estimated_lines
                        total_lines += estimated_lines
        
        return {
            'total_lines': total_lines,
            'by_language': language_lines
        }