# Redis Integration for Session Management (Optional)

This guide shows how to integrate Redis for persistent session history in agents.

## Installation

```bash
pip install redis aioredis
```

## Configuration

Add to your `.env`:

```env
# Redis Configuration (Optional)
REDIS_ENABLED=false
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_TTL=3600  # Session TTL in seconds (1 hour)
```

## Usage

### Basic Setup

```python
from app.services.redis_session import RedisSessionManager

# Initialize Redis session manager
session_manager = RedisSessionManager()

# Store conversation history
await session_manager.store_message(
    session_id="user-123",
    role="user",
    content="Hello!"
)

# Retrieve history
history = await session_manager.get_history("user-123")
```

### With Agents

```python
from langchain_openai import ChatOpenAI
from app.services.redis_session import RedisSessionManager

llm = ChatOpenAI(
    base_url="http://localhost:6969/v1",
    api_key="your-api-key",
    model="gemini-2.0-flash"
)

session_manager = RedisSessionManager()

# Get conversation history
history = await session_manager.get_history("agent-session-001")

# Add to messages
messages = history + [{"role": "user", "content": "New question"}]

# Get response
response = llm.invoke(messages)

# Store new message
await session_manager.store_message(
    session_id="agent-session-001",
    role="assistant",
    content=response.content
)
```

## Implementation

Create `src/app/services/redis_session.py`:

```python
import redis.asyncio as redis
from typing import List, Dict, Any, Optional
import json
import os
from app.logger import logger

class RedisSessionManager:
    """
    Redis-based session manager for persistent conversation history.
    Optional - only used if REDIS_ENABLED=true in .env
    """
    
    def __init__(self):
        self.enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
        
        if self.enabled:
            self.redis = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
                password=os.getenv("REDIS_PASSWORD", None),
                decode_responses=True
            )
            self.ttl = int(os.getenv("REDIS_TTL", 3600))
            logger.info("Redis session manager initialized")
        else:
            self.redis = None
            logger.info("Redis session manager disabled")
    
    async def store_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store a message in the session history."""
        if not self.enabled:
            return False
        
        try:
            key = f"session:{session_id}"
            message = {
                "role": role,
                "content": content,
                "metadata": metadata or {}
            }
            
            # Append to list
            await self.redis.rpush(key, json.dumps(message))
            
            # Set TTL
            await self.redis.expire(key, self.ttl)
            
            return True
        except Exception as e:
            logger.error(f"Error storing message in Redis: {e}")
            return False
    
    async def get_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve conversation history for a session."""
        if not self.enabled:
            return []
        
        try:
            key = f"session:{session_id}"
            
            # Get all messages
            if limit:
                messages = await self.redis.lrange(key, -limit, -1)
            else:
                messages = await self.redis.lrange(key, 0, -1)
            
            return [json.loads(msg) for msg in messages]
        except Exception as e:
            logger.error(f"Error retrieving history from Redis: {e}")
            return []
    
    async def clear_session(self, session_id: str) -> bool:
        """Clear a session's history."""
        if not self.enabled:
            return False
        
        try:
            key = f"session:{session_id}"
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error clearing session: {e}")
            return False
```

## Benefits

- ✅ **Unlimited History**: No memory limits
- ✅ **Persistent**: Survives server restarts
- ✅ **Scalable**: Works across multiple instances
- ✅ **Optional**: Falls back to in-memory if disabled
- ✅ **TTL Support**: Auto-cleanup of old sessions

## Docker Compose

Add Redis to your `docker-compose.yml`:

```yaml
version: '3.8'

services:
  webai-api:
    build: .
    ports:
      - "6969:6969"
    environment:
      - REDIS_ENABLED=true
      - REDIS_HOST=redis
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

## Testing

```python
import asyncio
from app.services.redis_session import RedisSessionManager

async def test_redis():
    manager = RedisSessionManager()
    
    # Store messages
    await manager.store_message("test-001", "user", "Hello!")
    await manager.store_message("test-001", "assistant", "Hi there!")
    
    # Retrieve history
    history = await manager.get_history("test-001")
    print(history)
    
    # Clear session
    await manager.clear_session("test-001")

asyncio.run(test_redis())
```

## Production Recommendations

1. **Use Redis Sentinel** for high availability
2. **Enable persistence** (RDB + AOF)
3. **Set appropriate TTL** based on your use case
4. **Monitor memory usage**
5. **Use connection pooling**

---

**Note**: Redis is **optional**. The system works perfectly without it using in-memory sessions.
