#!/usr/bin/env python3
"""
CHIMERA NEXUS - Blockchain Audit Trail
Immutable cryptographic audit log of all AI decisions and evolutions.
"""
import asyncio
import hashlib
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging

logger = logging.getLogger("chimera.blockchain")


@dataclass
class Transaction:
    """A single audit transaction"""
    tx_id: str
    tx_type: str  # "evolution", "decision", "deployment", "failure", "learning"
    actor: str  # Who/what made this change
    action: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def serialize(self) -> str:
        """Serialize for hashing"""
        data = self.to_dict()
        return json.dumps(data, sort_keys=True)


@dataclass
class Block:
    """A block in the audit chain"""
    index: int
    transactions: List[Transaction]
    previous_hash: str
    timestamp: float
    nonce: int = 0
    hash: str = ""
    merkle_root: str = ""

    def __post_init__(self):
        if not self.merkle_root:
            self.merkle_root = self.calculate_merkle_root()
        if not self.hash:
            self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate block hash"""
        block_string = f"{self.index}{self.previous_hash}{self.timestamp}{self.merkle_root}{self.nonce}"
        return hashlib.sha3_256(block_string.encode()).hexdigest()

    def calculate_merkle_root(self) -> str:
        """Calculate Merkle tree root of transactions"""
        if not self.transactions:
            return hashlib.sha3_256(b"").hexdigest()

        # Hash all transactions
        tx_hashes = [
            hashlib.sha3_256(tx.serialize().encode()).hexdigest()
            for tx in self.transactions
        ]

        # Build Merkle tree
        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 != 0:
                tx_hashes.append(tx_hashes[-1])  # Duplicate last if odd

            tx_hashes = [
                hashlib.sha3_256(
                    (tx_hashes[i] + tx_hashes[i+1]).encode()).hexdigest()
                for i in range(0, len(tx_hashes), 2)
            ]

        return tx_hashes[0]

    def mine(self, difficulty: int = 2):
        """Proof of work mining"""
        target = "0" * difficulty

        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()

        logger.debug(
            f"Block {self.index} mined: {self.hash[:16]}... (nonce: {self.nonce})")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'index': self.index,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'hash': self.hash,
            'merkle_root': self.merkle_root
        }


class Blockchain:
    """Immutable audit trail blockchain"""

    def __init__(self, difficulty: int = 2, block_size: int = 10):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.difficulty = difficulty
        self.block_size = block_size

        # Create genesis block
        self._create_genesis_block()

    def _create_genesis_block(self):
        """Create the first block"""
        genesis_tx = Transaction(
            tx_id="genesis",
            tx_type="system",
            actor="CHIMERA_NEXUS",
            action="initialize",
            data={"message": "Genesis block - CHIMERA audit trail begins"},
            metadata={"version": "1.0.0"}
        )

        genesis = Block(
            index=0,
            transactions=[genesis_tx],
            previous_hash="0" * 64,
            timestamp=time.time()
        )

        genesis.mine(self.difficulty)
        self.chain.append(genesis)

        logger.info(f"Genesis block created: {genesis.hash[:16]}...")

    def get_latest_block(self) -> Block:
        """Get the most recent block"""
        return self.chain[-1]

    async def add_transaction(self, transaction: Transaction) -> str:
        """Add transaction to pending pool"""
        self.pending_transactions.append(transaction)

        logger.debug(
            f"Transaction added: {transaction.tx_type} by {transaction.actor}")

        # Auto-mine if block is full
        if len(self.pending_transactions) >= self.block_size:
            await self.mine_pending_transactions()

        return transaction.tx_id

    async def mine_pending_transactions(self) -> Optional[Block]:
        """Mine pending transactions into a new block"""
        if not self.pending_transactions:
            logger.warning("No pending transactions to mine")
            return None

        # Create new block
        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions[:self.block_size],
            previous_hash=self.get_latest_block().hash,
            timestamp=time.time()
        )

        # Mine the block
        logger.info(
            f"Mining block {new_block.index} with {len(new_block.transactions)} transactions...")
        start = time.time()
        new_block.mine(self.difficulty)
        mining_time = time.time() - start

        # Add to chain
        self.chain.append(new_block)

        # Remove mined transactions
        self.pending_transactions = self.pending_transactions[self.block_size:]

        logger.info(
            f"Block {new_block.index} mined in {mining_time:.2f}s: {new_block.hash[:16]}...")

        return new_block

    def is_chain_valid(self) -> bool:
        """Validate entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # Check hash
            if current_block.hash != current_block.calculate_hash():
                logger.error(f"Block {i} hash invalid")
                return False

            # Check previous hash link
            if current_block.previous_hash != previous_block.hash:
                logger.error(f"Block {i} previous_hash invalid")
                return False

            # Check merkle root
            if current_block.merkle_root != current_block.calculate_merkle_root():
                logger.error(f"Block {i} merkle_root invalid")
                return False

            # Check proof of work
            if not current_block.hash.startswith("0" * self.difficulty):
                logger.error(f"Block {i} proof of work invalid")
                return False

        return True

    def get_transaction_history(self, tx_type: Optional[str] = None,
                                actor: Optional[str] = None,
                                limit: int = 100) -> List[Transaction]:
        """Query transaction history"""
        transactions = []

        for block in reversed(self.chain):
            for tx in reversed(block.transactions):
                if tx_type and tx.tx_type != tx_type:
                    continue
                if actor and tx.actor != actor:
                    continue

                transactions.append(tx)

                if len(transactions) >= limit:
                    return transactions

        return transactions

    def get_block_by_hash(self, block_hash: str) -> Optional[Block]:
        """Get block by hash"""
        for block in self.chain:
            if block.hash == block_hash:
                return block
        return None

    def get_transaction_by_id(self, tx_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        for block in self.chain:
            for tx in block.transactions:
                if tx.tx_id == tx_id:
                    return tx
        return None

    async def save_to_disk(self, filepath: str = "blockchain_audit.json"):
        """Save blockchain to disk"""
        data = {
            'difficulty': self.difficulty,
            'block_size': self.block_size,
            'chain': [block.to_dict() for block in self.chain],
            'pending': [tx.to_dict() for tx in self.pending_transactions]
        }

        path = Path(filepath)
        path.write_text(json.dumps(data, indent=2))

        logger.info(
            f"Blockchain saved to {filepath} ({len(self.chain)} blocks)")

    @classmethod
    async def load_from_disk(cls, filepath: str = "blockchain_audit.json") -> 'Blockchain':
        """Load blockchain from disk"""
        path = Path(filepath)

        if not path.exists():
            logger.warning(
                f"Blockchain file {filepath} not found, creating new")
            return cls()

        data = json.loads(path.read_text())

        blockchain = cls(
            difficulty=data['difficulty'],
            block_size=data['block_size']
        )

        # Clear genesis block (will be reconstructed)
        blockchain.chain = []

        # Reconstruct blocks
        for block_data in data['chain']:
            transactions = [
                Transaction(**tx_data)
                for tx_data in block_data['transactions']
            ]

            block = Block(
                index=block_data['index'],
                transactions=transactions,
                previous_hash=block_data['previous_hash'],
                timestamp=block_data['timestamp'],
                nonce=block_data['nonce'],
                hash=block_data['hash'],
                merkle_root=block_data['merkle_root']
            )

            blockchain.chain.append(block)

        # Reconstruct pending
        blockchain.pending_transactions = [
            Transaction(**tx_data)
            for tx_data in data['pending']
        ]

        logger.info(
            f"Blockchain loaded from {filepath} ({len(blockchain.chain)} blocks)")

        # Validate
        if not blockchain.is_chain_valid():
            logger.error("Loaded blockchain is INVALID!")

        return blockchain

    def get_stats(self) -> Dict[str, Any]:
        """Get blockchain statistics"""
        total_transactions = sum(len(block.transactions)
                                 for block in self.chain)

        tx_by_type = {}
        for block in self.chain:
            for tx in block.transactions:
                tx_by_type[tx.tx_type] = tx_by_type.get(tx.tx_type, 0) + 1

        return {
            'total_blocks': len(self.chain),
            'total_transactions': total_transactions,
            'pending_transactions': len(self.pending_transactions),
            'difficulty': self.difficulty,
            'latest_block_hash': self.get_latest_block().hash[:16] + "...",
            'chain_valid': self.is_chain_valid(),
            'transactions_by_type': tx_by_type,
            'blockchain_size_mb': len(json.dumps([b.to_dict() for b in self.chain])) / 1024 / 1024
        }


class AuditLogger:
    """High-level audit logging interface"""

    def __init__(self, blockchain: Optional[Blockchain] = None):
        self.blockchain = blockchain or Blockchain()
        self.auto_mine_interval = 60  # Mine every 60 seconds
        self._mining_task = None

    async def start(self):
        """Start automatic mining"""
        self._mining_task = asyncio.create_task(self._auto_mine())
        logger.info("Audit logger started with automatic mining")

    async def stop(self):
        """Stop automatic mining"""
        if self._mining_task:
            self._mining_task.cancel()
            try:
                await self._mining_task
            except asyncio.CancelledError:
                pass

        # Mine any remaining pending transactions
        if self.blockchain.pending_transactions:
            await self.blockchain.mine_pending_transactions()

        logger.info("Audit logger stopped")

    async def _auto_mine(self):
        """Automatically mine pending transactions"""
        while True:
            await asyncio.sleep(self.auto_mine_interval)

            if self.blockchain.pending_transactions:
                await self.blockchain.mine_pending_transactions()

    async def log_evolution(self, topic: str, fix: str, improvement: float) -> str:
        """Log a code evolution"""
        tx = Transaction(
            tx_id=self._generate_tx_id("EV"),
            tx_type="evolution",
            actor="NeuralEvolutionEngine",
            action="code_optimization",
            data={
                'topic': topic,
                'fix': fix,
                'improvement_percent': improvement
            },
            metadata={'category': 'self_improvement'}
        )

        return await self.blockchain.add_transaction(tx)

    async def log_decision(self, decision_type: str, chosen: str,
                           confidence: float, personality: str) -> str:
        """Log an AI decision"""
        tx = Transaction(
            tx_id=self._generate_tx_id("DEC"),
            tx_type="decision",
            actor="PersonalityEngine",
            action=decision_type,
            data={
                'chosen_option': chosen,
                'confidence': confidence,
                'personality_mode': personality
            },
            metadata={'category': 'decision_making'}
        )

        return await self.blockchain.add_transaction(tx)

    async def log_deployment(self, component: str, version: str,
                             nodes: List[str]) -> str:
        """Log a deployment"""
        tx = Transaction(
            tx_id=self._generate_tx_id("DEP"),
            tx_type="deployment",
            actor="CloudOrchestrator",
            action="deploy_component",
            data={
                'component': component,
                'version': version,
                'target_nodes': nodes
            },
            metadata={'category': 'deployment'}
        )

        return await self.blockchain.add_transaction(tx)

    async def log_failure(self, component: str, error: str,
                          recovery_action: str) -> str:
        """Log a failure and recovery"""
        tx = Transaction(
            tx_id=self._generate_tx_id("FAIL"),
            tx_type="failure",
            actor="MetacognitiveEngine",
            action="failure_recovery",
            data={
                'failed_component': component,
                'error_message': error,
                'recovery_action': recovery_action
            },
            metadata={'category': 'incident', 'severity': 'high'}
        )

        return await self.blockchain.add_transaction(tx)

    async def log_learning(self, topic: str, rounds: int,
                           improvement: float) -> str:
        """Log federated learning"""
        tx = Transaction(
            tx_id=self._generate_tx_id("LEARN"),
            tx_type="learning",
            actor="FederatedLearningEngine",
            action="federated_training",
            data={
                'topic': topic,
                'training_rounds': rounds,
                'improvement': improvement
            },
            metadata={'category': 'machine_learning'}
        )

        return await self.blockchain.add_transaction(tx)

    def _generate_tx_id(self, prefix: str) -> str:
        """Generate unique transaction ID"""
        timestamp = int(time.time() * 1000)
        random_suffix = hashlib.sha256(str(timestamp).encode()).hexdigest()[:8]
        return f"{prefix}_{timestamp}_{random_suffix}"

    async def get_audit_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate audit report"""
        cutoff = time.time() - (hours * 3600)

        recent_txs = [
            tx for block in self.blockchain.chain
            for tx in block.transactions
            if tx.timestamp >= cutoff
        ]

        tx_by_type = {}
        tx_by_actor = {}

        for tx in recent_txs:
            tx_by_type[tx.tx_type] = tx_by_type.get(tx.tx_type, 0) + 1
            tx_by_actor[tx.actor] = tx_by_actor.get(tx.actor, 0) + 1

        return {
            'period_hours': hours,
            'total_transactions': len(recent_txs),
            'transactions_by_type': tx_by_type,
            'transactions_by_actor': tx_by_actor,
            'blockchain_stats': self.blockchain.get_stats(),
            'recent_events': [
                {
                    'type': tx.tx_type,
                    'actor': tx.actor,
                    'action': tx.action,
                    'timestamp': tx.timestamp
                }
                for tx in recent_txs[-20:]
            ]
        }


# Integration with CHIMERA
class ChimeraBlockchainIntegration:
    """Integration layer for CHIMERA"""

    def __init__(self, heart_node):
        self.heart = heart_node
        self.audit_logger = AuditLogger()

    async def start(self):
        """Start blockchain audit system"""
        await self.audit_logger.start()
        logger.info("CHIMERA blockchain audit system started")

    async def stop(self):
        """Stop and save blockchain"""
        await self.audit_logger.stop()
        await self.audit_logger.blockchain.save_to_disk()
        logger.info("CHIMERA blockchain audit system stopped")

    async def audit_tool_execution(self, tool_name: str, success: bool,
                                   latency: float):
        """Audit a tool execution"""
        tx = Transaction(
            tx_id=f"TOOL_{int(time.time()*1000)}",
            tx_type="tool_execution",
            actor=tool_name,
            action="execute",
            data={
                'success': success,
                'latency_ms': latency * 1000
            }
        )

        await self.audit_logger.blockchain.add_transaction(tx)

