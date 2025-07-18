#!/usr/bin/env python3
"""
Portfolio Generator CLI
Command line interface for the portfolio generator application
"""

import argparse
import sys
from typing import Optional

from src.portfolio_generator import PortfolioGenerator
from src.config import PortfolioConfig, ConfigManager
from src.ai_providers.base import AIProviderConfigError
from src.repository_managers.base import RepositoryError
from src.utils import Logger


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser"""
    parser = argparse.ArgumentParser(
        description="Generate portfolio from GitHub and GitLab projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate portfolio using default settings
  %(prog)s
  
  # Generate portfolio for specific usernames
  %(prog)s --github-username myuser --gitlab-username myuser
  
  # Use existing data to regenerate summary
  %(prog)s --use-existing
  
  # Only collect data (stage 1)
  %(prog)s --stage 1
  
  # Only analyze existing data (stage 2)
  %(prog)s --stage 2
  
  # Use specific AI provider
  %(prog)s --model-provider anthropic --model-name claude-3-5-sonnet-latest
  
  # Limit commits and analyze only GitHub
  %(prog)s --platform github --max-commits 50
"""
    )
    
    # Repository options
    repo_group = parser.add_argument_group('Repository Options')
    repo_group.add_argument(
        "--github-username", 
        help="GitHub username (optional if using token)"
    )
    repo_group.add_argument(
        "--gitlab-username", 
        help="GitLab username (optional if using token)"
    )
    repo_group.add_argument(
        "--platform", 
        choices=['github', 'gitlab'], 
        help="Analyze only specific platform (default: analyze both)"
    )
    
    # Processing options
    process_group = parser.add_argument_group('Processing Options')
    process_group.add_argument(
        "--use-existing", 
        action="store_true", 
        help="Use the most recent portfolio data file instead of fetching new data"
    )
    process_group.add_argument(
        "--stage", 
        type=int, 
        choices=[1, 2], 
        help="Run specific stage: 1=get JSON data, 2=analyze data (default: run both stages)"
    )
    process_group.add_argument(
        "--min-commits", 
        type=int, 
        default=1, 
        help="Minimum user commits required for a project to be included (default: 1)"
    )
    process_group.add_argument(
        "--max-commits", 
        type=int, 
        help="Maximum commits per project to include in JSON (default: all commits)"
    )
    
    # AI provider options
    ai_group = parser.add_argument_group('AI Provider Options')
    ai_group.add_argument(
        "--model-provider", 
        choices=['anthropic', 'openai', 'google'], 
        default='google', 
        help="AI provider to use (default: google)"
    )
    ai_group.add_argument(
        "--model-name", 
        help="Specific model name to use (default: provider-specific default)"
    )
    
    # Other options
    other_group = parser.add_argument_group('Other Options')
    other_group.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug logging"
    )
    other_group.add_argument(
        "--check-config", 
        action="store_true", 
        help="Check configuration and exit"
    )
    
    return parser


def check_configuration() -> None:
    """Check and print configuration status"""
    print("Portfolio Generator Configuration Check")
    print("=" * 40)
    
    ConfigManager.print_environment_status()
    
    # Check for at least one repository token
    github_token = ConfigManager.get_github_token()
    gitlab_token = ConfigManager.get_gitlab_token()
    
    if not github_token and not gitlab_token:
        print("WARNING: No repository tokens found. You'll only be able to access public repositories.")
        print("   Set GITHUB_TOKEN and/or GITLAB_TOKEN environment variables for full access.")
        print()
    
    # Check AI provider keys
    keys = ConfigManager.get_ai_api_keys()
    available_providers = [provider for provider, key in keys.items() if key]
    
    if not available_providers:
        print("ERROR: No AI provider API keys found.")
        print("   Set at least one of: ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY")
        sys.exit(1)
    else:
        print(f"SUCCESS: Available AI providers: {', '.join(available_providers)}")
        print()


def main() -> None:
    """Main CLI entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Set up logging
    logger = Logger.get_logger()
    if args.debug:
        Logger.set_debug_mode(True)
        logger.debug("Debug mode enabled")
    
    # Check configuration if requested
    if args.check_config:
        check_configuration()
        return
    
    try:
        # Create configuration from arguments
        config = PortfolioConfig.from_args(args)
        
        # Validate that we have required API keys
        if not ConfigManager.validate_ai_provider_key(config.model_provider):
            # Map provider names to correct environment variable names
            env_var_map = {
                'anthropic': 'ANTHROPIC_API_KEY',
                'openai': 'OPENAI_API_KEY',
                'google': 'GEMINI_API_KEY'  # Google provider uses GEMINI_API_KEY
            }
            required_key = env_var_map.get(config.model_provider.lower(), f"{config.model_provider.upper()}_API_KEY")
            print(f"ERROR: {required_key} environment variable is required for {config.model_provider} provider")
            print("\nRun 'python portfolio_generator_cli.py --check-config' to see all configuration options.")
            sys.exit(1)
        
        # Create and run portfolio generator
        generator = PortfolioGenerator(config)
        generator.run()
        
    except AIProviderConfigError as e:
        print(f"AI Provider Configuration Error: {e}")
        print("\nRun 'python portfolio_generator_cli.py --check-config' to see available providers.")
        sys.exit(1)
    except RepositoryError as e:
        print(f"Repository Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()