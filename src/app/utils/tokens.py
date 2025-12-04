# src/app/utils/tokens.py
"""
Token counting utilities for WebAI-to-API.

Provides functions to count tokens and estimate costs for different models.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import tiktoken for accurate token counting
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logger.warning("tiktoken not available. Token counting will use approximations.")


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Count tokens in text for a given model.
    
    Args:
        text: Text to count tokens for
        model: Model name (used to select appropriate encoding)
        
    Returns:
        Number of tokens
    """
    if not text:
        return 0
    
    if TIKTOKEN_AVAILABLE:
        try:
            # Map Gemini models to equivalent OpenAI encodings
            encoding_map = {
                "gemini-1.5-flash": "cl100k_base",
                "gemini-2.0-flash": "cl100k_base",
                "gemini-2.5-pro": "cl100k_base",
                "gemini-3.0-pro": "cl100k_base",
            }
            
            # Get encoding name
            if model in encoding_map:
                encoding_name = encoding_map[model]
            else:
                # Try to get encoding for model directly
                try:
                    encoding = tiktoken.encoding_for_model(model)
                    return len(encoding.encode(text))
                except KeyError:
                    # Fall back to cl100k_base (GPT-4 encoding)
                    encoding_name = "cl100k_base"
            
            encoding = tiktoken.get_encoding(encoding_name)
            return len(encoding.encode(text))
            
        except Exception as e:
            logger.warning(f"Error counting tokens with tiktoken: {e}. Using approximation.")
            return _approximate_token_count(text)
    else:
        return _approximate_token_count(text)


def _approximate_token_count(text: str) -> int:
    """
    Approximate token count using simple heuristic.
    Roughly 1 token per 4 characters for English text.
    
    Args:
        text: Text to count tokens for
        
    Returns:
        Approximate number of tokens
    """
    # Simple approximation: ~4 characters per token
    return len(text) // 4


def count_messages_tokens(messages: list, model: str = "gpt-3.5-turbo") -> int:
    """
    Count tokens in a list of messages (OpenAI format).
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model name
        
    Returns:
        Total number of tokens
    """
    total_tokens = 0
    
    for message in messages:
        # Count tokens in content
        content = message.get("content", "")
        total_tokens += count_tokens(content, model)
        
        # Add overhead for message formatting (role, etc.)
        # OpenAI uses ~4 tokens per message for formatting
        total_tokens += 4
    
    # Add overhead for conversation formatting
    total_tokens += 2
    
    return total_tokens


def truncate_to_limit(text: str, max_tokens: int, model: str = "gpt-3.5-turbo") -> str:
    """
    Truncate text to fit within token limit.
    
    Args:
        text: Text to truncate
        max_tokens: Maximum number of tokens
        model: Model name
        
    Returns:
        Truncated text
    """
    current_tokens = count_tokens(text, model)
    
    if current_tokens <= max_tokens:
        return text
    
    # Estimate characters to keep
    chars_per_token = len(text) / current_tokens
    target_chars = int(max_tokens * chars_per_token * 0.95)  # 95% to be safe
    
    truncated = text[:target_chars]
    
    # Verify and adjust if needed
    while count_tokens(truncated, model) > max_tokens:
        truncated = truncated[:int(len(truncated) * 0.9)]
    
    return truncated


def estimate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    model: str = "gemini-2.0-flash"
) -> dict:
    """
    Estimate cost for API usage.
    
    Note: This is for informational purposes only.
    Actual costs may vary based on your API pricing.
    
    Args:
        prompt_tokens: Number of input tokens
        completion_tokens: Number of output tokens
        model: Model name
        
    Returns:
        Dict with cost information
    """
    # Approximate pricing (per 1M tokens) - UPDATE THESE WITH ACTUAL PRICING
    pricing = {
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
        "gemini-2.0-flash": {"input": 0.075, "output": 0.30},
        "gemini-2.5-pro": {"input": 1.25, "output": 5.00},
        "gemini-3.0-pro": {"input": 1.25, "output": 5.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "gpt-4": {"input": 30.00, "output": 60.00},
    }
    
    # Get pricing for model or use default
    model_pricing = pricing.get(model, {"input": 0.10, "output": 0.30})
    
    # Calculate costs (per million tokens)
    input_cost = (prompt_tokens / 1_000_000) * model_pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * model_pricing["output"]
    total_cost = input_cost + output_cost
    
    return {
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(total_cost, 6),
        "model": model,
        "note": "Estimated costs - actual pricing may vary"
    }
