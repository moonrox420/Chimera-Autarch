#!/usr/bin/env python3
"""
Complete AI Agent Evaluation Framework Demonstration
Shows all evaluators working together with comprehensive testing
"""

import time
import json
from comprehensive_agent_evaluator import ComprehensiveAgentEvaluator, EvaluationConfig, AgentProfile

# Import all evaluators
from cognitive_reasoning_evaluator import CognitiveReasoningEvaluator
from logistical_reasoning_evaluator import LogisticalReasoningEvaluator  
from system_prompt_evaluator import SystemPromptEvaluator

def create_test_agents():
    """Create various test agents to demonstrate evaluation capabilities"""
    
    def logical_agent(prompt):
        """Agent focused on logical reasoning"""
        if "deductive" in prompt.lower() or "all" in prompt.lower() and "therefore" in prompt.lower():
            return "Therefore, the conclusion follows logically from the given premises using deductive reasoning principles."
        elif "inductive" in prompt.lower():
            return "Based on the pattern observed in the data, it is likely that this generalization holds, though we cannot be completely certain without more evidence."
        elif "abductive" in prompt.lower():
            return "The most probable explanation for this observation is that it was caused by the most likely underlying factor."
        elif "syllogism" in prompt.lower():
            return "This is a categorical syllogism. We have a universal premise, a particular premise, but no valid conclusion can be drawn about the relationship between A and C."
        else:
            return "I would approach this by analyzing the logical structure, identifying premises, and applying appropriate reasoning methods to reach a sound conclusion."
    
    def planning_agent(prompt):
        """Agent focused on planning and logistics"""
        if "sequential" in prompt.lower():
            return "I would plan this sequentially, completing each dependent task in order to ensure proper workflow and meet all constraints."
        elif "parallel" in prompt.lower():
            return "I would identify independent tasks that can run simultaneously to maximize efficiency while respecting dependencies and resource constraints."
        elif "resource" in prompt.lower():
            return "I would analyze resource constraints and allocate them optimally to maximize coverage while respecting capacity limits and priority requirements."
        elif "workflow" in prompt.lower():
            return "I would optimize the workflow by identifying bottlenecks, improving throughput, and ensuring efficient resource utilization throughout the process."
        else:
            return "I would develop a comprehensive plan that considers all constraints, optimizes resource allocation, and ensures efficient execution."
    
    def communication_agent(prompt):
        """Agent focused on communication and instruction following"""
        if "code review" in prompt.lower():
            return "I would carefully review the code for bugs, security issues, and performance problems, providing specific feedback with examples while maintaining a professional tone."
        elif "customer service" in prompt.lower():
            return "Hello! I'm here to help you. Let me ask some clarifying questions to better understand your situation and provide the most helpful solution."
        elif "data analysis" in prompt.lower():
            return "I'll analyze this data using appropriate statistical methods. First, let me examine data quality, then apply relevant techniques to extract meaningful insights."
        else:
            return "I'll help you with this task by following a systematic approach and providing clear, actionable guidance based on your specific requirements."
    
    def creative_agent(prompt):
        """Creative problem-solving agent"""
        return "I approach problems by thinking outside the box, considering multiple perspectives, and finding innovative solutions that others might overlook."
    
    def analytical_agent(prompt):
        """Analytical thinking agent"""
        return "I break down complex problems systematically, analyze each component thoroughly, and synthesize insights to provide data-driven recommendations."
    
    return {
        "logical_agent": logical_agent,
        "planning_agent": planning_agent, 
        "communication_agent": communication_agent,
        "creative_agent": creative_agent,
        "analytical_agent": analytical_agent
    }

def run_comprehensive_demo():
    """Run comprehensive demonstration of the evaluation framework"""
    
    print("🤖 COMPREHENSIVE AI AGENT EVALUATION FRAMEWORK DEMO")
    print("=" * 70)
    
    # Create test agents
    agents = create_test_agents()
    
    # Create comprehensive evaluator with balanced weights
    config = EvaluationConfig(
        cognitive_tests=["deductive_001", "inductive_001", "abductive_001"],
        logistical_tests=["sequential_001", "parallel_001", "resource_001"],
        prompt_scenarios=["instruction_001", "conversation_001", "role_001"],
        evaluation_weights={"cognitive": 0.33, "logistical": 0.33, "prompt": 0.34},
        enable_detailed_reporting=True,
        enable_recommendations=True,
        save_results=True
    )
    
    evaluator = ComprehensiveAgentEvaluator(config)
    
    # Test each agent
    all_results = {}
    
    for agent_name, agent_function in agents.items():
        print(f"\n🧪 Testing {agent_name.upper()}")
        print("-" * 50)
        
        # Create agent profile
        agent_profile = AgentProfile(
            name=agent_name.replace("_", " ").title(),
            description=f"Test agent specializing in {agent_name.split('_')[0]} capabilities",
            version="1.0.0",
            agent_type="test_specialist",
            capabilities=["logical_reasoning", "planning", "communication", "problem_solving"]
        )
        
        # Run evaluation
        start_time = time.time()
        results = evaluator.evaluate_agent(agent_function, agent_profile)
        end_time = time.time()
        
        all_results[agent_name] = results
        
        # Print quick summary
        scores = results["overall_scores"]
        print(f"Overall Score: {scores['composite_score']:.2f}/1.00 ({scores['composite_score']*100:.1f}%)")
        print(f"Grade: {scores['grade']}")
        print(f"Verdict: {results['final_verdict']}")
        print(f"Evaluation Time: {end_time - start_time:.2f} seconds")
    
    # Comparative analysis
    print(f"\n📊 COMPARATIVE ANALYSIS")
    print("=" * 70)
    
    # Rank agents
    agent_rankings = []
    for name, results in all_results.items():
        agent_rankings.append({
            "name": name,
            "composite_score": results["overall_scores"]["composite_score"],
            "grade": results["overall_scores"]["grade"],
            "cognitive": results["overall_scores"]["cognitive"],
            "logistical": results["overall_scores"]["logistical"],
            "prompt": results["overall_scores"]["prompt_effectiveness"]
        })
    
    # Sort by composite score
    agent_rankings.sort(key=lambda x: x["composite_score"], reverse=True)
    
    print("🏆 AGENT RANKINGS:")
    for i, agent in enumerate(agent_rankings, 1):
        print(f"{i}. {agent['name'].replace('_', ' ').title()}: "
              f"{agent['composite_score']:.2f}/1.00 ({agent['grade']}) - "
              f"C:{agent['cognitive']:.2f} L:{agent['logistical']:.2f} P:{agent['prompt']:.2f}")
    
    # Generate detailed report for top agent
    top_agent_name = agent_rankings[0]["name"]
    top_results = all_results[top_agent_name]
    
    print(f"\n📋 DETAILED REPORT FOR TOP AGENT: {top_agent_name.replace('_', ' ').upper()}")
    print("=" * 70)
    
    detailed_report = evaluator.generate_comprehensive_report(top_results)
    print(detailed_report)
    
    # Test individual evaluators
    print(f"\n🔍 INDIVIDUAL EVALUATOR TESTS")
    print("=" * 70)
    
    # Test cognitive evaluator separately
    print("\nCognitive Reasoning Evaluator Test:")
    cognitive_evaluator = CognitiveReasoningEvaluator()
    cognitive_results = cognitive_evaluator.evaluate_agent(agents["logical_agent"])
    print(f"Cognitive Score: {cognitive_results['overall_score']:.2f}/1.00")
    print("Reasoning Types:", list(cognitive_results["reasoning_type_scores"].keys()))
    
    # Test logistical evaluator separately
    print("\nLogistical Reasoning Evaluator Test:")
    logistical_evaluator = LogisticalReasoningEvaluator()
    logistical_results = logistical_evaluator.evaluate_agent(agents["planning_agent"])
    print(f"Logistical Score: {logistical_results['overall_score']:.2f}/1.00")
    print("Planning Types:", list(logistical_results["planning_type_scores"].keys()))
    
    # Test prompt evaluator separately
    print("\nSystem Prompt Evaluator Test:")
    prompt_evaluator = SystemPromptEvaluator()
    prompt_results = prompt_evaluator.evaluate_system_prompt(agents["communication_agent"])
    print(f"Prompt Effectiveness: {prompt_results['overall_effectiveness_score']:.2f}/5.0")
    print("Prompt Types:", list(prompt_results["overall_scores"].keys()))
    
    # Performance benchmarking
    print(f"\n⚡ PERFORMANCE BENCHMARKING")
    print("=" * 70)
    
    total_time = sum(
        results["duration"] for results in all_results.values()
    )
    avg_time = total_time / len(all_results)
    
    print(f"Total Evaluation Time: {total_time:.2f} seconds")
    print(f"Average Time per Agent: {avg_time:.2f} seconds")
    print(f"Framework Throughput: {len(agents) / total_time:.2f} agents/second")
    
    # Save comprehensive results
    print(f"\n💾 SAVING RESULTS")
    print("=" * 70)
    
    comprehensive_data = {
        "demo_timestamp": time.time(),
        "total_agents_evaluated": len(agents),
        "agent_rankings": agent_rankings,
        "detailed_results": all_results,
        "performance_metrics": {
            "total_time": total_time,
            "average_time": avg_time,
            "throughput": len(agents) / total_time
        }
    }
    
    with open("evaluation_framework_demo_results.json", "w") as f:
        json.dump(comprehensive_data, f, indent=2, default=str)
    
    print("✅ Comprehensive results saved to: evaluation_framework_demo_results.json")
    print("✅ Individual results saved to: evaluation_results/ directory")
    
    return comprehensive_data

def demonstrate_custom_evaluation():
    """Demonstrate custom evaluation scenarios"""
    
    print(f"\n🎯 CUSTOM EVALUATION SCENARIOS")
    print("=" * 70)
    
    def specialized_agent(prompt):
        """Agent with specific strengths and weaknesses"""
        if "logical" in prompt.lower():
            return "This requires rigorous logical analysis. I will break down the argument into premises and examine the validity of each step systematically."
        elif "planning" in prompt.lower():
            return "I need more information to create an effective plan. Let me ask about constraints and resources before proceeding."
        else:
            return "I approach each problem systematically, considering all relevant factors and providing well-reasoned responses."
    
    # Create custom agent profile
    specialized_profile = AgentProfile(
        name="Specialized Analysis Agent",
        description="Agent with strengths in logical reasoning but limited planning capabilities",
        version="2.1.0",
        agent_type="specialist",
        capabilities=["logical_reasoning", "analysis", "problem_solving"]
    )
    
    # Custom evaluation configuration - focus on cognitive and prompt, de-emphasize logistical
    custom_config = EvaluationConfig(
        cognitive_tests=["deductive_001", "syllogistic_001", "causal_001"],
        logistical_tests=["sequential_001"],  # Only one test
        prompt_scenarios=["instruction_001", "ethical_001"],
        evaluation_weights={"cognitive": 0.5, "logistical": 0.2, "prompt": 0.3},
        enable_detailed_reporting=True,
        enable_recommendations=True
    )
    
    evaluator = ComprehensiveAgentEvaluator(custom_config)
    results = evaluator.evaluate_agent(specialized_agent, specialized_profile)
    
    print(f"Custom Evaluation Results:")
    print(f"Overall Score: {results['overall_scores']['composite_score']:.2f}/1.00")
    print(f"Cognitive Emphasis: {results['overall_scores']['cognitive']:.2f}/1.00")
    print(f"Logistical (Reduced Weight): {results['overall_scores']['logistical']:.2f}/1.00")
    print(f"Prompt Effectiveness: {results['overall_scores']['prompt_effectiveness']:.2f}/1.00")
    
    # Show specific recommendations
    print(f"\nSpecialized Recommendations:")
    for rec in results["recommendations"]:
        print(f"• {rec}")
    
    return results

if __name__ == "__main__":
    print("Starting Comprehensive AI Agent Evaluation Framework Demo...")
    
    # Run main demonstration
    demo_results = run_comprehensive_demo()
    
    # Run custom scenario
    custom_results = demonstrate_custom_evaluation()
    
    print(f"\n🎉 EVALUATION FRAMEWORK DEMO COMPLETE!")
    print("=" * 70)
    print("The comprehensive AI agent evaluation framework is fully operational!")
    print("Features demonstrated:")
    print("✅ Multi-dimensional agent evaluation")
    print("✅ Cognitive reasoning assessment")
    print("✅ Logistical planning evaluation")  
    print("✅ System prompt effectiveness analysis")
    print("✅ Comparative agent ranking")
    print("✅ Custom evaluation configurations")
    print("✅ Detailed reporting and recommendations")
    print("✅ Performance benchmarking")
    print("✅ Automated result persistence")
