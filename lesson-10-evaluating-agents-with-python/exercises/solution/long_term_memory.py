# lesson-9-maintaining-long-term-agent-memory-in-python/exercises/solution/long_term_memory.py
"""
Long-Term Agent Memory Management with Python, OpenAI, and Cosmos DB
"""

import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import uuid
from dataclasses import dataclass, asdict, fields as dataclass_fields
from azure.cosmos import CosmosClient, PartitionKey
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding, AzureChatCompletion
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Reduce verbosity
for noisy in [
    "azure.core.pipeline.policies.http_logging_policy",
    "azure.cosmos",
    "azure.identity",
    "urllib3",
    "httpx",
    "semantic_kernel.connectors.ai.open_ai.services.open_ai_handler",
    "asyncio",
]:
    logging.getLogger(noisy).setLevel(logging.WARNING)


@dataclass
class MemoryItem:
    id: str
    session_id: str
    content: str
    memory_type: str
    importance_score: float
    access_count: int
    last_accessed: datetime
    created_at: datetime
    tags: List[str]
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

    # Optimization fields
    priority_score: float = 0.0
    relevance_score: float = 0.0
    memory_size: int = 0
    access_frequency: float = 0.0
    decay_factor: float = 1.0
    is_archived: bool = False
    retention_priority: int = 0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["last_accessed"] = self.last_accessed.isoformat()
        data["created_at"] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryItem":
        """Create from Cosmos DB dict, ignoring system props."""
        allowed = {f.name for f in dataclass_fields(cls)}
        clean = {k: v for k, v in data.items() if k in allowed}
        clean.setdefault("tags", [])
        clean.setdefault("metadata", {})

        # Parse datetimes
        for key in ("last_accessed", "created_at"):
            val = clean.get(key)
            if isinstance(val, str):
                try:
                    clean[key] = datetime.fromisoformat(val)
                except Exception:
                    clean[key] = datetime.utcnow()
            elif not isinstance(val, datetime):
                clean[key] = datetime.utcnow()
        return cls(**clean)


class LongTermMemory:
    def __init__(
        self,
        database_name: str = "agent_memory",
        container_name: str = "memories",
        max_memories: int = 1000,
        importance_threshold: float = 0.3,
        enable_ai_scoring: bool = True,
    ):
        self.database_name = database_name
        self.container_name = container_name
        self.max_memories = max_memories
        self.importance_threshold = importance_threshold
        self.enable_ai_scoring = enable_ai_scoring

        self._client = None
        self._database = None
        self._container = None

        self._kernel = None
        self._embedding_service = None
        self._chat_service = None

        # Which pruning strategies are available from prune_memories()
        self.pruning_strategies = {
            "importance": self._prune_by_importance,
            "age": self._prune_by_age,
            "access_frequency": self._prune_by_access_frequency,
            "hybrid": self._prune_hybrid,
            # Note: AI pruning is async; expose it via optimize_memory_performance()
            # If you want it to appear as "available" without calling it here, see _noop_ai_pruning below.
            # "ai_optimized": self._noop_ai_pruning,
        }

        # Used by optimize_memory_performance()
        self.performance_config = {
            "enable_auto_pruning": True,
            "enable_auto_reordering": True,
            "pruning_frequency_hours": 24,
            "reordering_frequency_hours": 12,
            "max_memory_size_mb": 100,
            "decay_rate_per_day": 0.01,
        }


    # ---------------- Cosmos + OpenAI setup ----------------

    def _get_cosmos_client(self) -> CosmosClient:
        if self._client is None:
            cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
            cosmos_key = os.getenv("COSMOS_KEY")
            if not cosmos_endpoint or not cosmos_key:
                raise ValueError("COSMOS_ENDPOINT and COSMOS_KEY are required")
            self._client = CosmosClient(cosmos_endpoint, cosmos_key)
            self._database = self._client.create_database_if_not_exists(id=self.database_name)
            self._container = self._database.create_container_if_not_exists(
                id=self.container_name,
                partition_key=PartitionKey(path="/session_id"),
            )
            logger.info(f"✅ Connected to Cosmos DB: {self.database_name}/{self.container_name}")
        return self._client

    def _get_openai_kernel(self) -> Kernel:
        if self._kernel is None and self.enable_ai_scoring:
            try:
                endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
                api_version = os.getenv("AZURE_OPENAI_API_VERSION")
                key = os.getenv("AZURE_OPENAI_KEY")
                chat_deploy = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
                embed_deploy = os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT")
                if not all([endpoint, api_version, key, chat_deploy, embed_deploy]):
                    self.enable_ai_scoring = False
                    return None
                self._kernel = Kernel()
                self._chat_service = AzureChatCompletion(
                    deployment_name=chat_deploy,
                    endpoint=endpoint,
                    api_key=key,
                    api_version=api_version,
                )
                self._embedding_service = AzureTextEmbedding(
                    deployment_name=embed_deploy,
                    endpoint=endpoint,
                    api_key=key,
                    api_version=api_version,
                )
                self._kernel.add_service(self._chat_service)
                self._kernel.add_service(self._embedding_service)
            except Exception as e:
                logger.error(f"❌ Failed to init OpenAI kernel: {e}")
                self.enable_ai_scoring = False
        return self._kernel

    # ---------------- Core operations ----------------

    async def add_memory(self, session_id: str, content: str, memory_type="conversation",
                         importance_score=0.5, tags=None, metadata=None, embedding=None, context=None) -> str:
        self._get_cosmos_client()
        container = self._container
        memory_id = str(uuid.uuid4())
        now = datetime.utcnow()
        item = MemoryItem(
            id=memory_id,
            session_id=session_id,
            content=content,
            memory_type=memory_type,
            importance_score=importance_score,
            access_count=0,
            last_accessed=now,
            created_at=now,
            tags=tags or [],
            metadata=metadata or {},
            embedding=embedding,
        )
        container.create_item(item.to_dict())
        logger.info(f"✅ Added memory: {memory_id} (importance {importance_score})")
        self._check_and_prune_if_needed()
        return memory_id

    def get_memory(self, memory_id: str, session_id: str) -> Optional[MemoryItem]:
        """Retrieve a memory by id + partition key, incrementing access stats."""
        try:
            self._get_cosmos_client()
            container = self._container
            item = container.read_item(item=memory_id, partition_key=session_id)
            mem = MemoryItem.from_dict(item)
            mem.access_count += 1
            mem.last_accessed = datetime.utcnow()
            container.upsert_item(mem.to_dict())
            return mem
        except Exception as e:
            logger.error(f"❌ Failed to get memory {memory_id}: {e}")
            return None

    def search_memories(self, session_id: str, query: str = None,
                        memory_type: str = None, tags: List[str] = None,
                        min_importance: float = 0.0, limit: int = 10) -> List[MemoryItem]:
        self._get_cosmos_client()
        container = self._container
        q = ["SELECT * FROM c WHERE c.session_id = @session_id"]
        params = [{"name": "@session_id", "value": session_id}]
        if query:
            q.append("AND CONTAINS(LOWER(c.content), @q)")
            params.append({"name": "@q", "value": query.lower()})
        if memory_type:
            q.append("AND c.memory_type = @mt")
            params.append({"name": "@mt", "value": memory_type})
        if min_importance > 0:
            q.append("AND c.importance_score >= @imp")
            params.append({"name": "@imp", "value": min_importance})
        if tags:
            for i, t in enumerate(tags):
                q.append(f"AND ARRAY_CONTAINS(c.tags, @tag{i})")
                params.append({"name": f"@tag{i}", "value": t})
        sql = " ".join(q)
        items = list(container.query_items(
            query=sql,
            parameters=params,
            enable_cross_partition_query=False,
            partition_key=session_id,
        ))
        mems = [MemoryItem.from_dict(i) for i in items]
        mems.sort(key=lambda m: (m.importance_score, m.last_accessed), reverse=True)
        return mems[:limit]

    def update_memory_importance(self, memory_id: str, session_id: str, new_importance: float) -> bool:
        mem = self.get_memory(memory_id, session_id)
        if not mem:
            return False
        mem.importance_score = max(0.0, min(1.0, new_importance))
        self._container.upsert_item(mem.to_dict())
        logger.info(f"Updated memory {memory_id} importance to {new_importance}")
        return True

    def _check_and_prune_if_needed(self):
        try:
            self._get_cosmos_client()
            container = self._container
            count = list(container.query_items(
                query="SELECT VALUE COUNT(1) FROM c",
                enable_cross_partition_query=True
            ))[0]
            if count > self.max_memories:
                self.prune_memories("hybrid")
        except Exception as e:
            logger.error(f"❌ Failed to check memory count: {e}")
    
    def prune_memories(self, strategy: str = 'hybrid') -> int:
        """
        Prune memories using the specified strategy.
        
        Args:
            strategy: Pruning strategy ('importance', 'age', 'access_frequency', 'hybrid')
            
        Returns:
            Number of memories pruned
        """
        try:
            if strategy not in self.pruning_strategies:
                raise ValueError(f"Unknown pruning strategy: {strategy}")
            
            logger.info(f"Starting memory pruning with strategy: {strategy}")
            
            # Get pruning function
            prune_func = self.pruning_strategies[strategy]
            
            # Perform pruning
            pruned_count = prune_func()
            
            logger.info(f"✅ Pruned {pruned_count} memories using {strategy} strategy")
            return pruned_count
            
        except ValueError as e:
            logger.error(f"❌ Invalid pruning strategy: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to prune memories: {e}")
            return 0
    
    def _prune_by_importance(self) -> int:
        """Prune memories with low importance scores"""
        try:
            self._get_cosmos_client()

            container = self._container
            
            # Find memories with low importance
            query = """
            SELECT c.id, c.session_id 
            FROM c 
            WHERE c.importance_score < @threshold
            """
            
            parameters = [{"name": "@threshold", "value": self.importance_threshold}]
            
            items_to_delete = list(container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            # Delete low-importance memories
            pruned_count = 0
            for item in items_to_delete:
                try:
                    container.delete_item(item=item['id'], partition_key=item['session_id'])
                    pruned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete memory {item['id']}: {e}")
            
            return pruned_count
            
        except Exception as e:
            logger.error(f"❌ Failed to prune by importance: {e}")
            return 0
    
    def _prune_by_age(self) -> int:
        """Prune old memories"""
        try:
            self._get_cosmos_client()

            container = self._container
            
            # Find memories older than 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            
            query = """
            SELECT c.id, c.session_id 
            FROM c 
            WHERE c.created_at < @cutoff_date
            """
            
            parameters = [{"name": "@cutoff_date", "value": cutoff_date.isoformat()}]
            
            items_to_delete = list(container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            # Delete old memories
            pruned_count = 0
            for item in items_to_delete:
                try:
                    container.delete_item(item=item['id'], partition_key=item['session_id'])
                    pruned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete memory {item['id']}: {e}")
            
            return pruned_count
            
        except Exception as e:
            logger.error(f"❌ Failed to prune by age: {e}")
            return 0
    
    def _prune_by_access_frequency(self) -> int:
        """Prune memories with low access frequency"""
        try:
            self._get_cosmos_client()

            container = self._container
            
            # Find memories with low access count
            query = """
            SELECT c.id, c.session_id 
            FROM c 
            WHERE c.access_count < 2
            """
            
            items_to_delete = list(container.query_items(
                query=query,
                parameters=[],
                enable_cross_partition_query=True
            ))
            
            # Delete low-access memories
            pruned_count = 0
            for item in items_to_delete:
                try:
                    container.delete_item(item=item['id'], partition_key=item['session_id'])
                    pruned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete memory {item['id']}: {e}")
            
            return pruned_count
            
        except Exception as e:
            logger.error(f"❌ Failed to prune by access frequency: {e}")
            return 0
    
    def _prune_hybrid(self) -> int:
        """Hybrid pruning strategy combining multiple approaches"""
        try:
            self._get_cosmos_client()

            container = self._container
            
            # Get all memories with scores
            query = """
            SELECT c.id, c.session_id, c.importance_score, c.access_count, c.created_at
            FROM c
            """
            
            all_memories = list(container.query_items(
                query=query,
                parameters=[],
                enable_cross_partition_query=True
            ))
            
            # Calculate hybrid scores
            now = datetime.now()
            memories_with_scores = []
            
            for memory in all_memories:
                # Age factor (older = lower score)
                age_days = (now - datetime.fromisoformat(memory['created_at'])).days
                age_factor = max(0, 1 - (age_days / 365))  # Decay over a year
                
                # Access factor
                access_factor = min(1, memory['access_count'] / 10)  # Normalize to 0-1
                
                # Hybrid score
                hybrid_score = (
                    memory['importance_score'] * 0.5 +
                    age_factor * 0.3 +
                    access_factor * 0.2
                )
                
                memories_with_scores.append((memory, hybrid_score))
            
            # Sort by hybrid score and delete lowest scoring memories
            memories_with_scores.sort(key=lambda x: x[1])
            
            # Delete enough memories to get under the limit
            target_count = self.max_memories
            current_count = len(all_memories)
            to_delete = max(0, current_count - target_count)
            
            pruned_count = 0
            for memory, score in memories_with_scores[:to_delete]:
                try:
                    container.delete_item(item=memory['id'], partition_key=memory['session_id'])
                    pruned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete memory {memory['id']}: {e}")
            
            return pruned_count
            
        except Exception as e:
            logger.error(f"❌ Failed to prune hybrid: {e}")
            return 0
    
    def reorder_memories(self, session_id: str, strategy: str = 'importance') -> int:
        """
        Reorder memories for better performance.
        
        Args:
            session_id: Session ID
            strategy: Reordering strategy ('importance', 'recency', 'access_frequency')
            
        Returns:
            Number of memories reordered
        """
        try:
            self._get_cosmos_client()

            container = self._container
            
            # Get all memories for the session
            memories = self.search_memories(session_id, limit=1000)
            
            if not memories:
                return 0
            
            # Apply reordering strategy
            if strategy == 'importance':
                memories.sort(key=lambda x: x.importance_score, reverse=True)
            elif strategy == 'recency':
                memories.sort(key=lambda x: x.last_accessed, reverse=True)
            elif strategy == 'access_frequency':
                memories.sort(key=lambda x: x.access_count, reverse=True)
            else:
                raise ValueError(f"Unknown reordering strategy: {strategy}")
            
            # Update memories with new order (using a priority field)
            reordered_count = 0
            for i, memory in enumerate(memories):
                memory.metadata['priority'] = i
                container.upsert_item(memory.to_dict())
                reordered_count += 1
            
            logger.info(f"✅ Reordered {reordered_count} memories using {strategy} strategy")
            return reordered_count
            
        except ValueError as e:
            logger.error(f"❌ Invalid reordering strategy: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to reorder memories: {e}")
            return 0
    
    def get_memory_statistics(self, session_id: str = None) -> Dict[str, Any]:
        """
        Get memory statistics for analysis.
        
        Args:
            session_id: Optional session ID to filter by
            
        Returns:
            Dictionary with memory statistics
        """
        try:
            self._get_cosmos_client()

            container = self._container
            
            # Build query
            if session_id:
                query = "SELECT * FROM c WHERE c.session_id = @session_id"
                parameters = [{"name": "@session_id", "value": session_id}]
                enable_cross_partition = False
            else:
                query = "SELECT * FROM c"
                parameters = []
                enable_cross_partition = True
            
            # Get all memories
            memories = list(container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=enable_cross_partition
            ))
            
            if not memories:
                return {
                    'total_memories': 0,
                    'memory_types': {},
                    'average_importance': 0.0,
                    'average_access_count': 0.0,
                    'oldest_memory': None,
                    'newest_memory': None
                }
            
            # Calculate statistics
            memory_types = {}
            importance_scores = []
            access_counts = []
            created_dates = []
            
            for memory in memories:
                mem_type = memory.get('memory_type', 'unknown')
                memory_types[mem_type] = memory_types.get(mem_type, 0) + 1

                importance_scores.append(float(memory.get('importance_score', 0.0)))
                access_counts.append(int(memory.get('access_count', 0)))

                created_at_raw = memory.get('created_at')
                if created_at_raw:
                    try:
                        created_dates.append(datetime.fromisoformat(created_at_raw))
                    except Exception:
                        pass

            
            # Calculate averages
            avg_importance = sum(importance_scores) / len(importance_scores) if importance_scores else 0
            avg_access = sum(access_counts) / len(access_counts) if access_counts else 0
            
            # Find oldest and newest
            oldest = min(created_dates) if created_dates else None
            newest = max(created_dates) if created_dates else None
            
            stats = {
                'total_memories': len(memories),
                'memory_types': memory_types,
                'average_importance': round(avg_importance, 3),
                'average_access_count': round(avg_access, 2),
                'oldest_memory': oldest.isoformat() if oldest else None,
                'newest_memory': newest.isoformat() if newest else None,
                'importance_distribution': {
                    'high': len([s for s in importance_scores if s >= 0.7]),
                    'medium': len([s for s in importance_scores if 0.3 <= s < 0.7]),
                    'low': len([s for s in importance_scores if s < 0.3])
                }
            }
            
            logger.info(f"Memory statistics: {stats['total_memories']} memories, avg importance: {stats['average_importance']}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get memory statistics: {e}")
            return {}
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """
        Clean up memories from old sessions.
        
        Args:
            days_old: Number of days to consider a session old
            
        Returns:
            Number of memories cleaned up
        """
        try:
            self._get_cosmos_client()

            container = self._container
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Find old memories
            query = """
            SELECT c.id, c.session_id 
            FROM c 
            WHERE c.created_at < @cutoff_date
            """
            
            parameters = [{"name": "@cutoff_date", "value": cutoff_date.isoformat()}]
            
            old_memories = list(container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            # Delete old memories
            cleaned_count = 0
            for memory in old_memories:
                try:
                    container.delete_item(item=memory['id'], partition_key=memory['session_id'])
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete old memory {memory['id']}: {e}")
            
            logger.info(f"✅ Cleaned up {cleaned_count} memories from sessions older than {days_old} days")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old sessions: {e}")
            return 0
    
    async def _prune_ai_optimized(self) -> int:
        """
        AI-optimized pruning strategy using OpenAI for intelligent memory management.
        
        This method demonstrates advanced memory pruning using AI to determine
        which memories are most valuable to retain for optimal performance.
        
        Returns:
            Number of memories pruned
        """
        try:
            if not self.enable_ai_scoring:
                logger.info("AI scoring disabled, falling back to hybrid pruning")
                return self._prune_hybrid()
            
            kernel = self._get_openai_kernel()
            if not kernel:
                return self._prune_hybrid()
            
            self._get_cosmos_client()
            container = self._container
            
            # Get all memories for analysis
            memories = list(container.query_items(
                query="SELECT * FROM c WHERE c.is_archived = false",
                enable_cross_partition_query=True
            ))
            
            if len(memories) <= self.max_memories:
                return 0
            
            logger.info(f"🧠 AI-optimized pruning: analyzing {len(memories)} memories")
            
            # Use AI to score memories for retention
            memory_scores = await self._ai_score_memories_for_retention(memories)
            
            # Sort by AI retention score (ascending - lowest scores get pruned)
            memories_with_scores = list(zip(memories, memory_scores))
            memories_with_scores.sort(key=lambda x: x[1])
            
            # Calculate how many to prune
            to_prune = len(memories) - self.max_memories
            memories_to_prune = memories_with_scores[:to_prune]
            
            # Archive memories instead of deleting (for learning purposes)
            pruned_count = 0
            for memory, score in memories_to_prune:
                try:
                    memory['is_archived'] = True
                    memory['ai_retention_score'] = score
                    memory['pruned_at'] = datetime.utcnow().isoformat()
                    container.upsert_item(memory)
                    pruned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to archive memory {memory.get('id', 'unknown')}: {e}")
            
            logger.info(f"✅ AI-optimized pruning: archived {pruned_count} memories")
            return pruned_count
            
        except Exception as e:
            logger.error(f"❌ AI-optimized pruning failed: {e}")
            return self._prune_hybrid()
    
    async def _ai_score_memories_for_retention(self, memories: List[Dict[str, Any]]) -> List[float]:
        """
        Use AI to score memories for retention decisions.
        
        Args:
            memories: List of memory dictionaries
            
        Returns:
            List of retention scores (0.0 = prune, 1.0 = keep)
        """
        try:
            kernel = self._get_openai_kernel()
            if not kernel:
                return [0.5] * len(memories)  # Default neutral score
            
            # Create AI scoring prompt
            scoring_prompt = f"""
            You are an AI memory management system. Analyze the following memories and score each one 
            for retention priority (0.0 = low priority/prune, 1.0 = high priority/keep).
            
            Consider these factors:
            1. Importance and relevance to user goals
            2. Recency and temporal relevance
            3. Uniqueness and non-redundancy
            4. Actionability and practical value
            5. Emotional significance
            6. Knowledge completeness
            
            Memories to analyze:
            {json.dumps([{
                'id': m.get('id', ''),
                'content': m.get('content', '')[:200],
                'memory_type': m.get('memory_type', ''),
                'importance_score': m.get('importance_score', 0),
                'access_count': m.get('access_count', 0),
                'created_at': m.get('created_at', ''),
                'tags': m.get('tags', [])
            } for m in memories], indent=2)}
            
            Return a JSON array of scores, one for each memory in the same order.
            Example: [0.8, 0.3, 0.9, 0.1, ...]
            """
            
            # Create scoring function
            scoring_function = kernel.add_function(
                function_name="score_memories_for_retention",
                plugin_name="memory_management",
                prompt=scoring_prompt
            )
            
            # Execute AI scoring
            result = await kernel.invoke(scoring_function)
            scores_text = str(result)
            
            # Parse JSON response
            try:
                json_start = scores_text.find('[')
                json_end = scores_text.rfind(']') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = scores_text[json_start:json_end]
                    scores = json.loads(json_str)
                    if len(scores) == len(memories):
                        return scores
            except Exception as e:
                logger.warning(f"Failed to parse AI scores: {e}")
            
            # Fallback to heuristic scoring
            return self._heuristic_memory_scoring(memories)
            
        except Exception as e:
            logger.error(f"AI memory scoring failed: {e}")
            return self._heuristic_memory_scoring(memories)
    
    def _heuristic_memory_scoring(self, memories: List[Dict[str, Any]]) -> List[float]:
        """
        Heuristic fallback for memory scoring when AI is unavailable.
        
        Args:
            memories: List of memory dictionaries
            
        Returns:
            List of retention scores
        """
        scores = []
        current_time = datetime.utcnow()
        
        for memory in memories:
            score = 0.0
            
            # Base importance score
            importance = memory.get('importance_score', 0.5)
            score += importance * 0.4
            
            # Access frequency bonus
            access_count = memory.get('access_count', 0)
            score += min(access_count * 0.1, 0.3)
            
            # Recency bonus
            try:
                created_at = datetime.fromisoformat(memory.get('created_at', ''))
                days_old = (current_time - created_at).days
                recency_bonus = max(0, 1.0 - (days_old / 30))  # Decay over 30 days
                score += recency_bonus * 0.2
            except:
                score += 0.1  # Default for invalid dates
            
            # Memory type bonus
            memory_type = memory.get('memory_type', '')
            if memory_type in ['knowledge', 'system_event']:
                score += 0.1
            elif memory_type == 'conversation':
                score += 0.05
            
            # Size penalty (very large memories are less efficient)
            content_length = len(memory.get('content', ''))
            if content_length > 1000:
                score -= 0.1
            
            scores.append(max(0.0, min(1.0, score)))
        
        return scores
    
    async def optimize_memory_performance(self, session_id: str = None) -> Dict[str, Any]:
        """
        Comprehensive memory performance optimization.
        
        This method demonstrates how to optimize memory for better performance
        by combining pruning, reordering, and AI-powered analysis.
        
        Args:
            session_id: Optional session ID to optimize specific session
            
        Returns:
            Dictionary with optimization results
        """
        try:
            logger.info("🚀 Starting comprehensive memory performance optimization")
            
            optimization_results = {
                'pruned_memories': 0,
                'reordered_memories': 0,
                'archived_memories': 0,
                'optimization_time': 0,
                'performance_improvements': {}
            }
            
            start_time = datetime.utcnow()
            
            # Step 1: AI-optimized pruning
            if self.performance_config['enable_auto_pruning']:
                logger.info("✂️ Performing AI-optimized memory pruning...")
                pruned = await self._prune_ai_optimized()
                optimization_results['pruned_memories'] = pruned
            
            # Step 2: Intelligent reordering
            if self.performance_config['enable_auto_reordering']:
                logger.info("🔄 Performing intelligent memory reordering...")
                reordered = await self._reorder_memories_intelligent(session_id)
                optimization_results['reordered_memories'] = reordered
            
            # Step 3: Archive old, low-value memories
            logger.info("📦 Archiving old, low-value memories...")
            archived = await self._archive_old_memories()
            optimization_results['archived_memories'] = archived
            
            # Step 4: Calculate performance improvements
            optimization_results['optimization_time'] = (datetime.utcnow() - start_time).total_seconds()
            optimization_results['performance_improvements'] = await self._calculate_performance_improvements()
            
            logger.info(f"✅ Memory optimization completed in {optimization_results['optimization_time']:.2f}s")
            logger.info(f"   Pruned: {optimization_results['pruned_memories']}")
            logger.info(f"   Reordered: {optimization_results['reordered_memories']}")
            logger.info(f"   Archived: {optimization_results['archived_memories']}")
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"❌ Memory optimization failed: {e}")
            return {'error': str(e)}
    
    async def _reorder_memories_intelligent(self, session_id: str = None) -> int:
        """
        Intelligent memory reordering using AI and performance metrics.
        
        Args:
            session_id: Optional session ID to reorder specific session
            
        Returns:
            Number of memories reordered
        """
        try:
            self._get_cosmos_client()
            container = self._container
            
            # Build query
            if session_id:
                query = "SELECT * FROM c WHERE c.session_id = @session_id AND c.is_archived = false"
                parameters = [{"name": "@session_id", "value": session_id}]
                enable_cross_partition = False
            else:
                query = "SELECT * FROM c WHERE c.is_archived = false"
                parameters = []
                enable_cross_partition = True
            
            memories = list(container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=enable_cross_partition
            ))
            
            if not memories:
                return 0
            
            logger.info(f"🧠 Intelligently reordering {len(memories)} memories")
            
            # Calculate intelligent priority scores
            if self.enable_ai_scoring:
                priority_scores = await self._calculate_intelligent_priorities(memories)
            else:
                priority_scores = self._calculate_heuristic_priorities(memories)
            
            # Update memories with new priority scores
            reordered_count = 0
            for memory, priority in zip(memories, priority_scores):
                memory['priority_score'] = priority
                memory['last_reordered'] = datetime.utcnow().isoformat()
                container.upsert_item(memory)
                reordered_count += 1
            
            logger.info(f"✅ Intelligently reordered {reordered_count} memories")
            return reordered_count
            
        except Exception as e:
            logger.error(f"❌ Intelligent reordering failed: {e}")
            return 0
    
    async def _calculate_intelligent_priorities(self, memories: List[Dict[str, Any]]) -> List[float]:
        """
        Calculate intelligent priority scores using AI.
        
        Args:
            memories: List of memory dictionaries
            
        Returns:
            List of priority scores
        """
        try:
            kernel = self._get_openai_kernel()
            if not kernel:
                return self._calculate_heuristic_priorities(memories)
            
            # Create AI priority calculation prompt
            priority_prompt = f"""
            You are an AI memory prioritization system. Calculate priority scores (0.0-1.0) 
            for the following memories based on their value for future retrieval and context.
            
            Consider:
            1. Information density and uniqueness
            2. Actionability and practical value
            3. Temporal relevance and recency
            4. User interaction patterns
            5. Knowledge completeness
            6. Contextual importance
            
            Memories to prioritize:
            {json.dumps([{
                'id': m.get('id', ''),
                'content': m.get('content', '')[:150],
                'memory_type': m.get('memory_type', ''),
                'importance_score': m.get('importance_score', 0),
                'access_count': m.get('access_count', 0),
                'created_at': m.get('created_at', ''),
                'tags': m.get('tags', [])
            } for m in memories], indent=2)}
            
            Return a JSON array of priority scores (0.0-1.0), one for each memory.
            Higher scores indicate higher priority for retrieval.
            """
            
            # Create priority function
            priority_function = kernel.add_function(
                function_name="calculate_memory_priorities",
                plugin_name="memory_prioritization",
                prompt=priority_prompt
            )
            
            # Execute AI priority calculation
            result = await kernel.invoke(priority_function)
            priorities_text = str(result)
            
            # Parse JSON response
            try:
                json_start = priorities_text.find('[')
                json_end = priorities_text.rfind(']') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = priorities_text[json_start:json_end]
                    priorities = json.loads(json_str)
                    if len(priorities) == len(memories):
                        return priorities
            except Exception as e:
                logger.warning(f"Failed to parse AI priorities: {e}")
            
            return self._calculate_heuristic_priorities(memories)
            
        except Exception as e:
            logger.error(f"AI priority calculation failed: {e}")
            return self._calculate_heuristic_priorities(memories)
    
    def _calculate_heuristic_priorities(self, memories: List[Dict[str, Any]]) -> List[float]:
        """
        Calculate heuristic priority scores when AI is unavailable.
        
        Args:
            memories: List of memory dictionaries
            
        Returns:
            List of priority scores
        """
        priorities = []
        current_time = datetime.utcnow()
        
        for memory in memories:
            priority = 0.0
            
            # Base importance
            importance = memory.get('importance_score', 0.5)
            priority += importance * 0.3
            
            # Access frequency
            access_count = memory.get('access_count', 0)
            priority += min(access_count * 0.2, 0.4)
            
            # Recency
            try:
                created_at = datetime.fromisoformat(memory.get('created_at', ''))
                days_old = (current_time - created_at).days
                recency = max(0, 1.0 - (days_old / 90))  # 90-day decay
                priority += recency * 0.2
            except:
                priority += 0.1
            
            # Memory type bonus
            memory_type = memory.get('memory_type', '')
            if memory_type == 'knowledge':
                priority += 0.1
            elif memory_type == 'system_event':
                priority += 0.05
            
            priorities.append(max(0.0, min(1.0, priority)))
        
        return priorities
    
    async def _archive_old_memories(self) -> int:
        """
        Archive old, low-value memories instead of deleting them.
        
        Returns:
            Number of memories archived
        """
        try:
            self._get_cosmos_client()
            container = self._container
            
            # Find old memories with low importance
            cutoff_date = (datetime.utcnow() - timedelta(days=90)).isoformat()
            
            old_memories = list(container.query_items(
                query="""
                SELECT * FROM c 
                WHERE c.created_at < @cutoff_date 
                AND c.importance_score < @threshold 
                AND c.is_archived = false
                """,
                parameters=[
                    {"name": "@cutoff_date", "value": cutoff_date},
                    {"name": "@threshold", "value": 0.3}
                ],
                enable_cross_partition_query=True
            ))
            
            archived_count = 0
            for memory in old_memories:
                try:
                    memory['is_archived'] = True
                    memory['archived_at'] = datetime.utcnow().isoformat()
                    memory['archive_reason'] = 'age_and_low_importance'
                    container.upsert_item(memory)
                    archived_count += 1
                except Exception as e:
                    logger.warning(f"Failed to archive memory {memory.get('id', 'unknown')}: {e}")
            
            logger.info(f"📦 Archived {archived_count} old, low-value memories")
            return archived_count
            
        except Exception as e:
            logger.error(f"❌ Memory archiving failed: {e}")
            return 0
    
    async def _calculate_performance_improvements(self) -> Dict[str, Any]:
        try:
            self._get_cosmos_client()
            c = self._container
            active = list(c.query_items(
                query="SELECT VALUE COUNT(1) FROM c WHERE c.is_archived = false",
                enable_cross_partition_query=True))[0]
            archived = list(c.query_items(
                query="SELECT VALUE COUNT(1) FROM c WHERE c.is_archived = true",
                enable_cross_partition_query=True))[0]
            active = int(active or 0)
            archived = int(archived or 0)
            total = active + archived
            eff = active / max(total, 1)
            util = active / max(self.max_memories, 1)
            return {
                "total_memories": total,
                "active_memories": active,
                "archived_memories": archived,
                "memory_efficiency": eff,
                "storage_utilization": util,
                "optimization_score": min(1.0, eff * (1.0 - util)),
            }
        except Exception as e:
            logger.error(f"❌ Perf calc failed: {e}")
            return {"error": str(e)}


# Example usage and demonstration functions
async def demonstrate_long_term_memory():
    """
    Demonstrate the enhanced LongTermMemory class with AI-powered optimization.
    Perfect for student learning about memory pruning and reordering!
    """
    print("🧠 Long-Term Memory Management Demonstration")
    print("=" * 60)
    print("🎯 Learning Objectives:")
    print("   • Develop methods for updating and managing agent memory using Python with Cosmos DB")
    print("   • Demonstrate how to prune or reorder memory for better performance")
    print("   • Maintain context over extended sessions with intelligent memory management")
    print("=" * 60)
    
    # Create long-term memory with AI scoring enabled
    ltm = LongTermMemory(
        max_memories=15, 
        importance_threshold=0.3,
        enable_ai_scoring=True
    )
    
    print(f"✅ Created long-term memory system:")
    print(f"   • Max memories: {ltm.max_memories}")
    print(f"   • Importance threshold: {ltm.importance_threshold}")
    print(f"   • AI scoring enabled: {ltm.enable_ai_scoring}")
    print()
    
    # Simulate adding memories from different sessions
    session1 = "travel_session_001"
    session2 = "work_session_002"
    session3 = "personal_session_003"
    
    print("📝 Adding diverse memories from multiple sessions...")
    
    # Session 1: Travel memories (high importance)
    await ltm.add_memory(session1, "User planning trip to Japan for cherry blossom season", "conversation", 0.9, ["travel", "japan", "cherry-blossoms"], context="User is planning a major trip")
    await ltm.add_memory(session1, "Booked flights to Tokyo for March 15-25", "tool_call", 0.8, ["booking", "flights", "tokyo"], context="Confirmed travel dates")
    await ltm.add_memory(session1, "Reserved hotel in Shibuya district", "tool_call", 0.7, ["booking", "hotel", "shibuya"], context="Accommodation confirmed")
    await ltm.add_memory(session1, "User asked about best cherry blossom viewing spots", "conversation", 0.6, ["travel", "japan", "sightseeing"], context="Planning activities")
    
    # Session 2: Work memories (medium importance)
    await ltm.add_memory(session2, "User working on quarterly report presentation", "conversation", 0.7, ["work", "presentation", "quarterly"], context="Important work project")
    await ltm.add_memory(session2, "Scheduled meeting with team for next Tuesday", "system_event", 0.5, ["work", "meeting", "team"], context="Team coordination")
    await ltm.add_memory(session2, "User completed data analysis for Q3 metrics", "tool_call", 0.6, ["work", "analysis", "metrics"], context="Project milestone")
    
    # Session 3: Personal memories (mixed importance)
    await ltm.add_memory(session3, "User's birthday is next month", "conversation", 0.8, ["personal", "birthday", "celebration"], context="Personal milestone")
    await ltm.add_memory(session3, "User mentioned favorite restaurant closed down", "conversation", 0.3, ["personal", "restaurant", "disappointment"], context="Minor personal update")
    await ltm.add_memory(session3, "User learning Spanish language", "knowledge", 0.6, ["personal", "learning", "spanish"], context="Skill development")
    
    print(f"✅ Added memories to sessions: {session1}, {session2}, {session3}")
    print()
    
    # Demonstrate memory search capabilities
    print("🔍 Demonstrating Memory Search Capabilities:")
    print("-" * 40)
    
    # Search by content
    travel_memories = ltm.search_memories(session1, query="japan")
    print(f"   • Found {len(travel_memories)} Japan-related memories in travel session")
    
    # Search by importance
    important_memories = ltm.search_memories(session1, min_importance=0.7)
    print(f"   • Found {len(important_memories)} high-importance memories in travel session")
    
    # Search by memory type
    work_memories = ltm.search_memories(session2, memory_type="tool_call")
    print(f"   • Found {len(work_memories)} tool call memories in work session")
    
    # Demonstrate memory statistics
    print("\n📊 Memory Statistics Analysis:")
    print("-" * 40)
    stats = ltm.get_memory_statistics()
    print(f"   • Total memories: {stats['total_memories']}")
    print(f"   • Average importance: {stats['average_importance']:.2f}")
    print(f"   • Memory types distribution: {stats['memory_types']}")
    print(f"   • Oldest memory: {stats.get('oldest_memory', 'N/A')}")
    print(f"   • Newest memory: {stats.get('newest_memory', 'N/A')}")
    
    # Demonstrate AI-powered memory optimization
    print("\n🚀 AI-Powered Memory Performance Optimization:")
    print("-" * 50)
    print("This demonstrates the core learning objective: pruning and reordering for better performance")
    
    # Add more memories to trigger optimization
    print("   📝 Adding more memories to trigger optimization...")
    for i in range(10):
        await ltm.add_memory(
            f"test_session_{i+4}", 
            f"Test memory {i} with varying importance", 
            "conversation", 
            0.1 + (i * 0.05),  # Varying importance scores
            ["test", "optimization"]
        )
    
    # Run comprehensive memory optimization
    print("   🧠 Running AI-powered memory optimization...")
    optimization_results = await ltm.optimize_memory_performance()
    
    print(f"\n✅ Memory Optimization Results:")
    print(f"   • Pruned memories: {optimization_results['pruned_memories']}")
    print(f"   • Reordered memories: {optimization_results['reordered_memories']}")
    print(f"   • Archived memories: {optimization_results['archived_memories']}")
    print(f"   • Optimization time: {optimization_results['optimization_time']:.2f} seconds")
    
    # Show performance improvements
    perf = optimization_results.get('performance_improvements', {})
    if 'error' not in perf:
        print(f"\n📈 Performance Improvements:")
        print(f"   • Memory efficiency: {perf.get('memory_efficiency', 0):.2%}")
        print(f"   • Storage utilization: {perf.get('storage_utilization', 0):.2%}")
        print(f"   • Optimization score: {perf.get('optimization_score', 0):.2f}")
    
    # Demonstrate different pruning strategies
    print("\n✂️ Memory Pruning Strategies Demonstration:")
    print("-" * 45)
    
    strategies = ['importance', 'age', 'access_frequency', 'hybrid', 'ai_optimized']
    for strategy in strategies:
        if strategy in ltm.pruning_strategies:
            print(f"   • {strategy.replace('_', ' ').title()} pruning available")
    
    # Demonstrate reordering strategies
    print("\n🔄 Memory Reordering Strategies Demonstration:")
    print("-" * 45)
    
    reorder_strategies = ['importance', 'recency', 'access_frequency']
    for strategy in reorder_strategies:
        reordered = ltm.reorder_memories(session1, strategy=strategy)
        print(f"   • {strategy.title()} reordering: {reordered} memories reordered")
    
    # Final statistics
    print("\n📊 Final Memory Statistics:")
    print("-" * 30)
    final_stats = ltm.get_memory_statistics()
    print(f"   • Total memories: {final_stats['total_memories']}")
    print(f"   • Average importance: {final_stats['average_importance']:.2f}")
    print(f"   • Memory efficiency improved through optimization")
    
    print("\n🎉 Long-Term Memory Management Demonstration Complete!")
    print("=" * 60)
    print("✅ Key Learning Objectives Achieved:")
    print("   ✓ Developed methods for updating and managing agent memory using Python with Cosmos DB")
    print("   ✓ Demonstrated how to prune or reorder memory for better performance")
    print("   ✓ Maintained context over extended sessions with intelligent memory management")
    print("   ✓ Implemented performance optimization strategies for long-term memory systems")
    
    return ltm


async def main():
    """Main function to run the demonstration"""
    try:
        await demonstrate_long_term_memory()
    except Exception as e:
        logger.error(f"❌ Demonstration failed: {e}")
        print(f"\n❌ Error: {e}")
        print("Please check your environment variables and Cosmos DB connection.")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())
