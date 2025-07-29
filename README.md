# Project Overview

The AI Documentation Generator is a Python-based application designed to automatically analyze codebases and generate comprehensive documentation. It leverages AI models and a multi-agent architecture to provide detailed insights into code structure, dependencies, and functionality.

- **Purpose**: Automate the creation of high-quality documentation for software projects.
- **Main Functionality**: Code analysis, documentation generation, and integration with GitLab for automated updates.
- **Key Features**:
    - Multi-agent architecture for specialized analysis tasks.
    - Command-line interface for easy integration into development workflows.
    - Support for OpenAI and Gemini LLMs.
    - GitLab integration for automated analysis and merge request creation.
    - Comprehensive configuration management with YAML and environment variables.
- **Intended Use Cases**:
    - Automating documentation for large codebases.
    - Improving developer onboarding and knowledge sharing.
    - Ensuring documentation stays up-to-date with code changes.

## Table of Contents

## API Documentation

### Overview
This project is an AI-powered code documentation generator that provides a command-line interface rather than traditional REST APIs. The system operates through CLI commands and does not expose HTTP endpoints for external consumption.

### Command-Line Interface
The application serves functionality through three main CLI commands:

#### Analyze Command
- **Command**: `ai-doc-gen analyze`
- **Description**: Runs comprehensive code analysis on a repository
- **Parameters**:
  - `--repo-path` (required): Path to the repository to analyze
  - `--exclude-code-structure`: Skip code structure analysis
  - `--exclude-data-flow`: Skip data flow analysis  
  - `--exclude-dependencies`: Skip dependency analysis
  - `--exclude-request-flow`: Skip request flow analysis
  - `--exclude-api-analysis`: Skip API analysis
- **Output**: Creates analysis files in `{repo_path}/.ai/docs/`:
  - `structure_analysis.md`
  - `dependency_analysis.md`
  - `data_flow_analysis.md`
  - `request_flow_analysis.md`
  - `api_analysis.md`

#### Document Command
- **Command**: `ai-doc-gen document`
- **Description**: Generates comprehensive README documentation
- **Parameters**:
  - `--repo-path` (required): Path to the repository
  - Various `--exclude-*` flags for README sections
  - `--use-existing-readme`: Incorporate existing README content
- **Output**: Creates/updates `README.md` in the repository root

#### Cronjob Command
- **Command**: `ai-doc-gen cronjob analyze`
- **Description**: Automated analysis for GitLab projects
- **Parameters**:
  - `--max-days-since-last-commit`: Filter projects by activity (default: 30)
  - `--working-path`: Temporary directory for cloning (default: `/tmp/cronjob/projects`)
  - `--group-project-id`: GitLab group ID to analyze (default: 3)
- **Output**: Creates merge requests with analysis results

### Authentication & Security
- **CLI Access**: No authentication required for local usage
- **GitLab Integration**: Uses OAuth token (`GITLAB_OAUTH_TOKEN`) for repository access
- **LLM Services**: Requires API keys for analyzer and documenter models
- **Observability**: Optional Langfuse integration for monitoring

### Rate Limiting & Constraints
- **LLM API Limits**: Subject to configured model provider rate limits
- **GitLab API**: Standard GitLab API rate limiting applies
- **Parallel Processing**: Configurable parallel tool calls for LLM agents
- **Timeout Settings**: 180-second timeout for LLM requests
- **Token Limits**: 8192 max tokens per LLM response

## Data Flow Analysis

The AI documentation generator uses several key data models to structure and manage information flow:

### Data Models Overview

The AI documentation generator uses several key data models to structure and manage information flow:

#### Configuration Models
- **BaseHandlerConfig**: Core configuration model with `repo_path` and optional `config` path fields. Uses Pydantic validation to ensure repository paths exist and resolves default config paths automatically.
- **AnalyzeHandlerConfig**: Extends BaseHandlerConfig with analyzer-specific settings including boolean flags to exclude different analysis types (code structure, data flow, dependencies, request flow, API analysis).
- **ReadmeHandlerConfig**: Combines BaseHandlerConfig with DocumenterAgentConfig for README generation configuration.
- **JobAnalyzeHandlerConfig**: Configuration for cronjob execution with fields for commit timing, working paths, and group project IDs.

#### Agent Result Models
- **AnalyzerResult**: Simple wrapper containing `markdown_content` field for analysis output.
- **DocumenterResult**: Similar structure for documentation generation output.

#### Configuration Structures
- **ReadmeConfig**: Detailed configuration model controlling README section inclusion/exclusion with boolean flags for each section (project overview, architecture, API docs, etc.).

### Data Transformation Map

The system implements a multi-stage data transformation pipeline:

#### Configuration Loading Pipeline
1. **Environment Variables** â†’ **Config Module**: Environment variables are loaded and converted to typed configuration objects using `str_to_bool()` helper for boolean conversion.
2. **YAML Files** â†’ **Dictionary Structures**: Configuration files are parsed using `yaml.safe_load()` and traversed using dot notation for nested access.
3. **CLI Arguments** â†’ **Configuration Objects**: Command-line arguments are mapped to Pydantic model fields and merged with file-based configuration.
4. **Merged Configuration**: The `load_config()` function implements precedence order: defaults â†’ file config â†’ CLI args.

#### Analysis Data Flow
1. **Repository Path** â†’ **File System Analysis**: Tools scan directory structures and read file contents.
2. **Raw Code** â†’ **Structured Analysis**: AI agents process code through specialized analyzers (structure, data flow, dependencies, request flow).
3. **Analysis Results** â†’ **Markdown Documents**: Each analyzer produces structured markdown output stored in `.ai/docs/` directory.
4. **Multiple Analyses** â†’ **Consolidated Documentation**: The documenter agent combines all analysis files into comprehensive README documentation.

#### Prompt Template Processing
1. **YAML Templates** â†’ **Jinja2 Templates**: PromptManager loads YAML files and caches Jinja2 template objects.
2. **Template Variables** â†’ **Rendered Prompts**: Configuration values are injected into templates using `render_prompt()` method.

### Storage Interactions

#### File System Operations
- **Configuration Storage**: YAML files stored in `.ai/config.yaml` within repository directories.
- **Analysis Output**: Markdown files written to `.ai/docs/` directory with specific naming conventions:
  - `structure_analysis.md`
  - `data_flow_analysis.md` 
  - `dependency_analysis.md`
  - `request_flow_analysis.md`
  - `api_analysis.md`
- **Documentation Output**: Final README.md written to repository root.

#### Git Repository Interactions
- **Repository Cloning**: GitPython used for cloning repositories in cronjob mode.
- **Branch Management**: Automatic branch creation for analysis updates.
- **Commit Operations**: Automated commits with structured commit messages.

#### Logging Storage
- **Structured Logging**: JSON-formatted logs with timestamps and structured data.
- **File-based Logging**: Logs stored in timestamped files within `logs/` directory hierarchy.
- **Multiple Handlers**: Separate file and console handlers with configurable log levels.

### Validation Mechanisms

#### Pydantic Model Validation
- **Field Validation**: All configuration models use Pydantic for type checking and validation.
- **Path Validation**: Repository paths validated for existence using `@model_validator`.
- **Required Fields**: Critical fields marked as required with descriptive error messages.

#### Configuration Validation
- **File Existence Checks**: Config files validated before loading.
- **YAML Parsing**: Structured error handling for malformed YAML files.
- **Template Validation**: Jinja2 template syntax validated during rendering.

#### Analysis Validation
- **Output File Validation**: `validate_succession()` method ensures all expected analysis files are created.
- **Content Validation**: AI agents use structured output types to ensure consistent markdown format.

#### Git Operations Validation
- **Repository Validation**: Git repository status checked before operations.
- **Branch Validation**: Existing branch checks prevent conflicts.
- **Commit Validation**: Commit message structure enforced.

### State Management Analysis

#### Configuration State
- **Singleton Logger**: Logger class uses singleton pattern to maintain consistent logging state across the application.
- **Environment-based Config**: Configuration loaded once at startup and passed through dependency injection.
- **Template Caching**: PromptManager caches Jinja2 templates for performance optimization.

#### Agent Execution State
- **Concurrent Execution**: Multiple analyzer agents run concurrently using `asyncio.gather()`.
- **Error Isolation**: Individual agent failures don't stop other agents from completing.
- **Progress Tracking**: OpenTelemetry spans track agent execution progress and performance metrics.

#### File System State
- **Directory Creation**: Automatic creation of required directories (`logs/`, `.ai/docs/`).
- **File Overwriting**: Analysis files overwritten on each run to ensure freshness.
- **Cleanup Operations**: Temporary directories cleaned up after cronjob execution.

### Serialization Processes

#### Configuration Serialization
- **YAML Serialization**: Configuration objects serialized to/from YAML format using `yaml.safe_load()`.
- **Environment Variable Parsing**: String-based environment variables converted to appropriate types.
- **Pydantic Serialization**: Model objects serialized using `model_dump()` for template rendering.

#### Logging Serialization
- **JSON Serialization**: Structured log data serialized using `ujson` for performance.
- **Message Formatting**: Log messages formatted with timestamps and structured data.

#### Template Serialization
- **Template Variable Injection**: Configuration objects serialized into template context dictionaries.
- **Markdown Output**: Final analysis results serialized as markdown strings.

### Data Lifecycle Diagrams

#### Configuration Lifecycle
```
Environment Variables â†’ Config Module â†’ Pydantic Models â†’ Agent Configuration
                    â†—                                  â†˜
YAML Files â†’ Dictionary Merge â†’ Validation â†’ Dependency Injection
                    â†—
CLI Arguments â†’ Argument Parsing
```

#### Analysis Lifecycle
```
Repository Path â†’ File System Scan â†’ AI Agent Processing â†’ Markdown Generation â†’ File Storage
                                  â†˜                      â†—
                                   Tool Execution â†’ Content Analysis
```

#### Cronjob Lifecycle
```
GitLab API â†’ Project List â†’ Repository Clone â†’ Analysis Execution â†’ Commit & Push â†’ Cleanup
                         â†˜                   â†—
                          Validation Checks â†’ Branch Creation
```

#### Logging Lifecycle
```
Application Events â†’ Logger Instance â†’ Format & Serialize â†’ File/Console Output
                                   â†˜                     â†—
                                    Structured Data â†’ JSON Serialization
```

## Dependency Analysis

### Internal Dependencies Map

#### Core Module Dependencies

**Main Entry Point (`src/main.py`)**
- **Direct Dependencies**: `config`, `handlers.analyze`, `handlers.cronjob`, `handlers.readme`, `utils.Logger`
- **External Dependencies**: `argparse`, `asyncio`, `logging`, `pathlib`, `logfire`, `nest_asyncio`, `gitlab`, `pydantic`
- **Role**: Application orchestrator and CLI interface

**Configuration System (`src/config.py`)**
- **Direct Dependencies**: `utils.dict` (merge_dicts function)
- **External Dependencies**: `os`, `pathlib`, `yaml`, `dotenv`, `pydantic`
- **Role**: Centralized configuration management with multi-source merging

**Handler Layer**
- **Base Handler (`handlers/base_handler.py`)**: No internal dependencies, uses `pydantic` for validation
- **Analyze Handler (`handlers/analyze.py`)**: Depends on `agents.analyzer`, `handlers.base_handler`
- **README Handler (`handlers/readme.py`)**: Depends on `agents.documenter`, `handlers.base_handler`
- **Cronjob Handler (`handlers/cronjob.py`)**: Depends on `handlers.analyze`, `handlers.base_handler`, `config`, `utils.Logger`, `utils.dict`

**Agent System**
- **AnalyzerAgent (`agents/analyzer.py`)**: Depends on `agents.tools`, `utils.Logger`, `utils.PromptManager`, `config`
- **DocumenterAgent (`agents/documenter.py`)**: Depends on `agents.tools`, `utils.Logger`, `utils.PromptManager`, `utils.custom_models.gemini_provider`, `config`

**Tool System**
- **Tools Package (`agents/tools/__init__.py`)**: Exports `FileReadTool` and `ListFilesTool`
- **FileReadTool (`agents/tools/file_tool/file_reader.py`)**: No internal dependencies
- **ListFilesTool (`agents/tools/dir_tool/list_files.py`)**: No internal dependencies

**Utility Layer**
- **Logger (`utils/logger.py`)**: No internal dependencies
- **PromptManager (`utils/prompt_manager.py`)**: No internal dependencies
- **Repository Utils (`utils/repo.py`)**: No internal dependencies
- **Dictionary Utils (`utils/dict.py`)**: No internal dependencies
- **Custom Models (`utils/custom_models/gemini_provider.py`)**: No internal dependencies

#### Dependency Flow Patterns

**Configuration Flow**: `main.py` â†’ `config.py` â†’ `utils.dict` â†’ Handler instantiation
**Execution Flow**: `main.py` â†’ Handler â†’ Agent â†’ Tools â†’ External APIs
**Logging Flow**: All modules â†’ `utils.Logger` â†’ File/Console output
**Template Flow**: Agents â†’ `utils.PromptManager` â†’ YAML templates â†’ Jinja2 rendering

### External Libraries Analysis

#### Core Framework Dependencies

**pydantic-ai (>=0.4.2)**
- **Usage**: Primary AI agent framework for LLM interactions
- **Components**: `Agent`, `Tool`, `ModelSettings`, `AgentRunResult`
- **Integration Points**: All agent classes, tool definitions, model configuration
- **Features Used**: Agent orchestration, tool calling, structured outputs, retry mechanisms

**pydantic (>=2.11.7)**
- **Usage**: Data validation and configuration management
- **Components**: `BaseModel`, `Field`, `model_validator`
- **Integration Points**: All configuration classes, result models, validation logic
- **Features Used**: Type validation, field descriptions, model serialization

#### AI/ML Integration

**OpenAI Integration**
- **Components**: `OpenAIModel`, `OpenAIProvider`
- **Configuration**: Environment variables for API key, base URL, model selection
- **Usage**: Primary LLM provider for both analyzer and documenter agents

**Google Gemini Integration**
- **Components**: `GeminiModel`, Custom `CustomGeminiGLA` provider
- **Configuration**: Custom provider with configurable base URL
- **Usage**: Alternative LLM provider with custom implementation

#### Observability Stack

**logfire (>=3.24.2)**
- **Usage**: OpenTelemetry-based observability and tracing
- **Integration**: Configured in main.py with Langfuse authentication
- **Features**: Distributed tracing, performance monitoring, structured logging

**OpenTelemetry**
- **Components**: `trace` module for span creation and event tracking
- **Usage**: Agent execution tracking, performance metrics, debugging
- **Integration**: Embedded in agent execution and tool operations

#### Git and Repository Management

**GitPython (>=3.1.44)**
- **Usage**: Git repository operations in cronjob handler
- **Operations**: Repository cloning, branch creation, commit operations, push operations
- **Integration**: Automated analysis workflow with GitLab

**python-gitlab (>=6.1.0)**
- **Usage**: GitLab API integration for project discovery and MR creation
- **Operations**: Project listing, branch management, merge request creation
- **Authentication**: OAuth token-based authentication

#### Template and Configuration

**Jinja2 (>=3.1.5)**
- **Usage**: Prompt template rendering in PromptManager
- **Features**: Template caching, variable substitution, nested template support
- **Integration**: AI agent prompt generation with dynamic content

**PyYAML (>=6.0)**
- **Usage**: Configuration file parsing and prompt template loading
- **Operations**: YAML file reading, nested key traversal, safe loading
- **Integration**: Configuration system and prompt management

**python-dotenv (>=1.0.0)**
- **Usage**: Environment variable loading from .env files
- **Integration**: Configuration system initialization
- **Features**: Automatic .env file discovery and loading

#### Utility Libraries

**ujson (>=5.10.0)**
- **Usage**: High-performance JSON serialization for logging
- **Integration**: Structured logging output formatting
- **Benefits**: Performance optimization for log data serialization

**nest-asyncio (>=1.6.0)**
- **Usage**: Nested asyncio event loop support
- **Integration**: Applied globally in main.py for compatibility
- **Purpose**: Enables asyncio in environments with existing event loops

**psutil (>=7.0.0)**
- **Usage**: System and process utilities
- **Integration**: Likely used for system monitoring and resource tracking
- **Features**: Process management, system information

#### Version Constraints Analysis

**Python Version**: Strictly requires Python 3.13 (`>=3.13,<3.14`)
**Dependency Versions**: All dependencies use minimum version constraints with `>=`
**Stability**: Uses stable, well-maintained packages with recent versions
**Compatibility**: No conflicting version requirements identified

### Service Integrations

#### GitLab Integration

**Authentication**: OAuth token-based authentication via `GITLAB_OAUTH_TOKEN`
**API Endpoints**: 
- Project listing and filtering
- Branch creation and management
- Merge request creation and management
- Repository access and cloning

**Integration Points**:
- `JobAnalyzeHandler` for automated project analysis
- Project filtering based on activity and criteria
- Automated branch creation with timestamp-based naming
- Merge request creation with structured titles and descriptions

**Configuration**:
- `GITLAB_API_URL`: GitLab instance URL (default: https://git.divar.cloud)
- `GITLAB_USER_NAME`: Display name for automated commits
- `GITLAB_USER_USERNAME`: Username for MR authorship
- `GITLAB_USER_EMAIL`: Email for Git commits

#### LLM Provider Integrations

**OpenAI Integration**:
- **Analyzer Configuration**: `ANALYZER_LLM_MODEL`, `ANALYZER_LLM_BASE_URL`, `ANALYZER_LLM_API_KEY`
- **Documenter Configuration**: `DOCUMENTER_LLM_MODEL`, `DOCUMENTER_LLM_BASE_URL`, `DOCUMENTER_LLM_API_KEY`
- **Features**: Parallel tool calls, temperature control, token limits, timeout configuration

**Gemini Integration**:
- **Custom Provider**: `CustomGeminiGLA` with configurable base URL
- **Usage**: Alternative to OpenAI for document generation
- **Configuration**: Custom provider implementation extending `GoogleGLAProvider`

#### Observability Integrations

**Langfuse Integration**:
- **Authentication**: Basic auth with `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY`
- **Configuration**: OTLP headers for authentication
- **Features**: Distributed tracing, performance monitoring, debugging

**OpenTelemetry Integration**:
- **Service Name**: "code-documenter"
- **Environment**: Configurable via `ENVIRONMENT` variable
- **Features**: Span creation, event tracking, attribute setting

### Dependency Injection Patterns

#### Configuration Injection

**Pattern**: Constructor-based dependency injection with Pydantic models
**Implementation**: 
- Configuration objects passed to handler constructors
- Handlers pass configuration to agent constructors
- Agents receive typed configuration objects

**Example Flow**:
```python
# Configuration loading and injection
cfg: AnalyzeHandlerConfig = load_config(args, AnalyzeHandlerConfig, "analyzer")
handler = AnalyzeHandler(cfg)  # Constructor injection
```

## Code Structure Analysis

The AI Documentation Generator is a Python-based application built with a **multi-agent architecture** that leverages AI models to automatically analyze codebases and generate comprehensive documentation. The system follows a **command-pattern architecture** with distinct handlers for different operations (analyze, document, cronjob) and employs a **tool-based agent system** using the pydantic-ai framework.

**Key Architectural Patterns:**
- **Agent-Based Architecture**: Multiple specialized AI agents (AnalyzerAgent, DocumenterAgent) with specific responsibilities
- **Command Pattern**: Handler-based execution model with separate handlers for different operations
- **Tool Pattern**: Extensible tool system for file operations and directory traversal
- **Configuration-Driven Design**: YAML-based configuration with environment variable overrides
- **Async/Await Pattern**: Fully asynchronous execution model for concurrent operations

**Technology Stack:**
- **Core Framework**: Python 3.13 with pydantic-ai for AI agent orchestration
- **AI Integration**: OpenAI/Gemini models with custom providers
- **Observability**: OpenTelemetry tracing with Logfire integration
- **Git Integration**: GitPython and python-gitlab for repository operations
- **Configuration**: YAML + environment variables with Pydantic validation

### Core Components

#### 1. **Main Entry Point** (`src/main.py`)
- **Purpose**: CLI interface and application orchestration
- **Responsibilities**: 
  - Command-line argument parsing with dynamic handler configuration
  - Logging configuration and observability setup
  - Handler instantiation and execution coordination
- **Key Functions**: `main()`, `parse_args()`, `configure_langfuse()`

#### 2. **Configuration System** (`src/config.py`)
- **Purpose**: Centralized configuration management
- **Responsibilities**:
  - Environment variable loading and validation
  - YAML configuration file parsing
  - Multi-source configuration merging (defaults â†’ file â†’ CLI)
- **Key Functions**: `load_config()`, `load_config_from_file()`, `merge_dicts()`

#### 3. **Handler Layer** (`src/handlers/`)
- **Base Handler** (`base_handler.py`): Abstract base class defining handler contract
- **Analyze Handler** (`analyze.py`): Orchestrates code analysis through AnalyzerAgent
- **README Handler** (`readme.py`): Manages documentation generation via DocumenterAgent  
- **Cronjob Handler** (`cronjob.py`): Automated GitLab project analysis and MR creation

#### 4. **Agent System** (`src/agents/`)
- **AnalyzerAgent** (`analyzer.py`): Multi-faceted code analysis (structure, dependencies, data flow, request flow, API)
- **DocumenterAgent** (`documenter.py`): README generation with configurable sections
- **Tool Integration**: File reading and directory listing capabilities

#### 5. **Utility Layer** (`src/utils/`)
- **Logger** (`logger.py`): Structured logging with file and console outputs
- **PromptManager** (`prompt_manager.py`): YAML-based prompt template management with Jinja2 rendering
- **Repository Utils** (`repo.py`): Git repository version detection
- **Dictionary Utils** (`dict.py`): Configuration merging utilities

### Service Definitions

#### **AnalyzerAgent Service**
- **Input**: Repository path and analysis configuration flags
- **Output**: Multiple markdown analysis files (structure, dependencies, data flow, request flow, API)
- **Capabilities**: 
  - Concurrent execution of specialized analysis agents
  - File system traversal and code examination
  - Architectural pattern recognition
  - Component relationship mapping

#### **DocumenterAgent Service**  
- **Input**: Repository path and README configuration options
- **Output**: Comprehensive README.md file
- **Capabilities**:
  - Multi-source analysis integration
  - Configurable section inclusion/exclusion
  - Existing README preservation option
  - Structured markdown generation

#### **Cronjob Service**
- **Input**: GitLab group configuration and project filters
- **Output**: Automated analysis and merge request creation
- **Capabilities**:
  - GitLab API integration for project discovery
  - Automated repository cloning and analysis
  - Branch creation and merge request management
  - Project filtering based on activity and criteria

### Interface Contracts

#### **Handler Interface** (`AbstractHandler`)
```python
class AbstractHandler(ABC):
    @abstractmethod
    async def handle(self):
        pass
```

#### **Configuration Contracts**
- **BaseHandlerConfig**: Repository path and config file validation
- **AnalyzerAgentConfig**: Analysis exclusion flags and repository path
- **DocumenterAgentConfig**: README section configuration and repository path
- **JobAnalyzeHandlerConfig**: Cronjob timing and GitLab integration settings

#### **Tool Interface** (pydantic-ai Tool)
- **FileReadTool**: File content reading with line range support
- **ListFilesTool**: Directory traversal with filtering capabilities

#### **Agent Output Contracts**
- **AnalyzerResult**: Structured markdown content output
- **DocumenterResult**: README markdown content output

### Design Patterns Identified

#### 1. **Multi-Agent Pattern**
- Specialized agents for different analysis types
- Concurrent execution with error isolation
- Tool-based capability extension

#### 2. **Command Pattern**
- Handler-based command execution
- Configurable command parameters
- Async command processing

#### 3. **Template Method Pattern**
- Base handler with common initialization
- Specialized handle() implementations
- Shared configuration validation

#### 4. **Strategy Pattern**
- Configurable analysis exclusions
- Multiple LLM provider support (OpenAI/Gemini)
- Flexible output formatting

#### 5. **Factory Pattern**
- Dynamic agent creation based on configuration
- Tool instantiation and registration
- Model provider selection

#### 6. **Observer Pattern**
- OpenTelemetry tracing integration
- Structured logging with event correlation
- Progress tracking and monitoring

### Component Relationships

```
CLI Entry Point (main.py)
    â†“
Configuration System (config.py)
    â†“
Handler Layer
    â”œâ”€â”€ AnalyzeHandler â†’ AnalyzerAgent
    â”œâ”€â”€ ReadmeHandler â†’ DocumenterAgent  
    â””â”€â”€ CronjobHandler â†’ GitLab Integration
                    â†“
Agent System
    â”œâ”€â”€ AnalyzerAgent (5 specialized sub-agents)
    â””â”€â”€ DocumenterAgent
                    â†“
Tool System
    â”œâ”€â”€ FileReadTool
    â””â”€â”€ ListFilesTool
                    â†“
Utility Layer
    â”œâ”€â”€ Logger (structured logging)
    â”œâ”€â”€ PromptManager (template rendering)
    â””â”€â”€ Repository Utils
```

**Data Flow:**
1. CLI arguments â†’ Configuration loading â†’ Handler selection
2. Handler â†’ Agent instantiation â†’ Tool registration  
3. Agent â†’ LLM interaction â†’ Tool execution â†’ Result generation
4. Result â†’ File output â†’ Logging/Tracing

### Key Methods & Functions

#### **Core Orchestration**
- `main()`: Application entry point and command routing
- `parse_args()`: Dynamic CLI argument generation from Pydantic models
- `configure_langfuse()`: Observability and tracing setup

#### **Configuration Management**
- `load_config()`: Multi-source configuration merging
- `merge_dicts()`: Recursive dictionary merging for configuration layers

#### **Agent Execution**
- `AnalyzerAgent.run()`: Concurrent multi-agent analysis execution
- `DocumenterAgent.run()`: README generation orchestration
- `_run_agent()`: Individual agent execution with error handling and metrics

#### **Tool Operations**
- `FileReadTool._run()`: File content reading with line range support
- `ListFilesTool._run()`: Directory traversal with filtering

#### **GitLab Integration**
- `JobAnalyzeHandler._is_applicable_project()`: Project filtering logic
- `_create_merge_request()`: Automated MR creation with analysis results

#### **Utility Functions**
- `Logger.init()`: Structured logging configuration
- `PromptManager.render_prompt()`: Jinja2 template rendering
- `get_repo_version()`: Git repository version detection
