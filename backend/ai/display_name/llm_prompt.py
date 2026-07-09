def build_display_name_prompt(
    display_name: str,
    context: str = None,
) -> str:
    """
    Build a prompt for an LLM to evaluate whether a display name
    belongs to a real person (candidate) or is a generic/device name.

    Args:
        display_name: The name to evaluate.
        context: Optional extra context (e.g., meeting platform).

    Returns:
        Prompt string ready to send to an LLM API.
    """
    context_line = f"\nContext: {context}" if context else ""

    return (
        f"You are an AI assistant for an interview candidate identifier system.\n"
        f"Evaluate the following display name from a video meeting participant:\n\n"
        f"Display name: \"{display_name}\"{context_line}\n\n"
        f"Answer ONLY with a JSON object in this format:\n"
        f"{{\n"
        f"  \"is_person_name\": true/false,\n"
        f"  \"confidence\": 0.0 to 1.0,\n"
        f"  \"reason\": \"short explanation\"\n"
        f"}}"
    )
