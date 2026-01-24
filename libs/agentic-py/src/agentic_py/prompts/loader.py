"""
Prompt Loader

Loads prompt templates from markdown files and converts them to LangChain PromptTemplate instances.
"""

import logging
from functools import lru_cache
from pathlib import Path

from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

# Base directory for prompts (relative to this file)
_PROMPTS_BASE_DIR = Path(__file__).parent


def get_prompt_path(template_name: str) -> Path:
    """
    Resolve the path to a prompt template file.

    Supports loading from subdirectories:
    - `lesson_generation/lesson_generation_base.md` -> lesson_generation subdirectory
    - `violation_analysis/violation_analysis_base.md` -> violation_analysis subdirectory
    - `template_name.md` -> root prompts directory

    Args:
        template_name: Name of the template (with or without .md extension, with or without subdirectory)

    Returns:
        Path to the prompt template file

    Raises:
        FileNotFoundError: If the prompt file does not exist
    """
    # Remove .md extension if present
    if template_name.endswith(".md"):
        template_name = template_name[:-3]

    # Check if it includes a subdirectory path
    if "/" in template_name:
        # Path includes subdirectory (e.g., "lesson_generation/lesson_generation_base")
        prompt_path = _PROMPTS_BASE_DIR / f"{template_name}.md"
    else:
        # Try root directory first, then search subdirectories
        prompt_path = _PROMPTS_BASE_DIR / f"{template_name}.md"
        if not prompt_path.exists():
            # Search in subdirectories
            for subdir in ["lesson_generation", "violation_analysis", "agents"]:
                candidate = _PROMPTS_BASE_DIR / subdir / f"{template_name}.md"
                if candidate.exists():
                    prompt_path = candidate
                    break

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt template not found: {template_name}.md\nSearched in: {_PROMPTS_BASE_DIR}"
        )

    return prompt_path


def _parse_markdown_prompt(content: str) -> tuple[str | None, str]:
    """
    Parse markdown prompt content to extract system message and user message.

    Expected format:
    ```markdown
    # System Message (optional)
    [System message content]

    # User Message
    [User message with {variables}]
    ```

    Args:
        content: Raw markdown content

    Returns:
        Tuple of (system_message, user_message)
        system_message may be None if not present
    """
    lines = content.split("\n")
    system_message = None
    user_message = None
    current_section = None
    current_content: list[str] = []

    for line in lines:
        # Check for section headers
        if line.startswith("# System Message"):
            if current_section == "system" and current_content:
                system_message = "\n".join(current_content).strip()
            current_section = "system"
            current_content = []
        elif line.startswith("# User Message"):
            if current_section == "system" and current_content:
                system_message = "\n".join(current_content).strip()
            elif current_section == "user" and current_content:
                user_message = "\n".join(current_content).strip()
            current_section = "user"
            current_content = []
        elif line.startswith("#") and current_section:
            # Another section header after User Message - stop parsing
            if current_section == "user" and current_content:
                user_message = "\n".join(current_content).strip()
            elif current_section == "system" and current_content:
                system_message = "\n".join(current_content).strip()
            # Stop parsing after User Message section
            break
        elif current_section:
            current_content.append(line)
        elif not line.strip() and not current_content:
            # Skip leading empty lines
            continue
        else:
            # Content before any section header - treat as user message
            if not current_section:
                current_section = "user"
            current_content.append(line)

    # Save final section
    if current_section == "system" and current_content:
        system_message = "\n".join(current_content).strip()
    elif current_section == "user" and current_content:
        user_message = "\n".join(current_content).strip()

    # If no sections found, treat entire content as user message
    if user_message is None:
        user_message = content.strip()

    return system_message, user_message


@lru_cache(maxsize=32)
def load_prompt(template_name: str) -> PromptTemplate:
    """
    Load a prompt template from a markdown file and convert it to a LangChain PromptTemplate.

    The markdown file can contain:
    - Optional system message section (prefixed with "# System Message")
    - User message section (prefixed with "# User Message" or entire content)
    - Variables in {variable_name} format for LangChain PromptTemplate

    Args:
        template_name: Name of the template (e.g., "lesson_generation/lesson_generation_base" or "lesson_generation_base")

    Returns:
        LangChain PromptTemplate instance

    Raises:
        FileNotFoundError: If the prompt file does not exist
        ValueError: If the prompt content is invalid

    Example:
        ```python
        template = load_prompt("lesson_generation/lesson_generation_base")
        result = template.format(error_logs="TypeError", edit_frequency=15.0)
        ```
    """
    prompt_path = get_prompt_path(template_name)

    try:
        content = prompt_path.read_text(encoding="utf-8")
    except Exception as e:
        raise FileNotFoundError(f"Failed to read prompt file {prompt_path}: {e}") from e

    if not content.strip():
        raise ValueError(f"Prompt file {prompt_path} is empty")

    # Parse markdown to extract system and user messages
    system_message, user_message = _parse_markdown_prompt(content)

    # If system message exists, combine with user message
    # LangChain PromptTemplate doesn't natively support system messages,
    # so we'll include it in the template if present
    # In practice, the LLM framework will handle system messages separately
    # For now, we'll prepend it to the user message with a clear separator
    full_template = f"{system_message}\n\n{user_message}" if system_message else user_message

    try:
        # Create LangChain PromptTemplate
        # LangChain will validate the template and extract variables
        template = PromptTemplate.from_template(full_template)

        # Validate template variables
        try:
            # Try to validate template by checking for required variables
            # This will raise an error if template is malformed
            template_variables = template.input_variables
            logger.debug(
                f"Loaded prompt template: {template_name}",
                extra={
                    "template_name": template_name,
                    "variables": template_variables,
                    "has_system_message": system_message is not None,
                },
            )
        except Exception as validation_error:
            raise ValueError(
                f"Template validation failed for {template_name}: {validation_error}\n"
                f"Template content preview: {full_template[:200]}..."
            ) from validation_error

        return template
    except ValueError:
        # Re-raise ValueError as-is (already formatted)
        raise
    except Exception as e:
        raise ValueError(
            f"Failed to create PromptTemplate from {prompt_path}: {e}\n"
            f"Template content preview: {full_template[:200]}..."
        ) from e


def load_agent_system_prompt(template_name: str) -> str:
    """
    Load system prompt for an agent from a markdown file.

    The markdown file should contain a "# System Message" section.

    Args:
        template_name: Name of the template (e.g., "agents/struggle_agent_system")

    Returns:
        System prompt string

    Raises:
        FileNotFoundError: If the prompt file does not exist
        ValueError: If the prompt content is invalid or missing system message
    """
    prompt_path = get_prompt_path(template_name)

    try:
        content = prompt_path.read_text(encoding="utf-8")
    except Exception as e:
        raise FileNotFoundError(f"Failed to read prompt file {prompt_path}: {e}") from e

    if not content.strip():
        raise ValueError(f"Prompt file {prompt_path} is empty")

    # Parse markdown to extract system message
    system_message, _ = _parse_markdown_prompt(content)

    if system_message is None:
        raise ValueError(f"Prompt file {prompt_path} does not contain a '# System Message' section")

    return system_message


def load_agent_user_message_template(template_name: str) -> PromptTemplate:
    """
    Load user message template for an agent from a markdown file.

    The markdown file should contain a "# User Message" section with variables.

    Args:
        template_name: Name of the template (e.g., "agents/struggle_agent_user")

    Returns:
        LangChain PromptTemplate instance for the user message

    Raises:
        FileNotFoundError: If the prompt file does not exist
        ValueError: If the prompt content is invalid
    """
    prompt_path = get_prompt_path(template_name)

    try:
        content = prompt_path.read_text(encoding="utf-8")
    except Exception as e:
        raise FileNotFoundError(f"Failed to read prompt file {prompt_path}: {e}") from e

    if not content.strip():
        raise ValueError(f"Prompt file {prompt_path} is empty")

    # Parse markdown to extract user message
    _, user_message = _parse_markdown_prompt(content)

    if user_message is None:
        raise ValueError(f"Prompt file {prompt_path} does not contain a '# User Message' section")

    try:
        template = PromptTemplate.from_template(user_message)
        logger.debug(
            f"Loaded agent user message template: {template_name}",
            extra={
                "template_name": template_name,
                "variables": template.input_variables,
            },
        )
        return template
    except Exception as e:
        raise ValueError(
            f"Failed to create PromptTemplate from {prompt_path}: {e}\n"
            f"Template content preview: {user_message[:200]}..."
        ) from e
