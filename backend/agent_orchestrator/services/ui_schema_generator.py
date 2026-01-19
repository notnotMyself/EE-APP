"""
UI Schema Generator Service
Generates dynamic UI schemas from AI analysis results for adaptive rendering
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from anthropic import Anthropic

logger = logging.getLogger(__name__)

# Default LLM Gateway configuration
DEFAULT_BASE_URL = "https://llm-gateway.oppoer.me"
DEFAULT_MODEL = "saas/claude-haiku-4.5"  # Use haiku for cost efficiency


class UISchemaGenerator:
    """Generate UI schemas from analysis results using Claude"""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize UI Schema Generator

        Args:
            base_url: LLM Gateway base URL (default: from env or DEFAULT_BASE_URL)
            api_key: API key/token (default: from ANTHROPIC_AUTH_TOKEN env)
            model: Model to use (default: saas/claude-haiku-4.5)
        """
        self.anthropic_client = None
        self.model = model or os.getenv("UI_SCHEMA_MODEL", DEFAULT_MODEL)

        # Get configuration from parameters or environment
        effective_base_url = base_url or os.getenv("ANTHROPIC_BASE_URL", DEFAULT_BASE_URL)
        effective_api_key = api_key or os.getenv("ANTHROPIC_AUTH_TOKEN")

        if effective_api_key:
            self.anthropic_client = Anthropic(
                base_url=effective_base_url,
                api_key=effective_api_key,
            )
            logger.info(f"UISchemaGenerator initialized with base_url={effective_base_url}, model={self.model}")
        else:
            logger.warning("ANTHROPIC_AUTH_TOKEN not set, UI schema generation will be disabled")

    def generate_from_analysis(
        self,
        analysis_result: str,
        data_context: Dict[str, Any],
        agent_role: str
    ) -> Optional[Dict[str, Any]]:
        """
        Generate UI Schema from analysis result

        Args:
            analysis_result: Text analysis result from agent
            data_context: Additional context data
            agent_role: Role of the agent generating the briefing

        Returns:
            UI Schema dict or None if generation fails
        """
        if not self.anthropic_client:
            logger.warning("Anthropic client not initialized, skipping UI schema generation")
            return None

        try:
            # Build prompt for UI schema generation
            prompt = self._build_schema_prompt(analysis_result, data_context, agent_role)

            # Call Claude API via LLM Gateway
            response = self.anthropic_client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract and parse JSON response
            response_text = response.content[0].text if response.content else ""
            schema = self._extract_json(response_text)

            if not schema:
                logger.warning("Failed to extract JSON from Claude response")
                return None

            # Validate schema
            if not self._validate_schema(schema):
                logger.warning("Generated schema failed validation")
                return None

            logger.info(f"Successfully generated UI schema for agent {agent_role}")
            return schema

        except Exception as e:
            logger.error(f"Error generating UI schema: {e}")
            return None

    def _build_schema_prompt(
        self,
        analysis_result: str,
        data_context: Dict[str, Any],
        agent_role: str
    ) -> str:
        """Build prompt for UI schema generation"""
        return f"""Generate a structured UI schema for displaying the following analysis result in a mobile app.

Agent Role: {agent_role}
Analysis Result:
{analysis_result}

Data Context: {json.dumps(data_context, indent=2)}

Available Component Types:
1. **metric_cards**: Display key metrics with trend indicators
   - Each card has: label, value, trend (up/down/flat), change (e.g., "+5%")

2. **line_chart** / **bar_chart**: Visualize trends over time
   - Requires: title, xAxis (array of labels), series (array of data series)
   - Each series has: name, data (array of numbers)

3. **table**: Display tabular data
   - Requires: headers (array), rows (2D array)

4. **timeline**: Show chronological events
   - Each item has: timestamp, title, description, status (optional)

5. **alert_list**: Display warnings or important notices
   - Each item has: severity (high/medium/low), message

6. **markdown**: Fallback for text content
   - content: Markdown formatted text

Generate a JSON response with the following structure:
{{
  "type": "briefing",
  "version": "1.0",
  "content": {{
    "sections": [
      {{
        "type": "<component_type>",
        "title": "Optional section title",
        ...component-specific properties...
      }}
    ]
  }}
}}

Rules:
- Choose components that best visualize the data
- Use metric_cards for KPIs and statistics
- Use charts for trends and comparisons
- Use timeline for sequential events
- Use alert_list for critical issues
- Keep it simple - maximum 3-4 sections
- Ensure all data is properly formatted
- ONLY output valid JSON, no explanations

Generate the UI schema now:"""

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from Claude response"""
        try:
            # Try to parse directly
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON block
            start_idx = text.find('{')
            end_idx = text.rfind('}')

            if start_idx != -1 and end_idx != -1:
                json_str = text[start_idx:end_idx + 1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass

            return None

    def _validate_schema(self, schema: Dict[str, Any]) -> bool:
        """
        Validate UI schema structure

        Args:
            schema: UI schema dict

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required top-level fields
            if not isinstance(schema, dict):
                return False

            if schema.get('type') != 'briefing':
                return False

            if 'content' not in schema:
                return False

            content = schema['content']
            if not isinstance(content, dict):
                return False

            # Check sections
            sections = content.get('sections', [])
            if not isinstance(sections, list):
                return False

            # Validate each section
            valid_types = {
                'metric_cards', 'line_chart', 'bar_chart',
                'table', 'timeline', 'alert_list', 'markdown',
                'alert', 'insight', 'summary', 'action_list'  # Additional types
            }

            for section in sections:
                if not isinstance(section, dict):
                    return False

                section_type = section.get('type')
                if section_type not in valid_types:
                    logger.warning(f"Invalid section type: {section_type}")
                    return False

                # Type-specific validation
                if section_type == 'metric_cards':
                    if not self._validate_metric_cards(section):
                        return False
                elif section_type in ['line_chart', 'bar_chart']:
                    if not self._validate_chart(section):
                        return False
                elif section_type == 'table':
                    if not self._validate_table(section):
                        return False
                elif section_type == 'timeline':
                    if not self._validate_timeline(section):
                        return False
                elif section_type == 'alert_list':
                    if not self._validate_alert_list(section):
                        return False
                elif section_type == 'markdown':
                    if 'content' not in section:
                        return False

            return True

        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            return False

    def _validate_metric_cards(self, section: Dict) -> bool:
        """Validate metric_cards section"""
        # Accept both 'data' and 'cards' keys (LLM may use either)
        data = section.get('data') or section.get('cards', [])
        if not isinstance(data, list) or len(data) == 0:
            return False

        for card in data:
            if not all(k in card for k in ['label', 'value']):
                return False

        return True

    def _validate_chart(self, section: Dict) -> bool:
        """Validate chart section"""
        if 'xAxis' not in section or 'series' not in section:
            return False

        if not isinstance(section['xAxis'], list):
            return False

        if not isinstance(section['series'], list):
            return False

        for series in section['series']:
            if not all(k in series for k in ['name', 'data']):
                return False
            if not isinstance(series['data'], list):
                return False

        return True

    def _validate_table(self, section: Dict) -> bool:
        """Validate table section"""
        if 'headers' not in section or 'rows' not in section:
            return False

        if not isinstance(section['headers'], list):
            return False

        if not isinstance(section['rows'], list):
            return False

        return True

    def _validate_timeline(self, section: Dict) -> bool:
        """Validate timeline section"""
        items = section.get('items', [])
        if not isinstance(items, list) or len(items) == 0:
            return False

        for item in items:
            if not all(k in item for k in ['timestamp', 'title']):
                return False

        return True

    def _validate_alert_list(self, section: Dict) -> bool:
        """Validate alert_list section"""
        items = section.get('items', [])
        if not isinstance(items, list) or len(items) == 0:
            return False

        for item in items:
            if not all(k in item for k in ['severity', 'message']):
                return False
            if item['severity'] not in ['high', 'medium', 'low']:
                return False

        return True

    def create_fallback_markdown_schema(self, content: str) -> Dict[str, Any]:
        """
        Create a simple markdown fallback schema

        Args:
            content: Markdown content

        Returns:
            Markdown UI schema
        """
        return {
            "type": "briefing",
            "version": "1.0",
            "content": {
                "sections": [
                    {
                        "type": "markdown",
                        "content": content
                    }
                ]
            }
        }
