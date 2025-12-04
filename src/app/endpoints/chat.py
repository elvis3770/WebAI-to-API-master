# src/app/endpoints/chat.py
import time
import json
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.logger import logger
from schemas.request import GeminiRequest, OpenAIChatRequest
from app.services.gemini_client import get_gemini_client
from app.services.session_manager import get_translate_session_manager
from app.utils.tokens import count_tokens, count_messages_tokens
from app.config import STREAMING_ENABLED

router = APIRouter()


@router.post("/translate")
async def translate_chat(request: GeminiRequest):
    """
    Translation endpoint with session context.
    Compatible with Translate It! browser extension.
    """
    gemini_client = get_gemini_client()
    session_manager = get_translate_session_manager()
    if not gemini_client or not session_manager:
        raise HTTPException(status_code=503, detail="Gemini client is not initialized.")
    try:
        response = await session_manager.get_response(request.model, request.message, request.files)
        return {"response": response.text}
    except Exception as e:
        logger.error(f"Error in /translate endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error during translation: {str(e)}")


def convert_to_openai_format(
    response_text: str,
    model: str,
    prompt_text: str = "",
    stream: bool = False
):
    """
    Convert Gemini response to OpenAI format with real token counting.
    
    Args:
        response_text: Response from Gemini
        model: Model name
        prompt_text: Original prompt (for token counting)
        stream: Whether this is a streaming response
        
    Returns:
        OpenAI-formatted response dict
    """
    # Count tokens
    prompt_tokens = count_tokens(prompt_text, model) if prompt_text else 0
    completion_tokens = count_tokens(response_text, model)
    total_tokens = prompt_tokens + completion_tokens
    
    return {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion.chunk" if stream else "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        },
    }


async def stream_gemini_response(
    gemini_client,
    user_message: str,
    model: str
) -> AsyncGenerator[str, None]:
    """
    Stream Gemini response in OpenAI SSE format.
    
    Args:
        gemini_client: Gemini client instance
        user_message: User's message
        model: Model name
        
    Yields:
        SSE-formatted chunks
    """
    try:
        # Note: This is a placeholder for actual streaming implementation
        # The gemini-webapi library may not support streaming natively
        # This simulates streaming by yielding the full response
        
        response = await gemini_client.generate_content(
            message=user_message,
            model=model,
            files=None
        )
        
        # Simulate streaming by chunking the response
        chunk_size = 20  # Characters per chunk
        text = response.text
        
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            
            chunk_data = {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": chunk},
                        "finish_reason": None,
                    }
                ],
            }
            
            yield f"data: {json.dumps(chunk_data)}\n\n"
        
        # Send final chunk with finish_reason
        final_chunk = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop",
                }
            ],
        }
        
        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        logger.error(f"Error in streaming response: {e}", exc_info=True)
        error_data = {
            "error": {
                "message": str(e),
                "type": "server_error",
            }
        }
        yield f"data: {json.dumps(error_data)}\n\n"


@router.post("/v1/chat/completions")
async def chat_completions(request: OpenAIChatRequest):
    """
    OpenAI-compatible chat completions endpoint.
    Supports streaming and real token counting.
    """
    is_stream = request.stream if request.stream is not None else False
    gemini_client = get_gemini_client()
    
    if not gemini_client:
        raise HTTPException(status_code=503, detail="Gemini client is not initialized.")
    
    # Extract the user message from the list of messages
    user_message = next(
        (msg.get("content") for msg in request.messages if msg.get("role") == "user"),
        None
    )
    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found.")
    
    if not request.model:
        raise HTTPException(status_code=400, detail="Model not specified in the request.")
    
    model_value = request.model.value
    
    try:
        # Handle streaming if requested and enabled
        if is_stream and STREAMING_ENABLED:
            return StreamingResponse(
                stream_gemini_response(gemini_client, user_message, model_value),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",  # Disable nginx buffering
                }
            )
        
        # Non-streaming response
        response = await gemini_client.generate_content(
            message=user_message,
            model=model_value,
            files=None
        )
        
        # Convert to OpenAI format with real token counting
        return convert_to_openai_format(
            response.text,
            model_value,
            prompt_text=user_message,
            stream=False
        )
        
    except Exception as e:
        logger.error(f"Error in /v1/chat/completions endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat completion: {str(e)}"
        )
