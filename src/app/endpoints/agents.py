# src/app/endpoints/agents.py
"""
Agent-specific endpoints for multi-step tasks and chaining.

This module provides endpoints optimized for AI agent frameworks like
LangChain, CrewAI, and AutoGen, with support for multi-turn conversations,
task chaining, and intelligent model routing.
"""
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.services.gemini_client import get_gemini_client
from app.services.session_manager import get_translate_session_manager
from app.utils.tokens import count_messages_tokens, estimate_cost

logger = logging.getLogger(__name__)

router = APIRouter()


class AgentTask(BaseModel):
    """Single task in an agent chain."""
    task_id: str = Field(..., description="Unique identifier for this task")
    task_type: str = Field(..., description="Type of task: translate, summarize, research, etc.")
    input: str = Field(..., description="Input text for this task")
    model: Optional[str] = Field("gemini-2.0-flash", description="Model to use for this task")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class AgentChainRequest(BaseModel):
    """Request for chaining multiple agent tasks."""
    chain_id: str = Field(..., description="Unique identifier for this chain")
    tasks: List[AgentTask] = Field(..., description="List of tasks to execute in sequence")
    pass_output: bool = Field(True, description="Pass output of each task as input to next")
    model_routing: Optional[Dict[str, str]] = Field(
        default=None,
        description="Map task types to specific models (e.g., {'creative': 'gpt-4', 'factual': 'gemini-2.0-flash'})"
    )


class AgentChainResponse(BaseModel):
    """Response from agent chain execution."""
    chain_id: str
    results: List[Dict[str, Any]]
    total_tokens: int
    estimated_cost: Dict[str, float]
    execution_time_ms: float


@router.post("/v1/agents/chain", response_model=AgentChainResponse)
async def execute_agent_chain(request: AgentChainRequest):
    """
    Execute a chain of agent tasks sequentially.
    
    This endpoint is optimized for AI agent frameworks that need to:
    - Chain multiple LLM calls together
    - Pass outputs between tasks
    - Use different models for different task types
    - Track token usage and costs
    
    Example:
    ```python
    # LangChain integration
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(
        base_url="http://localhost:6969/v1",
        api_key="your-api-key",
        model="gemini-2.0-flash"
    )
    
    # Or use the chain endpoint directly
    response = requests.post(
        "http://localhost:6969/v1/agents/chain",
        json={
            "chain_id": "research-task-001",
            "tasks": [
                {"task_id": "1", "task_type": "research", "input": "What are AI agents?"},
                {"task_id": "2", "task_type": "summarize", "input": ""}
            ],
            "pass_output": True
        }
    )
    ```
    """
    import time
    start_time = time.time()
    
    gemini_client = get_gemini_client()
    if not gemini_client:
        raise HTTPException(status_code=503, detail="Gemini client is not initialized.")
    
    results = []
    total_tokens = 0
    previous_output = None
    
    for task in request.tasks:
        try:
            # Determine model to use (routing logic)
            model = task.model
            if request.model_routing and task.task_type in request.model_routing:
                model = request.model_routing[task.task_type]
            
            # Prepare input (use previous output if chaining)
            task_input = task.input
            if request.pass_output and previous_output:
                task_input = f"{task.input}\n\nContext from previous task:\n{previous_output}"
            
            # Execute task
            logger.info(f"Executing task {task.task_id} ({task.task_type}) with model {model}")
            
            response = await gemini_client.generate_content(
                message=task_input,
                model=model,
                files=None
            )
            
            # Count tokens
            task_tokens = count_messages_tokens(
                [{"role": "user", "content": task_input}],
                model
            )
            total_tokens += task_tokens
            
            # Store result
            result = {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "model": model,
                "output": response.text,
                "tokens": task_tokens,
                "success": True
            }
            results.append(result)
            
            # Save output for next task
            previous_output = response.text
            
        except Exception as e:
            logger.error(f"Error executing task {task.task_id}: {e}", exc_info=True)
            results.append({
                "task_id": task.task_id,
                "task_type": task.task_type,
                "model": task.model,
                "output": None,
                "error": str(e),
                "success": False
            })
            # Stop chain on error
            break
    
    # Calculate execution time
    execution_time = (time.time() - start_time) * 1000
    
    # Estimate costs
    cost_estimate = estimate_cost(
        prompt_tokens=total_tokens,
        completion_tokens=total_tokens // 2,  # Rough estimate
        model=request.tasks[0].model if request.tasks else "gemini-2.0-flash"
    )
    
    return AgentChainResponse(
        chain_id=request.chain_id,
        results=results,
        total_tokens=total_tokens,
        estimated_cost=cost_estimate,
        execution_time_ms=execution_time
    )


@router.post("/v1/agents/task")
async def execute_single_task(task: AgentTask):
    """
    Execute a single agent task.
    
    Simpler endpoint for single-step agent operations.
    """
    gemini_client = get_gemini_client()
    if not gemini_client:
        raise HTTPException(status_code=503, detail="Gemini client is not initialized.")
    
    try:
        response = await gemini_client.generate_content(
            message=task.input,
            model=task.model,
            files=None
        )
        
        tokens = count_messages_tokens(
            [{"role": "user", "content": task.input}],
            task.model
        )
        
        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "output": response.text,
            "tokens": tokens,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error executing task {task.task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")


@router.get("/v1/agents/models")
async def get_agent_models():
    """
    Get recommended models for different agent task types.
    
    Returns a mapping of task types to recommended models.
    """
    return {
        "task_routing": {
            "creative": "gemini-2.5-pro",
            "factual": "gemini-2.0-flash",
            "reasoning": "gemini-2.5-pro",
            "translation": "gemini-2.0-flash",
            "summarization": "gemini-2.0-flash",
            "research": "gemini-2.5-pro",
            "code": "gemini-2.0-flash",
            "vision": "gemini-2.5-pro"
        },
        "available_models": [
            "gemini-2.0-flash",
            "gemini-2.5-pro",
            "gemini-1.5-flash",
            "gpt-4",
            "claude-3",
            "grok-beta"
        ],
        "recommendations": {
            "speed": "gemini-2.0-flash",
            "quality": "gemini-2.5-pro",
            "cost": "gemini-2.0-flash",
            "reasoning": "gemini-2.5-pro"
        }
    }
