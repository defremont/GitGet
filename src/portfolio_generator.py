from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from .config import PortfolioConfig, ConfigManager
from .ai_providers import AIProviderFactory
from .repository_managers import GitHubManager, GitLabManager
from .utils import FileAnalyzer, DataProcessor


class PortfolioGenerator:
    """Main portfolio generator application"""
    
    def __init__(self, config: PortfolioConfig):
        self.config = config
        self.total_user_commits = 0
        
        # Initialize AI provider
        self.ai_provider = AIProviderFactory.create_provider(
            config.model_provider, 
            config.model_name or ConfigManager.get_default_model_for_provider(config.model_provider)
        )
        
        # Initialize repository managers
        self.github_manager = None
        self.gitlab_manager = None
        
        if not config.platform or config.platform == 'github':
            github_token = ConfigManager.get_github_token()
            if github_token or config.github_username:
                self.github_manager = GitHubManager(
                    github_token, 
                    config.min_commits, 
                    config.max_commits_per_project
                )
        
        if not config.platform or config.platform == 'gitlab':
            gitlab_token = ConfigManager.get_gitlab_token()
            if gitlab_token or config.gitlab_username:
                self.gitlab_manager = GitLabManager(
                    gitlab_token,
                    config.gitlab_url,
                    config.min_commits,
                    config.max_commits_per_project
                )
        
        # Initialize data processor
        self.data_processor = DataProcessor(config.max_commits_per_project)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current AI model"""
        return self.ai_provider.get_model_info()
    
    def run_stage_1(self) -> Optional[List[Dict[str, Any]]]:
        """Stage 1: Get JSON data from repositories"""
        print("Stage 1: Fetching repository data...")
        
        all_projects = []
        
        # Fetch GitHub repositories
        if self.github_manager:
            print("Fetching GitHub repositories...")
            try:
                self.github_manager.get_user_info()
                repos = self.github_manager.fetch_repositories(self.config.github_username)
                print(f"Processing {len(repos)} GitHub repositories with detailed analysis...")
                
                github_projects = []
                for repo in repos:
                    if not repo['fork'] or repo['stargazers_count'] > 0:  # Skip unmodified forks
                        processed_repo = self.github_manager.process_repository(repo)
                        if processed_repo.get('meets_commit_threshold', False):
                            github_projects.append(processed_repo)
                            self.total_user_commits += processed_repo.get('user_commits_count', 0)
                        else:
                            print(f"  Skipping {repo['full_name']} - insufficient user commits ({processed_repo.get('user_commits_count', 0)})")
                
                all_projects.extend(github_projects)
                print(f"Processed {len(github_projects)} GitHub repositories (filtered by commit threshold)")
                
            except Exception as e:
                print(f"Error processing GitHub repositories: {e}")
        
        # Fetch GitLab repositories
        if self.gitlab_manager:
            print("Fetching GitLab repositories...")
            try:
                self.gitlab_manager.get_user_info()
                repos = self.gitlab_manager.fetch_repositories(self.config.gitlab_username)
                print(f"Processing {len(repos)} GitLab repositories with detailed analysis...")
                
                gitlab_projects = []
                for repo in repos:
                    if not repo.get('forked_from_project') or repo.get('star_count', 0) > 0:  # Skip unmodified forks
                        processed_repo = self.gitlab_manager.process_repository(repo)
                        if processed_repo.get('meets_commit_threshold', False):
                            gitlab_projects.append(processed_repo)
                            self.total_user_commits += processed_repo.get('user_commits_count', 0)
                        else:
                            print(f"  Skipping {repo['path_with_namespace']} - insufficient user commits ({processed_repo.get('user_commits_count', 0)})")
                
                all_projects.extend(gitlab_projects)
                print(f"Processed {len(gitlab_projects)} GitLab repositories (filtered by commit threshold)")
                
            except Exception as e:
                print(f"Error processing GitLab repositories: {e}")
        
        if not all_projects:
            print("No projects found. Please check your credentials and usernames.")
            self._print_troubleshooting_tips()
            return None
        
        print(f"\nTotal projects found: {len(all_projects)}")
        print(f"Total user commits across all projects: {self.total_user_commits}")
        
        # Clean and save data
        cleaned_projects = [self.data_processor.clean_project_data(project) for project in all_projects]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'portfolio_data_{timestamp}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(cleaned_projects, f, indent=2, ensure_ascii=False)
        
        print(f"Stage 1 completed! Data saved to: {filename}")
        return all_projects
    
    def run_stage_2(self, projects_data: Optional[List[Dict[str, Any]]] = None) -> str:
        """Stage 2: Analyze the data and generate portfolio summary"""
        print("Stage 2: Analyzing data and generating portfolio summary...")
        
        if projects_data is None:
            projects_data = self.data_processor.load_latest_portfolio_data()
            if not projects_data:
                print("No data found. Please run stage 1 first or provide data.")
                return ""
        
        # Count total user commits from the data
        total_commits = sum(project.get('user_commits_count', 0) for project in projects_data)
        print(f"Analyzing {len(projects_data)} projects with {total_commits} total user commits...")
        
        # Estimate JSON size and reduce if necessary
        json_size = self.data_processor.estimate_json_size(projects_data)
        print(f"Estimated JSON size: {json_size:,} characters")
        
        # If JSON is too large, apply further reduction
        if json_size > 150000:  # Conservative limit to stay under 200k tokens
            print("JSON size is large, applying further reduction...")
            projects_data = self.data_processor.reduce_json_size_further(projects_data)
            new_size = self.data_processor.estimate_json_size(projects_data)
            print(f"Reduced JSON size to: {new_size:,} characters")
        
        print("Generating portfolio summary...")
        summary = self.generate_summary(projects_data)
        
        # Save files
        self.data_processor.save_results(projects_data, summary)
        
        print(f"Stage 2 completed! Portfolio summary generated.")
        return summary
    
    def generate_summary(self, projects: List[Dict[str, Any]]) -> str:
        """Generate portfolio summary using AI provider"""
        project_data = json.dumps(projects, indent=2)
        
        # Get top 5 projects by various metrics
        top_projects_by_commits = sorted(projects, key=lambda p: p.get('user_commits_count', 0), reverse=True)[:5]
        
        # Calculate lines of code estimation
        lines_data = FileAnalyzer.estimate_lines_of_code(projects)
        total_lines = lines_data['total_lines']
        lines_by_language = lines_data['by_language']
        
        # Format top projects summary
        top_projects_summary = []
        for project in top_projects_by_commits:
            summary = {
                'name': project.get('name', 'Unknown'),
                'commits': project.get('user_commits_count', 0),
                'stars': project.get('stars', 0),
                'description': project.get('description', ''),
                'languages': list(project.get('languages', {}).keys())[:3],
                'project_type': project.get('folder_structure', {}).get('project_type', 'general')
            }
            top_projects_summary.append(summary)
        
        prompt = self._build_summary_prompt(
            projects, project_data, top_projects_summary, total_lines, lines_by_language
        )
        
        try:
            return self.ai_provider.generate_summary(prompt)
        except Exception as e:
            print(f"Error generating summary with AI provider: {e}")
            return "Error generating portfolio summary."
    
    def _build_summary_prompt(
        self, 
        projects: List[Dict[str, Any]], 
        project_data: str, 
        top_projects_summary: List[Dict[str, Any]], 
        total_lines: int, 
        lines_by_language: Dict[str, int]
    ) -> str:
        """Build the prompt for AI summary generation"""
        return f"""
You are a professional portfolio writer and technical recruiter. Based on the following detailed project data from GitHub and GitLab repositories, create a comprehensive portfolio summary that highlights the developer's skills, contributions, and expertise.

**Key Statistics:**
- Total Projects: {len(projects)}
- Total User Commits: {sum(p.get('user_commits_count', 0) for p in projects)}
- Total Stars Earned: {sum(p.get('stars', 0) for p in projects)}
- Estimated Lines of Code: {total_lines:,}
- Top Languages by Lines: {', '.join([f'{lang} ({lines:,})' for lang, lines in sorted(lines_by_language.items(), key=lambda x: x[1], reverse=True)[:5]])}

**Top 5 Projects by Contribution:**
{json.dumps(top_projects_summary, indent=2)}

Project Data includes:
- Repository metadata (stars, forks, dates, topics, commit counts)
- README content providing project context and documentation quality
- Folder structure and file organization showing architectural understanding
- Programming languages and technologies with usage statistics
- Commit history showing development patterns and consistency
- Project types and complexity indicators
- Code quality metrics (stars, forks, activity levels)

Project Data:
{project_data}

Please create a comprehensive portfolio summary with the following sections:

## 1. Executive Summary
- Developer profile overview with estimated lines of code ({total_lines:,})
- Years of experience estimation based on project timeline
- Primary technical focus areas
- Notable achievements and standout projects

## 2. Top 5 Featured Projects
Create a detailed section highlighting the top 5 projects from the summary above, including:
- Project name and description
- Technical stack and complexity
- Your contribution level (commits, impact)
- Key features and innovations
- Business value and real-world applicability

## 3. Technical Skills & Expertise
- Programming languages (ranked by proficiency evidence and lines of code)
- Frameworks and libraries (with usage context)
- Development tools and environments
- Architecture patterns and design principles demonstrated
- Database technologies and data handling
- DevOps and deployment practices

## 4. Project Portfolio Analysis
- Most significant projects (based on commits, complexity, and impact)
- Project diversity and problem-solving range
- Evidence of full-stack capabilities
- Open source contributions and community engagement
- Commercial vs. personal project balance

## 5. Development Practices & Code Quality
- Code organization and architectural patterns
- Documentation quality and README standards
- Commit message quality and development workflow
- Testing practices and quality assurance
- Version control and collaboration patterns

## 6. Professional Growth & Learning
- Technology adoption timeline
- Increasing project complexity over time
- Learning new technologies and adaptation
- Problem-solving evolution and expertise development

## 7. Standout Qualities
- Unique technical combinations or specializations
- Innovation and creative problem-solving
- Leadership and mentoring evidence
- Industry-specific expertise

## 8. Portfolio Presentation Recommendations
- Which projects to highlight in interviews
- Technical talking points for each major project
- Areas of expertise to emphasize
- Potential areas for continued development

Analysis Guidelines:
- Weight projects by commit count, stars, forks, and recent activity
- Consider README quality as documentation/communication skills indicator
- Evaluate technology stack diversity and depth
- Look for patterns in commit messages showing professional development practices
- Assess project complexity through folder structure and file types
- Consider real-world applicability and business value of projects
- Emphasize the estimated {total_lines:,} lines of code as a measure of coding experience

Format the response in professional markdown suitable for portfolio presentation.
"""
    
    def _print_troubleshooting_tips(self) -> None:
        """Print troubleshooting tips for when no projects are found"""
        print("\nDEBUG: Troubleshooting tips:")
        print("1. Verify your GitHub/GitLab tokens have the correct permissions")
        print("2. Check if user info was retrieved correctly (see output above)")
        print("3. Try lowering --min-commits if you have commits but they're not being counted")
        print("4. Ensure your commit email matches your GitHub/GitLab account email")
    
    def run(self) -> None:
        """Main execution method with stage support"""
        print("Starting portfolio generation...")
        
        # Show model info
        model_info = self.get_model_info()
        print(f"Using AI Model: {model_info['provider'].upper()} {model_info['model']}")
        if model_info['is_free']:
            print("  - Free tier available")
        if model_info['has_reasoning']:
            print("  - Has reasoning capabilities")
        if model_info['is_cheaper']:
            print("  - Cheaper option")
        print()
        
        # Handle stage-specific execution
        if self.config.stage == 1:
            print("Running Stage 1 only: Data collection")
            self.run_stage_1()
            return
        elif self.config.stage == 2:
            print("Running Stage 2 only: Data analysis")
            self.run_stage_2()
            return
        
        # Default behavior: run both stages or use existing data
        if self.config.use_existing_data:
            existing_data = self.data_processor.load_latest_portfolio_data()
            if existing_data:
                print("Generating portfolio summary from existing data...")
                self.run_stage_2(existing_data)
                print("\nPortfolio generation completed using existing data!")
                return
            else:
                print("No existing data found, proceeding with fresh data collection...")
        
        # Run both stages
        print("Running both stages: Data collection and analysis")
        projects_data = self.run_stage_1()
        if projects_data:
            self.run_stage_2(projects_data)
            print("\nPortfolio generation completed!")
            print("\nFiles generated:")
            print("- Portfolio Summary: Comprehensive overview and analysis")
            print("- Raw Data: Complete JSON data for further analysis")