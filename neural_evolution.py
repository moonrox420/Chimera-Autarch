#!/usr/bin/env python3
"""
CHIMERA NEXUS - Neural Code Evolution Engine
AI that literally rewrites its own source code for performance optimization.
"""
import ast
import asyncio
import hashlib
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import subprocess
import sys

logger = logging.getLogger("chimera.neural_evolution")


@dataclass
class CodeVariant:
    """A candidate code optimization variant"""
    id: str
    original_code: str
    optimized_code: str
    optimization_type: str  # "vectorization", "caching", "parallelization", "algorithm"
    confidence: float  # 0.0 - 1.0
    estimated_speedup: float
    risk_level: str  # "low", "medium", "high"
    created_at: float = field(default_factory=time.time)
    test_results: Optional[Dict[str, Any]] = None


@dataclass
class PerformanceMetric:
    """Performance measurement for code variant"""
    execution_time: float
    memory_usage: float
    cpu_usage: float
    success_rate: float
    throughput: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class EvolutionResult:
    """Result of code evolution attempt"""
    success: bool
    variant: CodeVariant
    before_metrics: PerformanceMetric
    after_metrics: PerformanceMetric
    improvement_percent: float
    deployed: bool
    rollback_reason: Optional[str] = None


class CodeAnalyzer:
    """Analyzes code for optimization opportunities"""

    def __init__(self):
        self.optimization_patterns = {
            "loop_vectorization": self._detect_vectorizable_loops,
            "function_memoization": self._detect_cacheable_functions,
            "async_opportunities": self._detect_async_opportunities,
            "algorithm_complexity": self._detect_inefficient_algorithms,
            "redundant_operations": self._detect_redundant_code,
        }

    def analyze_function(self, source_code: str, function_name: str) -> List[Dict[str, Any]]:
        """Analyze a function for optimization opportunities"""
        try:
            tree = ast.parse(source_code)
            opportunities = []

            for pattern_name, detector in self.optimization_patterns.items():
                findings = detector(tree, function_name)
                if findings:
                    opportunities.extend(findings)

            return sorted(opportunities, key=lambda x: x['priority'], reverse=True)

        except SyntaxError as e:
            logger.error(f"Syntax error analyzing {function_name}: {e}")
            return []

    def _detect_vectorizable_loops(self, tree: ast.AST, target_func: str) -> List[Dict]:
        """Detect loops that can be vectorized with NumPy"""
        opportunities = []

        class LoopVisitor(ast.NodeVisitor):
            def __init__(self):
                self.in_target_func = False
                self.findings = []

            def visit_FunctionDef(self, node):
                if node.name == target_func:
                    self.in_target_func = True
                    self.generic_visit(node)
                    self.in_target_func = False

            def visit_AsyncFunctionDef(self, node):
                if node.name == target_func:
                    self.in_target_func = True
                    self.generic_visit(node)
                    self.in_target_func = False

            def visit_For(self, node):
                if self.in_target_func:
                    # Check if loop body has arithmetic operations
                    has_arithmetic = any(isinstance(n, (ast.BinOp, ast.UnaryOp))
                                         for n in ast.walk(node))

                    if has_arithmetic:
                        self.findings.append({
                            'type': 'loop_vectorization',
                            'line': node.lineno,
                            'description': 'Loop with arithmetic can be vectorized with NumPy',
                            'priority': 8,
                            'estimated_speedup': 5.0,
                            'risk': 'low'
                        })

                self.generic_visit(node)

        visitor = LoopVisitor()
        visitor.visit(tree)
        return visitor.findings

    def _detect_cacheable_functions(self, tree: ast.AST, target_func: str) -> List[Dict]:
        """Detect pure functions that can be memoized"""
        opportunities = []

        class CacheVisitor(ast.NodeVisitor):
            def __init__(self):
                self.findings = []

            def visit_FunctionDef(self, node):
                if node.name == target_func:
                    # Check if function has no side effects
                    has_io = any(isinstance(n, ast.Call) and
                                 isinstance(n.func, ast.Attribute) and
                                 n.func.attr in (
                                     'write', 'read', 'open', 'print')
                                 for n in ast.walk(node))

                    has_globals = any(isinstance(n, ast.Global)
                                      for n in ast.walk(node))

                    if not has_io and not has_globals:
                        self.findings.append({
                            'type': 'function_memoization',
                            'line': node.lineno,
                            'description': 'Pure function can be memoized with LRU cache',
                            'priority': 7,
                            'estimated_speedup': 3.0,
                            'risk': 'low'
                        })

                self.generic_visit(node)

        visitor = CacheVisitor()
        visitor.visit(tree)
        return visitor.findings

    def _detect_async_opportunities(self, tree: ast.AST, target_func: str) -> List[Dict]:
        """Detect synchronous I/O that can be made async"""
        opportunities = []

        class AsyncVisitor(ast.NodeVisitor):
            def __init__(self):
                self.in_target_func = False
                self.findings = []

            def visit_FunctionDef(self, node):
                # Only analyze sync functions (async already optimized)
                if node.name == target_func:
                    self.in_target_func = True
                    self.generic_visit(node)
                    self.in_target_func = False

            def visit_Call(self, node):
                if self.in_target_func:
                    # Detect blocking I/O operations
                    blocking_ops = ['sleep', 'read',
                                    'write', 'get', 'post', 'request']

                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in blocking_ops:
                            self.findings.append({
                                'type': 'async_opportunities',
                                'line': node.lineno,
                                'description': f'Blocking call to {node.func.attr} can be async',
                                'priority': 9,
                                'estimated_speedup': 10.0,
                                'risk': 'medium'
                            })

                self.generic_visit(node)

        visitor = AsyncVisitor()
        visitor.visit(tree)
        return visitor.findings

    def _detect_inefficient_algorithms(self, tree: ast.AST, target_func: str) -> List[Dict]:
        """Detect nested loops and inefficient algorithms"""
        opportunities = []

        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.in_target_func = False
                self.loop_depth = 0
                self.findings = []

            def visit_FunctionDef(self, node):
                if node.name == target_func:
                    self.in_target_func = True
                    self.generic_visit(node)
                    self.in_target_func = False

            def visit_For(self, node):
                if self.in_target_func:
                    self.loop_depth += 1

                    if self.loop_depth >= 2:
                        self.findings.append({
                            'type': 'algorithm_complexity',
                            'line': node.lineno,
                            'description': f'Nested loop depth {self.loop_depth} - O(n^{self.loop_depth}) complexity',
                            'priority': 10,
                            'estimated_speedup': self.loop_depth * 5.0,
                            'risk': 'high'
                        })

                    self.generic_visit(node)
                    self.loop_depth -= 1
                else:
                    self.generic_visit(node)

        visitor = ComplexityVisitor()
        visitor.visit(tree)
        return visitor.findings

    def _detect_redundant_code(self, tree: ast.AST, target_func: str) -> List[Dict]:
        """Detect duplicate code that can be refactored"""
        opportunities = []

        class RedundancyVisitor(ast.NodeVisitor):
            def __init__(self):
                self.in_target_func = False
                self.expressions = []
                self.findings = []

            def visit_FunctionDef(self, node):
                if node.name == target_func:
                    self.in_target_func = True
                    self.generic_visit(node)
                    self.in_target_func = False

                    # Check for duplicate expressions
                    seen = {}
                    for expr, line in self.expressions:
                        if expr in seen:
                            self.findings.append({
                                'type': 'redundant_operations',
                                'line': line,
                                'description': f'Duplicate expression also at line {seen[expr]}',
                                'priority': 6,
                                'estimated_speedup': 1.5,
                                'risk': 'low'
                            })
                        else:
                            seen[expr] = line

            def visit_Assign(self, node):
                if self.in_target_func and isinstance(node.value, ast.BinOp):
                    expr = ast.unparse(node.value)
                    self.expressions.append((expr, node.lineno))

                self.generic_visit(node)

        visitor = RedundancyVisitor()
        visitor.visit(tree)
        return visitor.findings


class CodeOptimizer:
    """Generates optimized code variants"""

    def __init__(self, analyzer: CodeAnalyzer):
        self.analyzer = analyzer

    def generate_variant(self, source_code: str, function_name: str,
                         opportunity: Dict[str, Any]) -> Optional[CodeVariant]:
        """Generate optimized code variant for a specific opportunity"""

        opt_type = opportunity['type']

        generators = {
            'loop_vectorization': self._vectorize_loop,
            'function_memoization': self._add_memoization,
            'async_opportunities': self._convert_to_async,
            'algorithm_complexity': self._optimize_algorithm,
            'redundant_operations': self._eliminate_redundancy,
        }

        generator = generators.get(opt_type)
        if not generator:
            return None

        try:
            optimized_code = generator(source_code, function_name, opportunity)

            if optimized_code and optimized_code != source_code:
                variant_id = hashlib.sha256(
                    optimized_code.encode()).hexdigest()[:16]

                return CodeVariant(
                    id=variant_id,
                    original_code=source_code,
                    optimized_code=optimized_code,
                    optimization_type=opt_type,
                    confidence=self._calculate_confidence(opportunity),
                    estimated_speedup=opportunity.get(
                        'estimated_speedup', 1.5),
                    risk_level=opportunity.get('risk', 'medium')
                )

        except Exception as e:
            logger.error(f"Failed to generate variant for {opt_type}: {e}")

        return None

    def _vectorize_loop(self, source: str, func_name: str, opp: Dict) -> str:
        """Convert loop to NumPy vectorized operation"""
        # This is a simplified example - real implementation would use AST transformation
        tree = ast.parse(source)

        class VectorizeTransformer(ast.NodeTransformer):
            def __init__(self, target_func: str):
                self.target_func = target_func
                self.in_target = False

            def visit_FunctionDef(self, node):
                if node.name == self.target_func:
                    self.in_target = True
                    # Add numpy import if not present
                    result = self.generic_visit(node)
                    self.in_target = False
                    return result
                return node

            def visit_For(self, node):
                if self.in_target:
                    # Convert simple arithmetic loops to numpy operations
                    # This is a placeholder - real implementation would be more sophisticated
                    return node
                return node

        transformer = VectorizeTransformer(func_name)
        new_tree = transformer.visit(tree)

        return ast.unparse(new_tree)

    def _add_memoization(self, source: str, func_name: str, opp: Dict) -> str:
        """Add LRU cache decorator to function"""
        tree = ast.parse(source)

        class MemoizeTransformer(ast.NodeTransformer):
            def __init__(self, target_func: str):
                self.target_func = target_func

            def visit_FunctionDef(self, node):
                if node.name == self.target_func:
                    # Add @lru_cache decorator
                    cache_decorator = ast.Name(id='lru_cache', ctx=ast.Load())
                    decorator = ast.Call(
                        func=cache_decorator,
                        args=[ast.Constant(value=128)],
                        keywords=[]
                    )
                    node.decorator_list.insert(0, decorator)

                return node

        transformer = MemoizeTransformer(func_name)
        new_tree = transformer.visit(tree)

        # Add functools import
        optimized = "from functools import lru_cache\n\n" + \
            ast.unparse(new_tree)
        return optimized

    def _convert_to_async(self, source: str, func_name: str, opp: Dict) -> str:
        """Convert synchronous function to async"""
        tree = ast.parse(source)

        class AsyncTransformer(ast.NodeTransformer):
            def __init__(self, target_func: str):
                self.target_func = target_func

            def visit_FunctionDef(self, node):
                if node.name == self.target_func:
                    # Convert to async function
                    async_node = ast.AsyncFunctionDef(
                        name=node.name,
                        args=node.args,
                        body=node.body,
                        decorator_list=node.decorator_list,
                        returns=node.returns,
                        type_comment=node.type_comment
                    )
                    return async_node
                return node

            def visit_Call(self, node):
                # Add await to blocking calls
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['sleep', 'read', 'write', 'get', 'post']:
                        return ast.Await(value=node)
                return node

        transformer = AsyncTransformer(func_name)
        new_tree = transformer.visit(tree)

        return ast.unparse(new_tree)

    def _optimize_algorithm(self, source: str, func_name: str, opp: Dict) -> str:
        """Optimize algorithmic complexity (placeholder)"""
        # Real implementation would use pattern matching and algorithm databases
        # For now, just return source with a comment
        return f"# TODO: Optimize algorithm complexity\n{source}"

    def _eliminate_redundancy(self, source: str, func_name: str, opp: Dict) -> str:
        """Remove redundant code (placeholder)"""
        # Real implementation would use CSE (Common Subexpression Elimination)
        return source

    def _calculate_confidence(self, opportunity: Dict) -> float:
        """Calculate confidence score for optimization"""
        priority = opportunity.get('priority', 5)
        risk = opportunity.get('risk', 'medium')

        risk_penalty = {'low': 0.0, 'medium': 0.1, 'high': 0.3}.get(risk, 0.2)

        confidence = (priority / 10.0) - risk_penalty
        return max(0.3, min(0.95, confidence))


class PerformanceTester:
    """A/B tests code variants"""

    def __init__(self):
        self.test_iterations = 100
        self.warmup_iterations = 10

    async def benchmark_variant(self, code: str, function_name: str,
                                test_inputs: List[Any]) -> PerformanceMetric:
        """Benchmark a code variant"""

        # Create temporary module
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            # Import and test
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "test_module", temp_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            func = getattr(module, function_name)

            # Warmup
            for _ in range(self.warmup_iterations):
                for test_input in test_inputs:
                    try:
                        if asyncio.iscoroutinefunction(func):
                            await func(**test_input)
                        else:
                            func(**test_input)
                    except:
                        pass

            # Actual benchmark
            timings = []
            successes = 0

            for _ in range(self.test_iterations):
                for test_input in test_inputs:
                    start = time.perf_counter()
                    try:
                        if asyncio.iscoroutinefunction(func):
                            await func(**test_input)
                        else:
                            func(**test_input)
                        successes += 1
                    except Exception as e:
                        logger.warning(f"Test failed: {e}")

                    timings.append(time.perf_counter() - start)

            avg_time = sum(timings) / len(timings) if timings else float('inf')
            success_rate = successes / \
                (self.test_iterations * len(test_inputs))

            return PerformanceMetric(
                execution_time=avg_time,
                memory_usage=0.0,  # Placeholder
                cpu_usage=0.0,  # Placeholder
                success_rate=success_rate,
                throughput=1.0 / avg_time if avg_time > 0 else 0.0
            )

        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def ab_test(self, original: str, optimized: str, function_name: str,
                      test_inputs: List[Any]) -> Tuple[PerformanceMetric, PerformanceMetric]:
        """A/B test original vs optimized code"""

        logger.info(f"Starting A/B test for {function_name}")

        original_metrics = await self.benchmark_variant(original, function_name, test_inputs)
        optimized_metrics = await self.benchmark_variant(optimized, function_name, test_inputs)

        return original_metrics, optimized_metrics


class NeuralEvolutionEngine:
    """Main engine for neural code evolution"""

    def __init__(self, target_file: str = "chimera_autarch.py"):
        self.target_file = Path(target_file)
        self.analyzer = CodeAnalyzer()
        self.optimizer = CodeOptimizer(self.analyzer)
        self.tester = PerformanceTester()
        self.evolution_history: List[EvolutionResult] = []
        self.active_variants: Dict[str, CodeVariant] = {}

    async def evolve_function(self, function_name: str,
                              test_inputs: List[Dict[str, Any]]) -> Optional[EvolutionResult]:
        """Evolve a single function"""

        if not self.target_file.exists():
            logger.error(f"Target file {self.target_file} not found")
            return None

        source_code = self.target_file.read_text()

        # Analyze for opportunities
        opportunities = self.analyzer.analyze_function(
            source_code, function_name)

        if not opportunities:
            logger.info(
                f"No optimization opportunities found for {function_name}")
            return None

        logger.info(
            f"Found {len(opportunities)} optimization opportunities for {function_name}")

        # Generate variants for top opportunity
        best_opportunity = opportunities[0]
        variant = self.optimizer.generate_variant(
            source_code, function_name, best_opportunity)

        if not variant:
            logger.warning("Failed to generate variant")
            return None

        # A/B test
        try:
            original_metrics, optimized_metrics = await self.tester.ab_test(
                variant.original_code,
                variant.optimized_code,
                function_name,
                test_inputs
            )

            improvement = ((original_metrics.execution_time - optimized_metrics.execution_time)
                           / original_metrics.execution_time * 100)

            # Deploy if significant improvement and high success rate
            should_deploy = (
                improvement > 10.0 and  # At least 10% faster
                optimized_metrics.success_rate >= 0.95 and  # 95%+ success rate
                variant.risk_level in ['low', 'medium']  # Not high risk
            )

            result = EvolutionResult(
                success=should_deploy,
                variant=variant,
                before_metrics=original_metrics,
                after_metrics=optimized_metrics,
                improvement_percent=improvement,
                deployed=should_deploy
            )

            if should_deploy:
                self._deploy_variant(variant)
                logger.info(
                    f"✅ Deployed optimization: {improvement:.1f}% improvement")
            else:
                reason = self._get_rejection_reason(
                    improvement, optimized_metrics, variant)
                result.rollback_reason = reason
                logger.info(f"❌ Rejected variant: {reason}")

            self.evolution_history.append(result)
            return result

        except Exception as e:
            logger.error(f"Evolution failed: {e}")
            return None

    def _deploy_variant(self, variant: CodeVariant):
        """Deploy optimized code to production"""
        # Backup original
        backup_path = self.target_file.with_suffix('.py.backup')
        shutil.copy(self.target_file, backup_path)

        # Write optimized code
        self.target_file.write_text(variant.optimized_code)

        logger.info(f"Deployed variant {variant.id} (backup: {backup_path})")

    def _get_rejection_reason(self, improvement: float, metrics: PerformanceMetric,
                              variant: CodeVariant) -> str:
        """Get human-readable rejection reason"""
        if improvement < 10.0:
            return f"Insufficient improvement ({improvement:.1f}% < 10%)"
        if metrics.success_rate < 0.95:
            return f"Low success rate ({metrics.success_rate:.1%})"
        if variant.risk_level == 'high':
            return "High risk optimization"
        return "Unknown reason"

    async def continuous_evolution(self, target_functions: List[str],
                                   test_inputs_map: Dict[str, List[Dict]],
                                   interval: int = 3600):
        """Continuously evolve code"""
        logger.info("Starting continuous neural evolution")

        while True:
            for func_name in target_functions:
                test_inputs = test_inputs_map.get(func_name, [{}])

                try:
                    result = await self.evolve_function(func_name, test_inputs)
                    if result and result.deployed:
                        logger.info(
                            f"🧠 Evolved {func_name}: {result.improvement_percent:.1f}% faster")

                except Exception as e:
                    logger.error(f"Evolution error for {func_name}: {e}")

            logger.info(f"Evolution cycle complete. Sleeping {interval}s")
            await asyncio.sleep(interval)

    def get_evolution_stats(self) -> Dict[str, Any]:
        """Get evolution statistics"""
        if not self.evolution_history:
            return {'total_evolutions': 0}

        deployed = [r for r in self.evolution_history if r.deployed]
        avg_improvement = sum(
            r.improvement_percent for r in deployed) / len(deployed) if deployed else 0.0

        return {
            'total_evolutions': len(self.evolution_history),
            'successful_deployments': len(deployed),
            'average_improvement': avg_improvement,
            'total_speedup': sum(r.improvement_percent for r in deployed),
            'recent_evolutions': [
                {
                    'variant_id': r.variant.id,
                    'optimization': r.variant.optimization_type,
                    'improvement': r.improvement_percent,
                    'deployed': r.deployed
                }
                for r in self.evolution_history[-10:]
            ]
        }
