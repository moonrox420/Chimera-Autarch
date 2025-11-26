"""
CHIMERA AUTARCH - GraphQL API Layer
Provides a GraphQL interface for querying system state, evolutions, and metrics.
"""
import json
from typing import Dict, Any, List, Optional
from dataclasses import asdict


class GraphQLSchema:
    """Simple GraphQL schema definition"""

    SCHEMA = """
    type Query {
        systemStatus: SystemStatus!
        nodes(status: String): [Node!]!
        node(id: ID!): Node
        tools: [Tool!]!
        tool(name: String!): Tool
        evolutions(topic: String, limit: Int): [Evolution!]!
        metrics(topic: String): Metrics!
        topics: [Topic!]!
    }
    
    type SystemStatus {
        uptime: Float!
        nodeCount: Int!
        confidence: Float!
        activeTopics: [String!]!
        timestamp: Float!
    }
    
    type Node {
        id: ID!
        type: String!
        status: String!
        reputation: Float!
        lastHeartbeat: Float!
        capabilities: [String!]!
        resources: JSON
    }
    
    type Tool {
        name: String!
        description: String!
        version: String!
        dependencies: [String!]!
        successRate: Float!
        avgLatency: Float!
        sampleSize: Int!
    }
    
    type Evolution {
        id: ID!
        topic: String!
        failureReason: String!
        appliedFix: String!
        observedImprovement: Float!
        timestamp: Float!
        validationMetrics: JSON
    }
    
    type Metrics {
        topic: String
        confidence: Float
        failureCount: Int
        successRate: Float
        recentHistory: [Boolean!]
    }
    
    type Topic {
        name: String!
        confidence: Float!
        failureCount: Int!
        successRate: Float!
    }
    
    scalar JSON
    """


class GraphQLResolver:
    """Resolver for GraphQL queries"""

    def __init__(self, heart_node):
        self.heart = heart_node

    async def resolve(self, query: str, variables: Dict = None) -> Dict[str, Any]:
        """
        Simple GraphQL query resolver
        Note: This is a basic implementation. For production, use a library like Strawberry or Graphene.
        """
        variables = variables or {}

        # Parse query to extract operation
        # This is a simplified parser - production should use proper GraphQL parser
        query = query.strip()

        if query.startswith("query") or query.startswith("{"):
            return await self._resolve_query(query, variables)

        return {"errors": [{"message": "Invalid query"}]}

    async def _resolve_query(self, query: str, variables: Dict) -> Dict[str, Any]:
        """Resolve a GraphQL query"""
        data = {}
        errors = []

        try:
            if "__schema" in query:
                data["__schema"] = {
                    "types": [
                        {"name": "Query"},
                        {"name": "SystemStatus"},
                        {"name": "Node"},
                        {"name": "Tool"},
                        {"name": "Evolution"},
                        {"name": "Metrics"},
                        {"name": "Topic"}
                    ]
                }

            if "systemStatus" in query:
                data["systemStatus"] = await self._resolve_system_status()

            if "nodes" in query:
                status_filter = variables.get("status")
                data["nodes"] = await self._resolve_nodes(status_filter)

            if "node(" in query:
                node_id = self._extract_argument(
                    query, "node", "id", variables)
                if node_id:
                    data["node"] = await self._resolve_node(node_id)

            if "tools" in query:
                data["tools"] = await self._resolve_tools()

            if "tool(" in query:
                tool_name = self._extract_argument(
                    query, "tool", "name", variables)
                if tool_name:
                    data["tool"] = await self._resolve_tool(tool_name)

            if "evolutions" in query:
                topic = self._extract_argument(
                    query, "evolutions", "topic", variables)
                limit = self._extract_argument(
                    query, "evolutions", "limit", variables)
                limit = int(limit) if limit else 10
                data["evolutions"] = await self._resolve_evolutions(topic, limit)

            if "metrics" in query:
                topic = self._extract_argument(
                    query, "metrics", "topic", variables)
                data["metrics"] = await self._resolve_metrics(topic)

            if "topics" in query:
                data["topics"] = await self._resolve_topics()

        except Exception as e:
            errors.append({"message": str(e)})

        result = {"data": data}
        if errors:
            result["errors"] = errors

        return result

    def _extract_argument(self, query: str, field: str, arg: str, variables: Dict) -> Optional[str]:
        """Extract argument value from query"""
        # Very simplified - looks for field(arg: value) or field(arg: $variable)
        import re

        # Try direct value first
        pattern = f'{field}\\s*\\(\\s*{arg}\\s*:\\s*"([^"]+)"'
        match = re.search(pattern, query)
        if match:
            return match.group(1)

        # Try variable reference
        pattern = f'{field}\\s*\\(\\s*{arg}\\s*:\\s*\\$([a-zA-Z0-9_]+)'
        match = re.search(pattern, query)
        if match:
            var_name = match.group(1)
            return variables.get(var_name)

        return None

    async def _resolve_system_status(self) -> Dict[str, Any]:
        """Resolve systemStatus query"""
        import time

        patterns = self.heart.metacog.failure_patterns
        total_confidence = sum(
            p.confidence for p in patterns.values()) if patterns else 1.0
        avg_confidence = total_confidence / len(patterns) if patterns else 1.0

        return {
            "uptime": time.time() - self.heart.start_time,
            "nodeCount": len(self.heart.nodes),
            "confidence": avg_confidence,
            "activeTopics": list(patterns.keys()),
            "timestamp": time.time()
        }

    async def _resolve_nodes(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Resolve nodes query"""
        import time

        nodes = []
        now = time.time()

        for node_id, node in self.heart.nodes.items():
            last_seen = now - node.last_heartbeat
            node_status = "healthy" if last_seen < 60 else "warning" if last_seen < 90 else "timeout"

            if status_filter and node_status != status_filter:
                continue

            nodes.append({
                "id": node_id,
                "type": node.type,
                "status": node_status,
                "reputation": node.reputation,
                "lastHeartbeat": node.last_heartbeat,
                "capabilities": node.capabilities,
                "resources": node.resources
            })

        return nodes

    async def _resolve_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Resolve single node query"""
        import time

        if node_id not in self.heart.nodes:
            return None

        node = self.heart.nodes[node_id]
        last_seen = time.time() - node.last_heartbeat
        node_status = "healthy" if last_seen < 60 else "warning" if last_seen < 90 else "timeout"

        return {
            "id": node_id,
            "type": node.type,
            "status": node_status,
            "reputation": node.reputation,
            "lastHeartbeat": node.last_heartbeat,
            "capabilities": node.capabilities,
            "resources": node.resources
        }

    async def _resolve_tools(self) -> List[Dict[str, Any]]:
        """Resolve tools query"""
        tools = []

        for name, tool in self.heart.registry.tools.items():
            metrics = self.heart.registry.get_metrics(name)

            tools.append({
                "name": name,
                "description": tool.description,
                "version": tool.version,
                "dependencies": tool.dependencies,
                "successRate": metrics.get("success_rate", 1.0),
                "avgLatency": metrics.get("avg_latency", 0.0),
                "sampleSize": metrics.get("sample_size", 0)
            })

        return tools

    async def _resolve_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Resolve single tool query"""
        if name not in self.heart.registry.tools:
            return None

        tool = self.heart.registry.tools[name]
        metrics = self.heart.registry.get_metrics(name)

        return {
            "name": name,
            "description": tool.description,
            "version": tool.version,
            "dependencies": tool.dependencies,
            "successRate": metrics.get("success_rate", 1.0),
            "avgLatency": metrics.get("avg_latency", 0.0),
            "sampleSize": metrics.get("sample_size", 0)
        }

    async def _resolve_evolutions(self, topic: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Resolve evolutions query"""
        import aiosqlite

        query = "SELECT * FROM evolutions WHERE 1=1"
        params = []

        if topic:
            query += " AND topic LIKE ?"
            params.append(f"%{topic}%")

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        evolutions = []

        try:
            async with aiosqlite.connect(self.heart.metacog.persistence.db_path) as db:
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]

                    for row in rows:
                        evolution = dict(zip(columns, row))
                        # Parse validation_metrics if it's stored as JSON string
                        if 'validation_metrics' in evolution and isinstance(evolution['validation_metrics'], str):
                            try:
                                evolution['validationMetrics'] = json.loads(
                                    evolution['validation_metrics'])
                            except:
                                evolution['validationMetrics'] = {}
                        else:
                            evolution['validationMetrics'] = evolution.get(
                                'validation_metrics', {})

                        evolutions.append({
                            "id": evolution.get('id', ''),
                            "topic": evolution.get('topic', ''),
                            "failureReason": evolution.get('failure_reason', ''),
                            "appliedFix": evolution.get('applied_fix', ''),
                            "observedImprovement": evolution.get('observed_improvement', 0.0),
                            "timestamp": evolution.get('timestamp', 0.0),
                            "validationMetrics": evolution['validationMetrics']
                        })
        except Exception as e:
            print(f"Error querying evolutions: {e}")

        return evolutions

    async def _resolve_metrics(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """Resolve metrics query"""
        patterns = self.heart.metacog.failure_patterns

        if topic:
            if topic not in patterns:
                return {
                    "topic": topic,
                    "confidence": None,
                    "failureCount": None,
                    "successRate": None,
                    "recentHistory": []
                }

            pattern = patterns[topic]
            return {
                "topic": topic,
                "confidence": pattern.confidence,
                "failureCount": pattern.failure_count,
                "successRate": pattern.success_rate,
                "recentHistory": list(pattern.success_history)[-20:]
            }
        else:
            # Return aggregated metrics
            total_confidence = sum(
                p.confidence for p in patterns.values()) if patterns else 0.0
            avg_confidence = total_confidence / \
                len(patterns) if patterns else 0.0
            total_failures = sum(p.failure_count for p in patterns.values())

            return {
                "topic": None,
                "confidence": avg_confidence,
                "failureCount": total_failures,
                "successRate": avg_confidence,  # Approximate
                "recentHistory": []
            }

    async def _resolve_topics(self) -> List[Dict[str, Any]]:
        """Resolve topics query"""
        topics = []

        for topic_name, pattern in self.heart.metacog.failure_patterns.items():
            topics.append({
                "name": topic_name,
                "confidence": pattern.confidence,
                "failureCount": pattern.failure_count,
                "successRate": pattern.success_rate
            })

        return topics
