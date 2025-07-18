# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-01-XX

### 🚀 Major Release - Complete Architectural Refactor

### Added
- **Modular Architecture**: Complete refactor into clean, maintainable components
- **Professional CLI**: New `portfolio_generator_cli.py` with comprehensive help system
- **Configuration Management**: Centralized configuration with validation
- **Error Handling**: Comprehensive error handling with specific exception types
- **Logging System**: Centralized logging with debug mode support
- **Factory Pattern**: Easy extensibility for AI providers and repository managers
- **Configuration Validation**: Environment variable checking and validation
- **Debug Mode**: Enhanced debugging capabilities with `--debug` flag
- **Professional Documentation**: Comprehensive README with badges and structure
- **Contributing Guidelines**: Detailed contribution guidelines for open-source collaboration
- **GNU GPL License**: Open-source license for community contributions
- **Architecture Documentation**: Detailed architecture overview and design principles

### Changed
- **Breaking**: New CLI interface with improved argument structure
- **Breaking**: Modular code structure - old imports will not work
- **Improved**: Better error messages and user feedback
- **Enhanced**: Configuration checking with `--check-config` command
- **Optimized**: Better separation of concerns and testability
- **Streamlined**: Cleaner code organization and maintainability

### Technical Improvements
- **Single Responsibility Principle**: Each class has one clear purpose
- **Open/Closed Principle**: Easy to extend without modifying existing code
- **Dependency Inversion**: High-level modules depend on abstractions
- **Interface Segregation**: Focused and specific interfaces
- **Error Handling**: Specific exception types for different scenarios
- **Testability**: Components can be unit tested in isolation
- **Extensibility**: Simple to add new AI providers or repository platforms

### Migration Notes
- **CLI**: Use `portfolio_generator_cli.py` instead of `portfolio_generator.py`
- **Configuration**: Environment variables remain the same
- **Backward Compatibility**: Legacy script still available during transition
- **New Features**: Access new features through the modern CLI interface

---

## [1.6.0] - 2023-12-XX

### Enhanced Portfolio Analysis & Simplified Workflow

### Added
- **Lines of Code Estimation**: Automatically estimates total lines of code across all projects
- **Top 5 Projects Highlight**: AI identifies and features your most significant projects
- **Enhanced AI Analysis**: Improved project ranking and technical skill assessment
- **Performance Improvements**: Faster execution with simplified two-stage process

### Changed
- **Streamlined Workflow**: Removed HTML generation for faster, focused portfolio creation
- **Improved Analysis**: Better project significance detection and ranking

### Removed
- **HTML Generation**: Removed to focus on core portfolio analysis functionality

---

## [1.5.0] - 2023-11-XX

### Multi-AI Provider Support

### Added
- **Multiple AI Providers**: Support for Anthropic Claude, OpenAI GPT, and Google Gemini
- **Smart Model Selection**: Choose from reasoning models, cheaper options, and free tiers
- **Gemini 2.5 Pro Default**: Best free model with excellent analysis capabilities
- **Model Recommendations**: Built-in guidance for choosing the right model for your needs
- **Provider-Specific Configuration**: Flexible API key management for different providers

### Changed
- **Default Provider**: Changed from Anthropic to Google Gemini for better accessibility
- **Enhanced Documentation**: Comprehensive model comparison and recommendations

### Maintained
- **Backward Compatibility**: Existing API keys continue to work seamlessly
- **Same Interface**: No breaking changes to command-line interface

---

## [1.3.0] - 2023-10-XX

### Smart Data Filtering & Clean JSON Output

### Added
- **Conditional Attribute Inclusion**: Only includes stars/forks if > 0, descriptions/READMEs if not empty
- **Total Commits Tracking**: Shows total commits from all users (not just authenticated user)
- **Enhanced Data Quality**: Cleaner, more meaningful data for AI analysis

### Changed
- **Cleaner JSON Data**: Removes irrelevant repository flags and empty attributes
- **Focused Analysis**: AI gets higher quality data for better portfolio generation
- **Improved Filtering**: More intelligent data selection and presentation

### Removed
- **Irrelevant Attributes**: Removed `has_issues`, `has_projects`, `has_wiki`, `has_pages`, `default_branch`, `open_issues_count`, `language`
- **Empty Data**: Eliminated empty descriptions, READMEs, and zero-value metrics

---

## [1.2.0] - 2023-09-XX

### Enhanced AI Analysis & Project Details

### Added
- **Comprehensive AI Prompts**: Significantly improved AI analysis with professional portfolio writing approach
- **Interactive HTML Portfolio**: Complete responsive website with project showcase and professional presentation
- **Duplicate Commit Filtering**: Ignores commits with identical messages to focus on unique contributions
- **Enhanced Sorting**: Projects sorted by commits, stars, forks, and documentation quality
- **Interview Preparation**: AI-generated talking points and project highlights for interviews

### Changed
- **Improved Analysis Quality**: Much more detailed and professional portfolio summaries
- **Better Data Processing**: More intelligent filtering and organization of project data
- **Enhanced User Experience**: Professional presentation suitable for job applications

### Fixed
- **Duplicate Detection**: Better handling of repetitive commit messages
- **Data Organization**: Improved project ranking and categorization

---

## [1.1.0] - 2023-08-XX

### Improved Commit Detection & Platform Selection

### Added
- **Enhanced Commit Detection**: Improved user commit detection by tracking multiple email addresses and usernames
- **Platform Selection**: New `--platform` option to analyze only GitHub or only GitLab repositories
- **Enhanced Debugging**: Added detailed output to help troubleshoot commit counting issues
- **Better Error Handling**: More informative error messages and troubleshooting tips

### Changed
- **Improved Accuracy**: Better matching of commits to authenticated user
- **Enhanced Debugging**: More detailed output for troubleshooting
- **Flexible Analysis**: Option to focus on specific platforms

### Fixed
- **Commit Counting Issues**: Resolved problems with commit attribution
- **User Identification**: Better handling of multiple email addresses and usernames

---

## [1.0.0] - 2023-07-XX

### Initial Release

### Added
- **GitHub Integration**: Fetch public and private repositories from GitHub
- **GitLab Integration**: Fetch public and private repositories from GitLab (including self-hosted)
- **AI-Powered Analysis**: Generate comprehensive portfolio summaries using Anthropic Claude
- **Repository Analysis**: Extract stars, forks, languages, commit history, and file structure
- **Stage-Based Execution**: Separate data collection and analysis phases
- **Commit Filtering**: Configurable minimum commit thresholds
- **Rate Limiting**: Automatic handling of API rate limits
- **JSON Output**: Structured data output for further analysis
- **Markdown Summary**: Professional portfolio summaries in Markdown format
- **Token-Based Auth**: Support for GitHub and GitLab personal access tokens
- **Public Repository Support**: Analyze public repositories without authentication
- **Comprehensive Documentation**: Full setup and usage instructions

### Core Features
- **Multi-Platform Support**: Both GitHub and GitLab repositories
- **Private Repository Access**: Full support with proper authentication
- **Intelligent Filtering**: Skip forks and focus on meaningful contributions
- **Professional Output**: AI-generated portfolio summaries suitable for job applications
- **Flexible Configuration**: Environment variable-based configuration
- **Error Handling**: Comprehensive error handling and user feedback

---

## Development Guidelines

### Version Numbering
- **Major (X.0.0)**: Breaking changes, architectural changes, major new features
- **Minor (X.Y.0)**: New features, significant improvements, backward compatible
- **Patch (X.Y.Z)**: Bug fixes, minor improvements, documentation updates

### Changelog Categories
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

### Release Process
1. Update version in `setup.py`
2. Update CHANGELOG.md with new version
3. Update badges in README.md
4. Create release tag
5. Update documentation as needed

---

**Note**: This project follows [Semantic Versioning](https://semver.org/). For the versions available, see the [releases on GitHub](https://github.com/yourusername/portfolio-generator/releases).