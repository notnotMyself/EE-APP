## ADDED Requirements

### Requirement: Agent Registration and Management

The system SHALL provide an AgentManager that registers and manages multiple AI agents with isolated workspaces.

#### Scenario: Register agent with workspace

- **WHEN** AgentManager initializes
- **THEN** it SHALL register all configured agents with unique roles and workspace directories
- **AND** each agent SHALL have an AgentConfig containing name, role, workdir, and description

#### Scenario: Retrieve agent configuration

- **WHEN** requesting agent config by role (e.g., "dev_efficiency_analyst")
- **THEN** the manager SHALL return the corresponding AgentConfig
- **AND** the config SHALL include the absolute path to the agent's workspace

### Requirement: Workspace Isolation

Each AI agent SHALL operate within an isolated workspace directory that contains its instructions, skills, data, and outputs.

#### Scenario: Agent workspace structure

- **WHEN** an agent workspace is created
- **THEN** it SHALL contain a CLAUDE.md file defining agent behavior
- **AND** it SHALL contain a .claude/skills/ directory for executable Python scripts
- **AND** it MAY contain data/ and reports/ directories for agent-specific files

#### Scenario: Workspace path resolution

- **WHEN** an agent executes a tool (e.g., bash, read_file, write_file)
- **THEN** all file paths SHALL be resolved relative to the agent's workspace directory
- **AND** the agent SHALL NOT access files outside its workspace

### Requirement: CLAUDE.md Instruction Loading

The system SHALL load each agent's behavior definition from a CLAUDE.md file in its workspace and provide it as the system prompt.

#### Scenario: Load agent instructions from CLAUDE.md

- **WHEN** creating a conversation with an agent
- **THEN** the manager SHALL read {workspace}/CLAUDE.md
- **AND** use its content as the system prompt for Claude API
- **AND** if CLAUDE.md does not exist, fall back to a default prompt with agent name and description

#### Scenario: System prompt structure

- **WHEN** CLAUDE.md is loaded successfully
- **THEN** the system prompt SHALL include the agent's role definition, core responsibilities, available capabilities, workflow procedures, and working principles
- **AND** the prompt SHALL guide the agent's behavior during conversations

### Requirement: Multi-Agent Support

The system SHALL support registering and running multiple specialized AI agents simultaneously.

#### Scenario: Register multiple agents

- **WHEN** AgentManager initializes
- **THEN** it SHALL register at least the following agents:
  - dev_efficiency_analyst (研发效能分析官)
  - nps_insight_analyst (NPS洞察官)
  - product_requirement_analyst (产品需求提炼官)
  - competitor_tracking_analyst (竞品追踪分析官)
  - knowledge_management_assistant (企业知识管理官)
- **AND** each agent SHALL have a unique role identifier

#### Scenario: Agent metadata availability

- **WHEN** querying agent list
- **THEN** each agent SHALL expose its Chinese name, role ID, workspace path, and description
- **AND** this metadata SHALL be available for frontend display and routing
