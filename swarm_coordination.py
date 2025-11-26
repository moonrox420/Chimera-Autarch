#!/usr/bin/env python3
"""
CHIMERA AUTARCH - Multi-Agent Swarm Coordination
Spawn child agents, task decomposition, consensus decision making
"""
import asyncio
import subprocess
import sys
import json
import time
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging

logger = logging.getLogger("chimera.swarm")


class AgentStatus(Enum):
    """Agent lifecycle states"""
    SPAWNING = "spawning"
    INITIALIZING = "initializing"
    IDLE = "idle"
    BUSY = "busy"
    FAILED = "failed"
    TERMINATED = "terminated"


class ConsensusMethod(Enum):
    """Consensus algorithms"""
    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_VOTE = "weighted_vote"
    UNANIMOUS = "unanimous"
    QUORUM = "quorum"


@dataclass
class Task:
    """Distributed task"""
    task_id: str
    description: str
    subtasks: List['Task'] = field(default_factory=list)
    assigned_agent: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[Any] = None
    dependencies: List[str] = field(default_factory=list)  # task_ids
    priority: int = 5  # 1-10, higher = more important
    created_at: float = field(default_factory=lambda: time.time())
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


@dataclass
class AgentSpec:
    """Specification for spawning an agent"""
    agent_id: str
    role: str  # analyzer, executor, monitor, coordinator
    capabilities: Set[str]
    max_concurrent_tasks: int = 1
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    specialization: Optional[str] = None


@dataclass
class Agent:
    """Spawned CHIMERA agent"""
    agent_id: str
    spec: AgentSpec
    process: Optional[asyncio.subprocess.Process] = None
    status: AgentStatus = AgentStatus.SPAWNING
    current_tasks: List[str] = field(default_factory=list)
    completed_tasks: int = 0
    failed_tasks: int = 0
    reputation: float = 1.0  # 0.0 - 1.0
    spawned_at: float = field(default_factory=lambda: time.time())
    last_heartbeat: Optional[float] = None
    websocket_url: Optional[str] = None
    port: Optional[int] = None


@dataclass
class Vote:
    """Agent vote for consensus"""
    agent_id: str
    decision: Any
    confidence: float  # 0.0 - 1.0
    reasoning: str
    timestamp: float = field(default_factory=lambda: time.time())


class TaskDecomposer:
    """Decomposes complex tasks into subtasks"""

    def __init__(self):
        self.decomposition_patterns: Dict[str, Callable] = {}

    def register_pattern(self, pattern_name: str, decomposer: Callable):
        """Register task decomposition pattern"""
        self.decomposition_patterns[pattern_name] = decomposer

    async def decompose(self, task: Task) -> List[Task]:
        """Decompose task into subtasks"""
        # Check for registered patterns
        for pattern_name, decomposer in self.decomposition_patterns.items():
            if pattern_name in task.description.lower():
                subtasks = await decomposer(task)
                return subtasks

        # Default: simple decomposition by keywords
        return await self._default_decomposition(task)

    async def _default_decomposition(self, task: Task) -> List[Task]:
        """Default task decomposition logic"""
        subtasks = []

        # Check for multi-step indicators
        if "and" in task.description.lower():
            parts = task.description.split(" and ")
            for i, part in enumerate(parts):
                subtask = Task(
                    task_id=f"{task.task_id}_sub_{i}",
                    description=part.strip(),
                    priority=task.priority,
                    dependencies=[subtasks[-1].task_id] if subtasks else []
                )
                subtasks.append(subtask)

        # Check for numbered steps
        elif any(f"{i}." in task.description for i in range(1, 10)):
            lines = task.description.split('\n')
            for i, line in enumerate(lines):
                if any(line.strip().startswith(f"{j}.") for j in range(1, 10)):
                    subtask = Task(
                        task_id=f"{task.task_id}_step_{i}",
                        description=line.strip(),
                        priority=task.priority,
                        dependencies=[subtasks[-1].task_id] if subtasks else []
                    )
                    subtasks.append(subtask)

        return subtasks


class ConsensusEngine:
    """Implements consensus algorithms for multi-agent decisions"""

    def __init__(self, method: ConsensusMethod = ConsensusMethod.MAJORITY_VOTE):
        self.method = method
        self.quorum_threshold = 0.51  # 51% for quorum

    async def reach_consensus(
        self,
        votes: List[Vote],
        method: Optional[ConsensusMethod] = None
    ) -> tuple[Any, float]:
        """Reach consensus from agent votes

        Returns:
            (decision, confidence)
        """
        method = method or self.method

        if not votes:
            return None, 0.0

        if method == ConsensusMethod.MAJORITY_VOTE:
            return await self._majority_vote(votes)
        elif method == ConsensusMethod.WEIGHTED_VOTE:
            return await self._weighted_vote(votes)
        elif method == ConsensusMethod.UNANIMOUS:
            return await self._unanimous_vote(votes)
        elif method == ConsensusMethod.QUORUM:
            return await self._quorum_vote(votes)

        return None, 0.0

    async def _majority_vote(self, votes: List[Vote]) -> tuple[Any, float]:
        """Simple majority vote"""
        vote_counts = {}
        for vote in votes:
            decision_key = str(vote.decision)
            if decision_key not in vote_counts:
                vote_counts[decision_key] = []
            vote_counts[decision_key].append(vote)

        if not vote_counts:
            return None, 0.0

        # Find majority
        majority_decision = max(vote_counts.items(), key=lambda x: len(x[1]))
        decision_votes = majority_decision[1]

        confidence = len(decision_votes) / len(votes)
        avg_vote_confidence = sum(
            v.confidence for v in decision_votes) / len(decision_votes)

        final_confidence = confidence * avg_vote_confidence

        return decision_votes[0].decision, final_confidence

    async def _weighted_vote(self, votes: List[Vote]) -> tuple[Any, float]:
        """Vote weighted by agent confidence"""
        vote_weights = {}

        for vote in votes:
            decision_key = str(vote.decision)
            if decision_key not in vote_weights:
                vote_weights[decision_key] = 0.0
            vote_weights[decision_key] += vote.confidence

        if not vote_weights:
            return None, 0.0

        # Find highest weighted decision
        best_decision = max(vote_weights.items(), key=lambda x: x[1])

        total_weight = sum(vote_weights.values())
        confidence = best_decision[1] / total_weight

        # Convert back to actual decision
        for vote in votes:
            if str(vote.decision) == best_decision[0]:
                return vote.decision, confidence

        return None, 0.0

    async def _unanimous_vote(self, votes: List[Vote]) -> tuple[Any, float]:
        """Require unanimous agreement"""
        if not votes:
            return None, 0.0

        first_decision = votes[0].decision

        # Check if all votes agree
        if all(v.decision == first_decision for v in votes):
            avg_confidence = sum(v.confidence for v in votes) / len(votes)
            return first_decision, avg_confidence

        return None, 0.0

    async def _quorum_vote(self, votes: List[Vote]) -> tuple[Any, float]:
        """Require quorum (>50%) agreement"""
        vote_counts = {}

        for vote in votes:
            decision_key = str(vote.decision)
            if decision_key not in vote_counts:
                vote_counts[decision_key] = []
            vote_counts[decision_key].append(vote)

        if not vote_counts:
            return None, 0.0

        # Check for quorum
        for decision_key, decision_votes in vote_counts.items():
            if len(decision_votes) / len(votes) >= self.quorum_threshold:
                avg_confidence = sum(
                    v.confidence for v in decision_votes) / len(decision_votes)
                return decision_votes[0].decision, avg_confidence

        return None, 0.0


class SwarmCoordinator:
    """Coordinates multi-agent swarm"""

    def __init__(self, max_agents: int = 10, base_port: int = 9000):
        self.max_agents = max_agents
        self.base_port = base_port
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_decomposer = TaskDecomposer()
        self.consensus_engine = ConsensusEngine()
        self.next_port = base_port
        self.workload_threshold = 0.8  # Spawn new agent if load > 80%

    async def spawn_agent(self, spec: AgentSpec) -> Optional[Agent]:
        """Spawn new CHIMERA agent process"""
        if len(self.agents) >= self.max_agents:
            logger.warning(
                f"Max agents ({self.max_agents}) reached, cannot spawn")
            return None

        # Allocate port
        port = self.next_port
        self.next_port += 1

        # Create agent
        agent = Agent(
            agent_id=spec.agent_id,
            spec=spec,
            port=port,
            websocket_url=f"ws://localhost:{port}"
        )

        # Spawn subprocess
        try:
            # Create specialized config for agent
            config = {
                "agent_id": spec.agent_id,
                "role": spec.role,
                "capabilities": list(spec.capabilities),
                "port": port,
                "parent_port": 8765,  # Connect to main CHIMERA
                "specialization": spec.specialization
            }

            config_path = Path(f"/tmp/chimera_agent_{spec.agent_id}.json")
            config_path.write_text(json.dumps(config, indent=2))

            # Spawn agent process
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(Path(__file__).parent / "chimera_autarch.py"),
                "--agent-mode",
                "--config", str(config_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            agent.process = process
            agent.status = AgentStatus.INITIALIZING

            self.agents[spec.agent_id] = agent

            logger.info(f"Spawned agent {spec.agent_id} on port {port}")

            # Monitor agent initialization
            asyncio.create_task(self._monitor_agent(agent))

            return agent

        except Exception as e:
            logger.error(f"Failed to spawn agent {spec.agent_id}: {e}")
            return None

    async def _monitor_agent(self, agent: Agent):
        """Monitor agent health"""
        await asyncio.sleep(5)  # Wait for initialization

        # Check if agent is running
        if agent.process and agent.process.returncode is None:
            agent.status = AgentStatus.IDLE
            logger.info(f"Agent {agent.agent_id} initialized successfully")
        else:
            agent.status = AgentStatus.FAILED
            logger.error(f"Agent {agent.agent_id} failed to initialize")

    async def terminate_agent(self, agent_id: str):
        """Terminate agent gracefully"""
        if agent_id not in self.agents:
            return

        agent = self.agents[agent_id]

        if agent.process:
            agent.process.terminate()
            await asyncio.sleep(2)

            if agent.process.returncode is None:
                agent.process.kill()

        agent.status = AgentStatus.TERMINATED
        logger.info(f"Terminated agent {agent_id}")

        # Reassign tasks
        for task_id in agent.current_tasks:
            if task_id in self.tasks:
                await self.reassign_task(task_id)

    async def submit_task(self, task: Task) -> str:
        """Submit task to swarm"""
        self.tasks[task.task_id] = task

        # Decompose if complex
        subtasks = await self.task_decomposer.decompose(task)

        if subtasks:
            logger.info(
                f"Decomposed task {task.task_id} into {len(subtasks)} subtasks")
            task.subtasks = subtasks
            for subtask in subtasks:
                self.tasks[subtask.task_id] = subtask

            # Dispatch subtasks
            for subtask in subtasks:
                await self._dispatch_task(subtask)
        else:
            # Dispatch task directly
            await self._dispatch_task(task)

        return task.task_id

    async def _dispatch_task(self, task: Task):
        """Dispatch task to best available agent"""
        # Check dependencies
        if task.dependencies:
            for dep_id in task.dependencies:
                if dep_id in self.tasks and self.tasks[dep_id].status != "completed":
                    logger.info(
                        f"Task {task.task_id} waiting for dependency {dep_id}")
                    return

        # Find best agent
        best_agent = await self._select_agent(task)

        if not best_agent:
            # No agent available, check if we should spawn
            if await self._should_spawn_agent():
                spec = AgentSpec(
                    agent_id=f"agent_{len(self.agents)}",
                    role="executor",
                    capabilities=set(),  # General purpose
                    max_concurrent_tasks=3
                )
                best_agent = await self.spawn_agent(spec)

        if best_agent:
            task.assigned_agent = best_agent.agent_id
            task.status = "in_progress"
            task.started_at = time.time()
            best_agent.current_tasks.append(task.task_id)
            best_agent.status = AgentStatus.BUSY

            logger.info(
                f"Assigned task {task.task_id} to agent {best_agent.agent_id}")

            # Execute task (in real implementation, send via WebSocket)
            asyncio.create_task(self._execute_task_on_agent(task, best_agent))
        else:
            logger.warning(f"No agent available for task {task.task_id}")

    async def _select_agent(self, task: Task) -> Optional[Agent]:
        """Select best agent for task using reputation and load"""
        available_agents = [
            a for a in self.agents.values()
            if a.status in [AgentStatus.IDLE, AgentStatus.BUSY]
            and len(a.current_tasks) < a.spec.max_concurrent_tasks
        ]

        if not available_agents:
            return None

        # Score agents
        def score_agent(agent: Agent) -> float:
            load_factor = 1.0 - (len(agent.current_tasks) /
                                 agent.spec.max_concurrent_tasks)
            reputation_factor = agent.reputation

            # Check capability match
            capability_bonus = 0.0
            # (In real implementation, check task requirements vs agent capabilities)

            return load_factor * 0.5 + reputation_factor * 0.4 + capability_bonus * 0.1

        best_agent = max(available_agents, key=score_agent)
        return best_agent

    async def _should_spawn_agent(self) -> bool:
        """Determine if new agent should be spawned"""
        if len(self.agents) >= self.max_agents:
            return False

        # Calculate overall swarm load
        if not self.agents:
            return True

        total_capacity = sum(
            a.spec.max_concurrent_tasks for a in self.agents.values())
        current_load = sum(len(a.current_tasks) for a in self.agents.values())

        load_ratio = current_load / total_capacity if total_capacity > 0 else 1.0

        return load_ratio > self.workload_threshold

    async def _execute_task_on_agent(self, task: Task, agent: Agent):
        """Execute task on agent (simulated)"""
        # In real implementation, send task via WebSocket to agent
        # For now, simulate execution

        await asyncio.sleep(2 + (task.priority * 0.1))  # Simulate work

        # Simulate success/failure based on agent reputation
        import random
        success = random.random() < agent.reputation

        if success:
            task.status = "completed"
            task.result = {"success": True,
                           "output": f"Task {task.task_id} completed"}
            task.completed_at = time.time()
            agent.completed_tasks += 1
            agent.reputation = min(1.0, agent.reputation + 0.01)
        else:
            task.status = "failed"
            task.result = {"success": False, "error": "Task failed"}
            agent.failed_tasks += 1
            agent.reputation = max(0.0, agent.reputation - 0.05)

        # Remove from current tasks
        agent.current_tasks.remove(task.task_id)

        if not agent.current_tasks:
            agent.status = AgentStatus.IDLE

        logger.info(
            f"Task {task.task_id} {task.status} on agent {agent.agent_id}")

    async def reassign_task(self, task_id: str):
        """Reassign failed task to different agent"""
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]
        task.assigned_agent = None
        task.status = "pending"

        await self._dispatch_task(task)

    async def request_consensus(
        self,
        question: str,
        options: List[Any],
        method: Optional[ConsensusMethod] = None
    ) -> tuple[Any, float]:
        """Request consensus decision from swarm"""
        votes: List[Vote] = []

        # Collect votes from all idle/busy agents
        active_agents = [
            a for a in self.agents.values()
            if a.status in [AgentStatus.IDLE, AgentStatus.BUSY]
        ]

        for agent in active_agents:
            # In real implementation, send question via WebSocket
            # For now, simulate vote
            import random
            vote = Vote(
                agent_id=agent.agent_id,
                decision=random.choice(options),
                confidence=random.uniform(0.5, 1.0) * agent.reputation,
                reasoning=f"Agent {agent.agent_id} analysis"
            )
            votes.append(vote)

        decision, confidence = await self.consensus_engine.reach_consensus(votes, method)

        logger.info(
            f"Consensus reached: {decision} (confidence={confidence:.2f}, "
            f"votes={len(votes)})"
        )

        return decision, confidence

    def get_swarm_stats(self) -> Dict[str, Any]:
        """Get swarm statistics"""
        active_agents = [a for a in self.agents.values() if a.status not in [
            AgentStatus.FAILED, AgentStatus.TERMINATED]]

        return {
            "total_agents": len(self.agents),
            "active_agents": len(active_agents),
            "idle_agents": sum(1 for a in active_agents if a.status == AgentStatus.IDLE),
            "busy_agents": sum(1 for a in active_agents if a.status == AgentStatus.BUSY),
            "total_tasks": len(self.tasks),
            "completed_tasks": sum(1 for t in self.tasks.values() if t.status == "completed"),
            "failed_tasks": sum(1 for t in self.tasks.values() if t.status == "failed"),
            "pending_tasks": sum(1 for t in self.tasks.values() if t.status == "pending"),
            "avg_agent_reputation": sum(a.reputation for a in active_agents) / len(active_agents) if active_agents else 0.0
        }
