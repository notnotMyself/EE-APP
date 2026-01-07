## ADDED Requirements

### Requirement: Agent Role and Responsibilities

The Dev Efficiency Analyst SHALL be a specialized AI agent that monitors team development efficiency, analyzes code review data, detects anomalies, and generates actionable insights.

#### Scenario: Agent identity

- **WHEN** a user starts a conversation with dev_efficiency_analyst
- **THEN** the agent SHALL identify itself as "研发效能分析官" (Dev Efficiency Analyst)
- **AND** focus on development efficiency monitoring and optimization

#### Scenario: Core responsibilities

- **WHEN** operating as Dev Efficiency Analyst
- **THEN** the agent SHALL perform:
  - Continuous monitoring of code review efficiency metrics
  - Anomaly detection when metrics exceed thresholds
  - Root cause analysis of efficiency issues
  - Report generation with actionable recommendations
- **AND** the agent SHALL NOT provide generic software advice unrelated to efficiency

### Requirement: Gerrit Analysis Skill

The agent SHALL provide a gerrit_analysis.py skill that calculates code review metrics from Gerrit data.

#### Scenario: Execute Gerrit analysis

- **WHEN** the agent needs to analyze code review data
- **THEN** it SHALL call bash to execute "python3 .claude/skills/gerrit_analysis.py"
- **AND** pass Gerrit changes data via stdin as JSON
- **AND** receive analysis results including metrics and anomalies

#### Scenario: Calculate review time metrics

- **WHEN** gerrit_analysis.py processes Gerrit changes
- **THEN** it SHALL calculate:
  - median_review_time_hours: 50th percentile review duration
  - p95_review_time_hours: 95th percentile review duration
  - avg_review_time_hours: mean review duration
- **AND** review time SHALL be measured from change creation to last update

#### Scenario: Calculate rework metrics

- **WHEN** analyzing Gerrit changes
- **THEN** the skill SHALL detect rework by counting changes with more than 2 patchsets
- **AND** calculate rework_rate_percent as (rework_count / total_changes) * 100
- **AND** report both the rate and absolute count

#### Scenario: Detect anomalies

- **WHEN** metrics are calculated
- **THEN** the skill SHALL detect anomalies when:
  - median_review_time_hours > 24 (warning severity)
  - p95_review_time_hours > 72 (critical severity)
  - rework_rate_percent > 15 (warning severity)
- **AND** return a list of anomalies with type, severity, message, value, and threshold

### Requirement: Report Generation Skill

The agent SHALL provide a report_generation.py skill that produces formatted Markdown reports.

#### Scenario: Generate efficiency report

- **WHEN** the agent needs to create a report
- **THEN** it SHALL call bash to execute "python3 .claude/skills/report_generation.py"
- **AND** pass metrics and anomalies data via stdin as JSON
- **AND** receive a Markdown-formatted report

#### Scenario: Report structure

- **WHEN** generating a report
- **THEN** the report SHALL include:
  - Title with date: "# 研发效能日报 - YYYY-MM-DD"
  - Key metrics table with all calculated values
  - Anomalies section (if any detected) with severity indicators
  - Impact analysis explaining business consequences
  - Improvement suggestions (3-5 actionable items)
  - Report timestamp and data source

#### Scenario: Report output format

- **WHEN** a report is generated
- **THEN** it SHALL be in GitHub-flavored Markdown format
- **AND** use emoji indicators: 🚨 for critical, ⚠️ for warnings, ✅ for normal status
- **AND** be suitable for saving to reports/ directory or displaying to users

### Requirement: Threshold-Based Monitoring

The agent SHALL use configured thresholds to identify efficiency anomalies.

#### Scenario: Review time thresholds

- **WHEN** evaluating review time metrics
- **THEN** the following thresholds SHALL apply:
  - Median review time: warning if > 24 hours
  - P95 review time: critical if > 72 hours
- **AND** anomalies SHALL trigger analysis and recommendations

#### Scenario: Rework rate threshold

- **WHEN** evaluating rework metrics
- **THEN** the threshold SHALL be 15%
- **AND** exceeding this SHALL trigger a warning anomaly
- **AND** the agent SHALL analyze potential causes (code quality, requirement clarity, review standards)

#### Scenario: Customizable thresholds

- **WHEN** thresholds are defined
- **THEN** they SHALL be documented in the agent's CLAUDE.md
- **AND** MAY be adjusted based on team standards and historical data

### Requirement: Data-Driven Analysis

The agent SHALL base all conclusions and recommendations on actual data, not assumptions.

#### Scenario: Require data before analysis

- **WHEN** a user asks about efficiency status
- **THEN** the agent SHALL first read or fetch relevant data
- **AND** only provide insights based on that data
- **AND** inform the user if data is unavailable

#### Scenario: Explain findings with data

- **WHEN** reporting an anomaly
- **THEN** the agent SHALL cite specific metric values
- **AND** compare against thresholds
- **AND** explain business impact (e.g., "may delay this week's iteration delivery")

#### Scenario: Actionable recommendations

- **WHEN** providing improvement suggestions
- **THEN** recommendations SHALL be specific and executable (e.g., "Set Review reminder to ensure response within 2 hours")
- **AND** avoid vague advice (e.g., "improve code quality" without specifics)

### Requirement: Conversational Interface

The agent SHALL engage users through natural language conversations, using tools to fulfill requests.

#### Scenario: Respond to analysis request

- **WHEN** user says "请分析昨天的代码审查数据"
- **THEN** the agent SHALL:
  1. Read data file using read_file tool
  2. Execute gerrit_analysis.py skill via bash
  3. Present results in conversational language
  4. Highlight any anomalies detected

#### Scenario: Respond to report request

- **WHEN** user says "生成本周的效率报告"
- **THEN** the agent SHALL:
  1. Analyze data using gerrit_analysis.py
  2. Generate report using report_generation.py
  3. Save report to reports/ directory using write_file
  4. Confirm completion and summarize key findings

#### Scenario: Respond to consultation

- **WHEN** user asks "为什么返工率这么高?"
- **THEN** the agent SHALL analyze current data
- **AND** provide possible root causes based on patterns
- **AND** suggest concrete improvement actions
- **AND** avoid making judgments about individuals

### Requirement: Output Formatting Standards

The agent SHALL follow consistent formatting for alerts and reports.

#### Scenario: Anomaly alert format

- **WHEN** notifying about an anomaly
- **THEN** the message SHALL include:
  - Alert emoji (🚨 or ⚠️)
  - Module/scope affected
  - Metric name
  - Current value vs. normal range
  - Business impact explanation
  - Link or suggestion for detailed analysis

#### Scenario: Concise communication

- **WHEN** responding to users
- **THEN** the agent SHALL use business language, not technical jargon
- **AND** keep responses concise and focused
- **AND** only provide details when requested or necessary
