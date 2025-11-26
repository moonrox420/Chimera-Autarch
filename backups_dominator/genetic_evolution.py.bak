#!/usr/bin/env python3
"""
CHIMERA NEXUS - Genetic Algorithm Evolution
Breed multiple CHIMERA variants and evolve optimal configurations.
"""
import asyncio
import random
import time
import copy
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import logging
import json
import hashlib

logger = logging.getLogger("chimera.genetic")


@dataclass
class Genome:
    """Configuration genome for CHIMERA variant"""
    genes: Dict[str, Any]
    fitness: float = 0.0
    generation: int = 0
    id: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = hashlib.sha256(json.dumps(
                self.genes, sort_keys=True).encode()).hexdigest()[:16]

    def mutate(self, mutation_rate: float = 0.1):
        """Mutate genes"""
        for key, value in self.genes.items():
            if random.random() < mutation_rate:
                self.genes[key] = self._mutate_value(value)

    def _mutate_value(self, value: Any) -> Any:
        """Mutate a single value"""
        if isinstance(value, bool):
            return not value
        elif isinstance(value, int):
            return value + random.randint(-10, 10)
        elif isinstance(value, float):
            return value * random.uniform(0.8, 1.2)
        elif isinstance(value, str):
            return value  # Don't mutate strings
        elif isinstance(value, list):
            if value:
                idx = random.randint(0, len(value) - 1)
                value[idx] = self._mutate_value(value[idx])
            return value
        return value

    def copy(self) -> 'Genome':
        """Create a copy"""
        return Genome(
            genes=copy.deepcopy(self.genes),
            fitness=self.fitness,
            generation=self.generation
        )


@dataclass
class Individual:
    """A CHIMERA variant individual"""
    genome: Genome
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    birth_time: float = field(default_factory=time.time)
    evaluations: int = 0

    async def evaluate(self) -> float:
        """Evaluate fitness"""
        # Simulate evaluation (in real implementation, would actually run the variant)
        await asyncio.sleep(0.1)

        # Fitness function based on multiple metrics
        fitness = 0.0

        # Factor 1: Speed (lower latency is better)
        latency = self.genome.genes.get('latency_tolerance', 100)
        fitness += (1.0 - min(latency / 1000.0, 1.0)) * 0.3

        # Factor 2: Accuracy (higher confidence threshold is more accurate but slower)
        confidence = self.genome.genes.get('confidence_threshold', 0.7)
        fitness += confidence * 0.3

        # Factor 3: Resource efficiency
        resource_factor = 1.0 - self.genome.genes.get('resource_usage', 0.5)
        fitness += resource_factor * 0.2

        # Factor 4: Adaptability
        adaptability = self.genome.genes.get('adaptability', 0.5)
        fitness += adaptability * 0.2

        # Add some noise for realism
        fitness += random.gauss(0, 0.05)
        fitness = max(0.0, min(1.0, fitness))

        self.genome.fitness = fitness
        self.evaluations += 1

        return fitness


class GeneticEvolutionEngine:
    """Genetic algorithm for evolving CHIMERA configurations"""

    def __init__(self, population_size: int = 20, elite_size: int = 4):
        self.population_size = population_size
        self.elite_size = elite_size
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7

        self.population: List[Individual] = []
        self.generation = 0
        self.best_individual: Optional[Individual] = None
        self.history: List[Dict[str, Any]] = []

    def initialize_population(self):
        """Create initial random population"""
        logger.info(
            f"Initializing population of {self.population_size} individuals")

        for _ in range(self.population_size):
            genome = self._create_random_genome()
            individual = Individual(genome=genome)
            self.population.append(individual)

    def _create_random_genome(self) -> Genome:
        """Create random genome"""
        genes = {
            # Performance parameters
            'latency_tolerance': random.randint(50, 500),
            'batch_size': random.choice([8, 16, 32, 64, 128]),
            'concurrent_tasks': random.randint(1, 10),

            # Learning parameters
            'confidence_threshold': random.uniform(0.5, 0.95),
            'learning_rate': random.uniform(0.001, 0.1),
            'exploration_rate': random.uniform(0.1, 0.5),

            # Resource management
            'resource_usage': random.uniform(0.3, 0.9),
            'memory_limit': random.choice([512, 1024, 2048, 4096]),
            'cpu_limit': random.uniform(0.5, 2.0),

            # Behavior
            'adaptability': random.uniform(0.3, 0.9),
            'risk_tolerance': random.uniform(0.2, 0.8),
            'innovation_bias': random.uniform(0.3, 0.7),

            # Features
            'enable_caching': random.choice([True, False]),
            'enable_prefetch': random.choice([True, False]),
            'enable_compression': random.choice([True, False]),
        }

        return Genome(genes=genes, generation=self.generation)

    async def evolve(self, generations: int = 10) -> Individual:
        """Run genetic evolution"""
        logger.info(
            f"Starting genetic evolution for {generations} generations")

        if not self.population:
            self.initialize_population()

        for gen in range(generations):
            self.generation = gen
            logger.info(f"Generation {gen}/{generations}")

            # Evaluate fitness
            await self._evaluate_population()

            # Track best
            current_best = max(
                self.population, key=lambda ind: ind.genome.fitness)
            if not self.best_individual or current_best.genome.fitness > self.best_individual.genome.fitness:
                self.best_individual = current_best
                logger.info(
                    f"New best fitness: {current_best.genome.fitness:.4f}")

            # Record history
            self.history.append({
                'generation': gen,
                'best_fitness': current_best.genome.fitness,
                'avg_fitness': sum(ind.genome.fitness for ind in self.population) / len(self.population),
                'diversity': self._calculate_diversity()
            })

            # Create next generation
            self.population = await self._create_next_generation()

            logger.info(f"Gen {gen} - Best: {current_best.genome.fitness:.4f}, "
                        f"Avg: {self.history[-1]['avg_fitness']:.4f}, "
                        f"Diversity: {self.history[-1]['diversity']:.4f}")

        logger.info(
            f"Evolution complete. Best fitness: {self.best_individual.genome.fitness:.4f}")
        return self.best_individual

    async def _evaluate_population(self):
        """Evaluate all individuals"""
        tasks = [ind.evaluate() for ind in self.population]
        await asyncio.gather(*tasks)

    async def _create_next_generation(self) -> List[Individual]:
        """Create next generation through selection, crossover, mutation"""
        next_gen = []

        # Elitism: Keep best individuals
        sorted_pop = sorted(
            self.population, key=lambda ind: ind.genome.fitness, reverse=True)
        elite = sorted_pop[:self.elite_size]
        next_gen.extend([Individual(genome=ind.genome.copy())
                        for ind in elite])

        # Fill rest through crossover and mutation
        while len(next_gen) < self.population_size:
            # Selection
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()

            # Crossover
            if random.random() < self.crossover_rate:
                child_genome = self._crossover(parent1.genome, parent2.genome)
            else:
                child_genome = parent1.genome.copy()

            # Mutation
            child_genome.mutate(self.mutation_rate)
            child_genome.generation = self.generation + 1

            next_gen.append(Individual(genome=child_genome))

        return next_gen

    def _tournament_selection(self, tournament_size: int = 3) -> Individual:
        """Tournament selection"""
        tournament = random.sample(self.population, min(
            tournament_size, len(self.population)))
        return max(tournament, key=lambda ind: ind.genome.fitness)

    def _crossover(self, genome1: Genome, genome2: Genome) -> Genome:
        """Uniform crossover"""
        child_genes = {}

        for key in genome1.genes:
            if random.random() < 0.5:
                child_genes[key] = genome1.genes[key]
            else:
                child_genes[key] = genome2.genes[key]

        return Genome(genes=child_genes)

    def _calculate_diversity(self) -> float:
        """Calculate population diversity"""
        if len(self.population) < 2:
            return 0.0

        # Simple diversity measure: variance in fitness
        fitnesses = [ind.genome.fitness for ind in self.population]
        mean = sum(fitnesses) / len(fitnesses)
        variance = sum((f - mean) ** 2 for f in fitnesses) / len(fitnesses)

        return variance

    def get_best_genome(self) -> Optional[Genome]:
        """Get best genome found"""
        if self.best_individual:
            return self.best_individual.genome
        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get evolution statistics"""
        return {
            'generation': self.generation,
            'population_size': len(self.population),
            'best_fitness': self.best_individual.genome.fitness if self.best_individual else 0.0,
            'evolution_history': self.history[-10:],
            'best_genome': self.best_individual.genome.genes if self.best_individual else None
        }


class MultiObjectiveEvolution(GeneticEvolutionEngine):
    """Multi-objective genetic algorithm (Pareto optimization)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pareto_front: List[Individual] = []

    def _dominates(self, ind1: Individual, ind2: Individual) -> bool:
        """Check if ind1 dominates ind2 (for multi-objective)"""
        # Objectives: maximize fitness, minimize resource usage
        fitness1 = ind1.genome.fitness
        resource1 = ind1.genome.genes.get('resource_usage', 0.5)

        fitness2 = ind2.genome.fitness
        resource2 = ind2.genome.genes.get('resource_usage', 0.5)

        better_fitness = fitness1 >= fitness2
        better_resource = resource1 <= resource2

        strictly_better = fitness1 > fitness2 or resource1 < resource2

        return (better_fitness and better_resource) and strictly_better

    def _update_pareto_front(self):
        """Update Pareto front"""
        self.pareto_front = []

        for ind in self.population:
            dominated = False
            for other in self.population:
                if self._dominates(other, ind):
                    dominated = True
                    break

            if not dominated:
                self.pareto_front.append(ind)

        logger.info(f"Pareto front size: {len(self.pareto_front)}")

    async def evolve(self, generations: int = 10) -> List[Individual]:
        """Evolve and return Pareto front"""
        await super().evolve(generations)
        self._update_pareto_front()
        return self.pareto_front


# Integration with CHIMERA
class ChimeraGeneticIntegration:
    """Integration layer for CHIMERA"""

    def __init__(self, heart_node):
        self.heart = heart_node
        self.engine = GeneticEvolutionEngine(population_size=30, elite_size=5)

    async def evolve_configuration(self, generations: int = 20) -> Dict[str, Any]:
        """Evolve optimal CHIMERA configuration"""
        logger.info("Starting configuration evolution")

        best = await self.engine.evolve(generations)

        logger.info(
            f"Best configuration found: fitness={best.genome.fitness:.4f}")
        logger.info(
            f"Optimal genes: {json.dumps(best.genome.genes, indent=2)}")

        return best.genome.genes

    async def apply_genome(self, genome: Genome):
        """Apply evolved genome to CHIMERA"""
        logger.info(f"Applying genome {genome.id} to CHIMERA")

        # Apply configuration (in real implementation, would update CHIMERA config)
        config_updates = {
            'metacognitive': {
                'confidence_threshold': genome.genes.get('confidence_threshold', 0.7),
                'exploration_rate': genome.genes.get('exploration_rate', 0.3)
            },
            'performance': {
                'batch_size': genome.genes.get('batch_size', 32),
                'concurrent_tasks': genome.genes.get('concurrent_tasks', 5)
            },
            'resources': {
                'memory_limit': genome.genes.get('memory_limit', 2048),
                'cpu_limit': genome.genes.get('cpu_limit', 1.0)
            }
        }

        logger.info(
            f"Configuration applied: {json.dumps(config_updates, indent=2)}")

        return config_updates
