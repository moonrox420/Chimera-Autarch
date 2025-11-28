#!/usr/bin/env python3
"""
Logistical Reasoning Evaluator for AI Agents
Comprehensive tests for planning, resource allocation, workflow management, and operational efficiency
"""

import json
import time
import uuid
import itertools
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import heapq

class PlanningType(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONSTRAINT = "constraint"
    OPTIMIZATION = "optimization"
    WORKFLOW = "workflow"
    RESOURCE_ALLOCATION = "resource_allocation"
    SCHEDULING = "scheduling"
    DEPENDENCY = "dependency"

class ResourceType(Enum):
    TIME = "time"
    MONEY = "money"
    HUMAN = "human"
    MATERIAL = "material"
    ENERGY = "energy"
    INFORMATION = "information"

@dataclass
class Resource:
    """Resource definition for allocation tests"""
    name: str
    type: ResourceType
    quantity: float
    availability: Dict[str, float] = field(default_factory=dict)  # time-based availability

@dataclass
class Task:
    """Task definition for planning tests"""
    id: str
    name: str
    duration: float
    dependencies: List[str] = field(default_factory=list)
    resources_required: Dict[ResourceType, float] = field(default_factory=dict)
    parallel_capable: bool = False
    deadline: Optional[float] = None
    priority: int = 1

@dataclass
class LogisticalTestCase:
    """Individual logistical reasoning test case"""
    id: str
    planning_type: PlanningType
    scenario: str
    description: str
    tasks: List[Task]
    resources: List[Resource]
    constraints: Dict[str, Any]
    expected_solution: Dict[str, Any]
    evaluation_criteria: Dict[str, float]
    optimal_metrics: Dict[str, float]

class LogisticalReasoningEvaluator:
    """Main logistical reasoning evaluation engine"""
    
    def __init__(self):
        self.test_suite = self._initialize_test_suite()
        
    def _initialize_test_suite(self) -> List[LogisticalTestCase]:
        """Initialize comprehensive logistical reasoning test cases"""
        return [
            # SEQUENTIAL PLANNING TESTS
            LogisticalTestCase(
                id="sequential_001",
                planning_type=PlanningType.SEQUENTIAL,
                scenario="Software Development Pipeline",
                description="Plan a sequential software development process with dependencies",
                tasks=[
                    Task("requirements", "Gather Requirements", 2.0, dependencies=[]),
                    Task("design", "System Design", 3.0, dependencies=["requirements"]),
                    Task("coding", "Implementation", 8.0, dependencies=["design"]),
                    Task("testing", "Testing", 4.0, dependencies=["coding"]),
                    Task("deployment", "Deployment", 1.0, dependencies=["testing"])
                ],
                resources=[
                    Resource("dev_time", ResourceType.TIME, 18.0),
                    Resource("budget", ResourceType.MONEY, 1000.0)
                ],
                constraints={
                    "max_duration": 20.0,
                    "max_cost": 1200.0,
                    "deadline": 15.0
                },
                expected_solution={
                    "sequence": ["requirements", "design", "coding", "testing", "deployment"],
                    "total_duration": 18.0,
                    "total_cost": 1000.0,
                    "makespan": 18.0
                },
                evaluation_criteria={
                    "feasibility": 0.3,
                    "efficiency": 0.3,
                    "constraint_satisfaction": 0.2,
                    "optimality": 0.2
                },
                optimal_metrics={
                    "makespan": 18.0,
                    "resource_utilization": 1.0,
                    "constraint_violations": 0
                }
            ),
            
            # PARALLEL PLANNING TESTS
            LogisticalTestCase(
                id="parallel_001",
                planning_type=PlanningType.PARALLEL,
                scenario="Manufacturing Assembly Line",
                description="Optimize parallel assembly line with multiple concurrent tasks",
                tasks=[
                    Task("frame", "Build Frame", 3.0, dependencies=[], parallel_capable=True),
                    Task("engine", "Install Engine", 4.0, dependencies=[], parallel_capable=True),
                    Task("wheels", "Mount Wheels", 2.0, dependencies=[], parallel_capable=True),
                    Task("interior", "Install Interior", 3.0, dependencies=[], parallel_capable=True),
                    Task("assembly", "Final Assembly", 2.0, dependencies=["frame", "engine", "wheels", "interior"])
                ],
                resources=[
                    Resource("assembly_line", ResourceType.MATERIAL, 1.0),
                    Resource("workers", ResourceType.HUMAN, 3.0),
                    Resource("time", ResourceType.TIME, 12.0)
                ],
                constraints={
                    "max_station_workers": 3,
                    "assembly_dependencies": True
                },
                expected_solution={
                    "parallel_phases": [
                        ["frame", "engine", "wheels", "interior"],
                        ["assembly"]
                    ],
                    "makespan": 9.0,
                    "worker_efficiency": 0.9
                },
                evaluation_criteria={
                    "parallel_efficiency": 0.4,
                    "resource_optimization": 0.3,
                    "dependency_respect": 0.3
                },
                optimal_metrics={
                    "makespan": 9.0,
                    "parallelism_degree": 4,
                    "resource_conflicts": 0
                }
            ),
            
            # CONSTRAINT SATISFACTION TESTS
            LogisticalTestCase(
                id="constraint_001",
                planning_type=PlanningType.CONSTRAINT,
                scenario="Project Resource Scheduling",
                description="Schedule projects with complex resource and time constraints",
                tasks=[
                    Task("proj_a", "Project A", 5.0, dependencies=[], priority=3),
                    Task("proj_b", "Project B", 3.0, dependencies=[], priority=2),
                    Task("proj_c", "Project C", 4.0, dependencies=["proj_a"], priority=1),
                    Task("proj_d", "Project D", 2.0, dependencies=["proj_b"], priority=2)
                ],
                resources=[
                    Resource("dev1", ResourceType.HUMAN, 1.0),
                    Resource("dev2", ResourceType.HUMAN, 1.0),
                    Resource("qa", ResourceType.HUMAN, 1.0)
                ],
                constraints={
                    "max_concurrent_devs": 2,
                    "qa_must_follow_dev": True,
                    "high_priority_first": True,
                    "deadline_day": 10.0
                },
                expected_solution={
                    "schedule": [
                        ("proj_a", 0, 5, "dev1"),
                        ("proj_b", 0, 3, "dev2"),
                        ("proj_c", 5, 9, "dev1"),
                        ("proj_d", 3, 5, "dev2")
                    ],
                    "makespan": 9.0,
                    "priority_optimization": True
                },
                evaluation_criteria={
                    "constraint_satisfaction": 0.4,
                    "priority_optimization": 0.3,
                    "makespan_optimization": 0.3
                },
                optimal_metrics={
                    "constraint_violations": 0,
                    "priority_score": 1.0,
                    "deadline_met": True
                }
            ),
            
            # RESOURCE ALLOCATION TESTS
            LogisticalTestCase(
                id="resource_001",
                planning_type=PlanningType.RESOURCE_ALLOCATION,
                scenario="Emergency Response Resource Distribution",
                description="Optimally distribute limited resources across multiple emergencies",
                tasks=[
                    Task("emergency_1", "Fire Response", 0.0, resources_required={ResourceType.MATERIAL: 3.0, ResourceType.HUMAN: 2.0}),
                    Task("emergency_2", "Medical Emergency", 0.0, resources_required={ResourceType.HUMAN: 3.0, ResourceType.MATERIAL: 1.0}),
                    Task("emergency_3", "Search and Rescue", 0.0, resources_required={ResourceType.HUMAN: 4.0, ResourceType.MATERIAL: 2.0})
                ],
                resources=[
                    Resource("fire_trucks", ResourceType.MATERIAL, 3.0),
                    Resource("paramedics", ResourceType.HUMAN, 5.0),
                    Resource("rescue_team", ResourceType.HUMAN, 4.0)
                ],
                constraints={
                    "total_materials": 6.0,
                    "total_humans": 9.0,
                    "max_per_emergency": 3.0
                },
                expected_solution={
                    "allocation": {
                        "emergency_1": {"fire_trucks": 2, "paramedics": 2},
                        "emergency_2": {"fire_trucks": 1, "paramedics": 3},
                        "emergency_3": {"fire_trucks": 0, "rescue_team": 4}
                    },
                    "efficiency": 1.0,
                    "coverage": 1.0
                },
                evaluation_criteria={
                    "allocation_efficiency": 0.4,
                    "coverage_completeness": 0.3,
                    "priority_optimization": 0.3
                },
                optimal_metrics={
                    "resource_utilization": 1.0,
                    "unmet_needs": 0,
                    "priority_satisfaction": 1.0
                }
            ),
            
            # WORKFLOW OPTIMIZATION TESTS
            LogisticalTestCase(
                id="workflow_001",
                planning_type=PlanningType.WORKFLOW,
                scenario="Order Fulfillment Process",
                description="Optimize multi-step order fulfillment workflow",
                tasks=[
                    Task("receive", "Receive Order", 0.1, dependencies=[]),
                    Task("verify", "Verify Payment", 0.2, dependencies=["receive"]),
                    Task("pick", "Pick Items", 0.5, dependencies=["verify"]),
                    Task("pack", "Pack Order", 0.3, dependencies=["pick"]),
                    Task("ship", "Ship Order", 0.1, dependencies=["pack"])
                ],
                resources=[
                    Resource("warehouse_time", ResourceType.TIME, 1.2),
                    Resource("staff", ResourceType.HUMAN, 2.0)
                ],
                constraints={
                    "max_order_time": 2.0,
                    "parallel_processing": False,
                    "quality_checks": True
                },
                expected_solution={
                    "workflow_sequence": ["receive", "verify", "pick", "pack", "ship"],
                    "total_time": 1.2,
                    "bottleneck": "pick",
                    "efficiency": 0.95
                },
                evaluation_criteria={
                    "throughput_optimization": 0.3,
                    "bottleneck_identification": 0.3,
                    "workflow_efficiency": 0.4
                },
                optimal_metrics={
                    "orders_per_hour": 50.0,
                    "bottleneck_utilization": 1.0,
                    "workflow_delay": 0.0
                }
            ),
            
            # SCHEDULING TESTS
            LogisticalTestCase(
                id="scheduling_001",
                planning_type=PlanningType.SCHEDULING,
                scenario="University Course Scheduling",
                description="Schedule courses with classroom, instructor, and time constraints",
                tasks=[
                    Task("cs101", "Intro to CS", 3.0, dependencies=[], priority=5),
                    Task("math201", "Calculus II", 3.0, dependencies=[], priority=4),
                    Task("eng301", "Technical Writing", 3.0, dependencies=[], priority=3),
                    Task("cs301", "Data Structures", 3.0, dependencies=["cs101"], priority=4),
                    Task("math301", "Linear Algebra", 3.0, dependencies=["math201"], priority=3)
                ],
                resources=[
                    Resource("room_1", ResourceType.MATERIAL, 1.0),
                    Resource("room_2", ResourceType.MATERIAL, 1.0),
                    Resource("prof_cs", ResourceType.HUMAN, 1.0),
                    Resource("prof_math", ResourceType.HUMAN, 1.0),
                    Resource("prof_eng", ResourceType.HUMAN, 1.0)
                ],
                constraints={
                    "max_courses_per_day": 2,
                    "no_overlapping_courses": True,
                    "prerequisite_enforcement": True,
                    "working_hours": (9, 17)
                },
                expected_solution={
                    "schedule": {
                        "cs101": ("room_1", "prof_cs", (9, 12)),
                        "math201": ("room_2", "prof_math", (9, 12)),
                        "eng301": ("room_1", "prof_eng", (13, 16)),
                        "cs301": ("room_2", "prof_cs", (13, 16)),
                        "math301": ("room_1", "prof_math", (16, 19))
                    },
                    "feasibility": True,
                    "constraint_violations": 0
                },
                evaluation_criteria={
                    "constraint_satisfaction": 0.4,
                    "resource_utilization": 0.3,
                    "schedule_efficiency": 0.3
                },
                optimal_metrics={
                    "rooms_utilized": 1.0,
                    "instructors_utilized": 1.0,
                    "time_slots_used": 6
                }
            )
        ]
    
    def evaluate_agent(self, agent_function, test_subset: List[str] = None) -> Dict[str, Any]:
        """
        Evaluate an AI agent on logistical reasoning tasks
        
        Args:
            agent_function: Function that takes a prompt and returns a response
            test_subset: Optional list of test IDs to run (default: all tests)
            
        Returns:
            Comprehensive evaluation results
        """
        if test_subset:
            tests_to_run = [t for t in self.test_suite if t.id in test_subset]
        else:
            tests_to_run = self.test_suite
            
        results = {
            "evaluation_id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "total_tests": len(tests_to_run),
            "tests_completed": 0,
            "tests_passed": 0,
            "detailed_results": [],
            "planning_type_scores": {},
            "scenario_scores": {},
            "constraint_analysis": {},
            "overall_score": 0.0
        }
        
        for test_case in tests_to_run:
            result = self._run_single_test(agent_function, test_case)
            results["detailed_results"].append(result)
            results["tests_completed"] += 1
            
            if result["passed"]:
                results["tests_passed"] += 1
                
        self._calculate_aggregate_scores(results)
        return results
    
    def _run_single_test(self, agent_function, test_case: LogisticalTestCase) -> Dict[str, Any]:
        """Run a single logistical reasoning test"""
        prompt = self._build_test_prompt(test_case)
        
        start_time = time.time()
        try:
            agent_response = agent_function(prompt)
            response_time = time.time() - start_time
            
            evaluation = self._evaluate_response(agent_response, test_case)
            
            return {
                "test_id": test_case.id,
                "planning_type": test_case.planning_type.value,
                "scenario": test_case.scenario,
                "passed": evaluation["overall_score"] >= 0.7,
                "overall_score": evaluation["overall_score"],
                "detailed_scores": evaluation["component_scores"],
                "agent_response": agent_response,
                "expected_solution": test_case.expected_solution,
                "response_time": response_time,
                "constraint_analysis": evaluation["constraint_analysis"],
                "optimization_metrics": evaluation["optimization_metrics"]
            }
            
        except Exception as e:
            return {
                "test_id": test_case.id,
                "planning_type": test_case.planning_type.value,
                "scenario": test_case.scenario,
                "passed": False,
                "overall_score": 0.0,
                "error": str(e),
                "response_time": time.time() - start_time
            }
    
    def _build_test_prompt(self, test_case: LogisticalTestCase) -> str:
        """Build test prompt for agent"""
        # Convert tasks and resources to readable format
        tasks_info = "\n".join([f"- {task.name} ({task.id}): {task.duration}h" + 
                               (f" [depends on: {', '.join(task.dependencies)}]" if task.dependencies else "")
                               for task in test_case.tasks])
        
        resources_info = "\n".join([f"- {res.name}: {res.quantity} units" for res in test_case.resources])
        
        constraints_info = "\n".join([f"- {k}: {v}" for k, v in test_case.constraints.items()])
        
        prompt = f"""
        LOGISTICAL REASONING EVALUATION TEST
        
        Scenario: {test_case.scenario}
        Planning Type: {test_case.planning_type.value.title()}
        
        Description: {test_case.description}
        
        Available Tasks:
        {tasks_info}
        
        Available Resources:
        {resources_info}
        
        Constraints:
        {constraints_info}
        
        Please provide:
        1. Your optimal solution/plan
        2. Resource allocation strategy
        3. Timeline/scheduling approach
        4. How you handle constraints
        5. Expected performance metrics
        
        Focus on demonstrating efficient planning, resource optimization, and constraint satisfaction.
        """
        return prompt
    
    def _evaluate_response(self, response: str, test_case: LogisticalTestCase) -> Dict[str, Any]:
        """Evaluate agent response against test case criteria"""
        scores = {}
        response_lower = response.lower()
        
        # Evaluate based on planning type
        if test_case.planning_type == PlanningType.SEQUENTIAL:
            scores = self._evaluate_sequential_response(response, test_case)
        elif test_case.planning_type == PlanningType.PARALLEL:
            scores = self._evaluate_parallel_response(response, test_case)
        elif test_case.planning_type == PlanningType.CONSTRAINT:
            scores = self._evaluate_constraint_response(response, test_case)
        elif test_case.planning_type == PlanningType.RESOURCE_ALLOCATION:
            scores = self._evaluate_allocation_response(response, test_case)
        elif test_case.planning_type == PlanningType.WORKFLOW:
            scores = self._evaluate_workflow_response(response, test_case)
        elif test_case.planning_type == PlanningType.SCHEDULING:
            scores = self._evaluate_scheduling_response(response, test_case)
        else:
            scores = self._evaluate_generic_logistical_response(response, test_case)
        
        # Calculate weighted overall score
        weighted_score = sum(
            scores.get(criterion, 0.0) * weight 
            for criterion, weight in test_case.evaluation_criteria.items()
        )
        
        # Additional analysis
        constraint_analysis = self._analyze_constraints(response, test_case)
        optimization_metrics = self._analyze_optimization(response, test_case)
        
        return {
            "component_scores": scores,
            "overall_score": weighted_score,
            "constraint_analysis": constraint_analysis,
            "optimization_metrics": optimization_metrics
        }
    
    def _evaluate_sequential_response(self, response: str, test_case: LogisticalTestCase) -> Dict[str, float]:
        """Evaluate sequential planning response"""
        scores = {}
        
        # Check for sequence awareness
        sequential_indicators = ["first", "then", "next", "after", "sequence", "order"]
        if any(indicator in response.lower() for indicator in sequential_indicators):
            scores["feasibility"] = 1.0
        else:
            scores["feasibility"] = 0.5
            
        # Check for efficiency considerations
        efficiency_indicators = ["optimize", "efficient", "minimize", "reduce", "improve"]
        if any(indicator in response.lower() for indicator in efficiency_indicators):
            scores["efficiency"] = 1.0
        else:
            scores["efficiency"] = 0.5
            
        # Check constraint awareness
        constraint_indicators = ["constraint", "requirement", "limit", "must", "deadline"]
        if any(indicator in response.lower() for indicator in constraint_indicators):
            scores["constraint_satisfaction"] = 1.0
        else:
            scores["constraint_satisfaction"] = 0.5
            
        # Check for optimality thinking
        if len(response.split()) > 50:  # Detailed response
            scores["optimality"] = 1.0
        elif len(response.split()) > 20:
            scores["optimality"] = 0.7
        else:
            scores["optimality"] = 0.3
            
        return scores
    
    def _evaluate_parallel_response(self, response: str, test_case: LogisticalTestCase) -> Dict[str, float]:
        """Evaluate parallel planning response"""
        scores = {}
        
        # Check for parallel awareness
        parallel_indicators = ["parallel", "concurrent", "simultaneously", "at the same time"]
        if any(indicator in response.lower() for indicator in parallel_indicators):
            scores["parallel_efficiency"] = 1.0
        else:
            scores["parallel_efficiency"] = 0.5
            
        # Check for resource optimization
        resource_indicators = ["resource", "utilize", "allocate", "capacity"]
        if any(indicator in response.lower() for indicator in resource_indicators):
            scores["resource_optimization"] = 1.0
        else:
            scores["resource_optimization"] = 0.5
            
        # Check dependency respect
        dependency_indicators = ["dependency", "before", "after", "require"]
        if any(indicator in response.lower() for indicator in dependency_indicators):
            scores["dependency_respect"] = 1.0
        else:
            scores["dependency_respect"] = 0.5
            
        return scores
    
    def _evaluate_constraint_response(self, response: str, test_case: LogisticalTestCase) -> Dict[str, float]:
        """Evaluate constraint satisfaction response"""
        scores = {}
        
        # Check constraint identification
        if "constraint" in response.lower() or "requirement" in response.lower():
            scores["constraint_satisfaction"] = 1.0
        else:
            scores["constraint_satisfaction"] = 0.5
            
        # Check priority optimization
        priority_indicators = ["priority", "important", "critical", "urgent"]
        if any(indicator in response.lower() for indicator in priority_indicators):
            scores["priority_optimization"] = 1.0
        else:
            scores["priority_optimization"] = 0.5
            
        # Check makespan optimization
        timing_indicators = ["time", "duration", "schedule", "timeline"]
        if any(indicator in response.lower() for indicator in timing_indicators):
            scores["makespan_optimization"] = 1.0
        else:
            scores["makespan_optimization"] = 0.5
            
        return scores
    
    def _evaluate_allocation_response(self, response: str, test_case: LogisticalTestCase) -> Dict[str, float]:
        """Evaluate resource allocation response"""
        scores = {}
        
        # Check allocation strategy
        allocation_indicators = ["allocate", "distribute", "assign", "distribute"]
        if any(indicator in response.lower() for indicator in allocation_indicators):
            scores["allocation_efficiency"] = 1.0
        else:
            scores["allocation_efficiency"] = 0.5
            
        # Check coverage thinking
        coverage_indicators = ["cover", "address", "handle", "response"]
        if any(indicator in response.lower() for indicator in coverage_indicators):
            scores["coverage_completeness"] = 1.0
        else:
            scores["coverage_completeness"] = 0.5
            
        # Check priority optimization
        if any(word in response.lower() for word in ["priority", "urgent", "important"]):
            scores["priority_optimization"] = 1.0
        else:
            scores["priority_optimization"] = 0.5
            
        return scores
    
    def _evaluate_workflow_response(self, response: str, test_case: LogisticalTestCase) -> Dict[str, float]:
        """Evaluate workflow optimization response"""
        scores = {}
        
        # Check throughput optimization
        throughput_indicators = ["throughput", "speed", "rate", "process"]
        if any(indicator in response.lower() for indicator in throughput_indicators):
            scores["throughput_optimization"] = 1.0
        else:
            scores["throughput_optimization"] = 0.5
            
        # Check bottleneck identification
        bottleneck_indicators = ["bottleneck", "limiting", "slowest", "constraint"]
        if any(indicator in response.lower() for indicator in bottleneck_indicators):
            scores["bottleneck_identification"] = 1.0
        else:
            scores["bottleneck_identification"] = 0.5
            
        # Check workflow efficiency
        efficiency_indicators = ["efficient", "optimize", "streamline", "improve"]
        if any(indicator in response.lower() for indicator in efficiency_indicators):
            scores["workflow_efficiency"] = 1.0
        else:
            scores["workflow_efficiency"] = 0.5
            
        return scores
    
    def _evaluate_scheduling_response(self, response: str, test_case: LogisticalTestCase) -> Dict[str, float]:
        """Evaluate scheduling response"""
        scores = {}
        
        # Check constraint satisfaction
        if "constraint" in response.lower() or "limit" in response.lower():
            scores["constraint_satisfaction"] = 1.0
        else:
            scores["constraint_satisfaction"] = 0.5
            
        # Check resource utilization
        utilization_indicators = ["utilize", "use", "allocate", "assign"]
        if any(indicator in response.lower() for indicator in utilization_indicators):
            scores["resource_utilization"] = 1.0
        else:
            scores["resource_utilization"] = 0.5
            
        # Check schedule efficiency
        if len(response.split()) > 30:  # Detailed scheduling plan
            scores["schedule_efficiency"] = 1.0
        else:
            scores["schedule_efficiency"] = 0.5
            
        return scores
    
    def _evaluate_generic_logistical_response(self, response: str, test_case: LogisticalTestCase) -> Dict[str, float]:
        """Generic evaluation for other planning types"""
        scores = {}
        
        # Basic planning indicators
        if any(word in response.lower() for word in ["plan", "schedule", "organize", "manage"]):
            scores["planning_quality"] = 0.8
        else:
            scores["planning_quality"] = 0.4
            
        # Resource awareness
        if any(word in response.lower() for word in ["resource", "time", "cost", "capacity"]):
            scores["resource_awareness"] = 0.8
        else:
            scores["resource_awareness"] = 0.4
            
        return scores
    
    def _analyze_constraints(self, response: str, test_case: LogisticalTestCase) -> Dict[str, Any]:
        """Analyze how well constraints are addressed"""
        constraint_analysis = {
            "constraints_mentioned": 0,
            "constraint_violations": 0,
            "constraint_creativity": 0.0
        }
        
        response_lower = response.lower()
        
        # Count constraint mentions
        for constraint in test_case.constraints.keys():
            if constraint.replace("_", " ") in response_lower:
                constraint_analysis["constraints_mentioned"] += 1
                
        # Check for constraint violations (simplified)
        if "deadline" in test_case.constraints and "deadline" in response_lower:
            if "cannot" in response_lower or "impossible" in response_lower:
                constraint_analysis["constraint_violations"] += 1
                
        # Creativity score based on solution complexity
        constraint_analysis["constraint_creativity"] = min(1.0, len(response.split()) / 100)
        
        return constraint_analysis
    
    def _analyze_optimization(self, response: str, test_case: LogisticalTestCase) -> Dict[str, Any]:
        """Analyze optimization approach"""
        optimization_metrics = {
            "efficiency_score": 0.0,
            "optimality_thinking": 0.0,
            "trade_off_consideration": 0.0
        }
        
        response_lower = response.lower()
        
        # Efficiency indicators
        efficiency_words = ["optimize", "efficient", "minimize", "maximize", "improve"]
        optimization_metrics["efficiency_score"] = sum(1 for word in efficiency_words if word in response_lower) / len(efficiency_words)
        
        # Optimality thinking
        optimality_words = ["optimal", "best", "ideal", "perfect", "minimum", "maximum"]
        optimization_metrics["optimality_thinking"] = sum(1 for word in optimality_words if word in response_lower) / len(optimality_words)
        
        # Trade-off consideration
        tradeoff_words = ["trade-off", "compromise", "balance", "vs", "versus", "instead"]
        optimization_metrics["trade_off_consideration"] = sum(1 for word in tradeoff_words if word in response_lower) / len(tradeoff_words)
        
        return optimization_metrics
    
    def _calculate_aggregate_scores(self, results: Dict[str, Any]) -> None:
        """Calculate aggregate scores and statistics"""
        detailed_results = results["detailed_results"]
        
        # Overall score
        total_score = sum(r["overall_score"] for r in detailed_results)
        results["overall_score"] = total_score / len(detailed_results) if detailed_results else 0.0
        
        # Planning type scores
        planning_groups = {}
        for result in detailed_results:
            planning_type = result["planning_type"]
            if planning_type not in planning_groups:
                planning_groups[planning_type] = []
            planning_groups[planning_type].append(result["overall_score"])
            
        results["planning_type_scores"] = {
            ptype: sum(scores) / len(scores)
            for ptype, scores in planning_groups.items()
        }
        
        # Scenario scores
        scenario_groups = {}
        for result in detailed_results:
            scenario = result["scenario"]
            if scenario not in scenario_groups:
                scenario_groups[scenario] = []
            scenario_groups[scenario].append(result["overall_score"])
            
        results["scenario_scores"] = {
            scenario: sum(scores) / len(scores)
            for scenario, scores in scenario_groups.items()
        }
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive evaluation report"""
        report = f"""
# LOGISTICAL REASONING EVALUATION REPORT

## Summary Statistics
- **Overall Score**: {results['overall_score']:.2f}/1.00 ({results['overall_score']*100:.1f}%)
- **Tests Passed**: {results['tests_passed']}/{results['tests_completed']} ({results['tests_passed']/results['tests_completed']*100:.1f}%)
- **Evaluation ID**: {results['evaluation_id']}

## Planning Type Performance
"""
        
        for planning_type, score in results["planning_type_scores"].items():
            report += f"- **{planning_type.replace('_', ' ').title()}**: {score:.2f}/1.00 ({score*100:.1f}%)\n"
            
        report += "\n## Scenario Performance\n"
        for scenario, score in results["scenario_scores"].items():
            report += f"- **{scenario}**: {score:.2f}/1.00 ({score*100:.1f}%)\n"
            
        report += "\n## Detailed Test Results\n"
        for result in results["detailed_results"]:
            status = "âœ… PASS" if result["passed"] else "âŒ FAIL"
            report += f"\n### {result['test_id']} - {result['planning_type'].title()} ({result['scenario']})\n"
            report += f"**Status**: {status} | **Score**: {result['overall_score']:.2f}/1.00\n"
            report += f"**Agent Response**: {result['agent_response'][:200]}...\n"
            
            if "constraint_analysis" in result:
                ca = result["constraint_analysis"]
                report += f"**Constraints Mentioned**: {ca['constraints_mentioned']}/{len(ca)} | **Constraint Creativity**: {ca['constraint_creativity']:.2f}\n"
            
        return report

# Example usage
if __name__ == "__main__":
    def mock_logistical_agent(prompt):
        if "sequential" in prompt.lower():
            return "I would approach this sequentially, completing each task in dependency order to ensure feasibility and efficiency while meeting all constraints."
        elif "parallel" in prompt.lower():
            return "For parallel processing, I would identify independent tasks that can run simultaneously to maximize efficiency while respecting dependencies."
        elif "resource" in prompt.lower():
            return "I would analyze resource constraints and allocate resources optimally to maximize coverage while respecting capacity limits."
        else:
            return "I would develop a comprehensive plan that considers all constraints and optimizes for efficiency and feasibility."
    
    # Run evaluation
    evaluator = LogisticalReasoningEvaluator()
    results = evaluator.evaluate_agent(mock_logistical_agent, test_subset=["sequential_001", "parallel_001", "resource_001"])
    
    # Generate and print report
    report = evaluator.generate_report(results)
    print(report)

