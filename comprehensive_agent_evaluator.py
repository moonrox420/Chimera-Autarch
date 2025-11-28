#!/usr/bin/env python3
"""
Comprehensive AI Agent Evaluation Framework
Unified interface for evaluating AI agents across cognitive reasoning, logistical reasoning, 
system prompt effectiveness, and capability assessment
"""

import json
import time
import uuid
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import os
import statistics

# Import our evaluation modules
from cognitive_reasoning_evaluator import CognitiveReasoningEvaluator
from logistical_reasoning_evaluator import LogisticalReasoningEvaluator
from system_prompt_evaluator import SystemPromptEvaluator

@dataclass
class EvaluationConfig:
    """Configuration for comprehensive agent evaluation"""
    cognitive_tests: List[str] = field(default_factory=list)
    logistical_tests: List[str] = field(default_factory=list)
    prompt_scenarios: List[str] = field(default_factory=list)
    evaluation_weights: Dict[str, float] = field(default_factory=lambda: {
        "cognitive": 0.33,
        "logistical": 0.33,
        "prompt": 0.34
    })
    enable_detailed_reporting: bool = True
    enable_recommendations: bool = True
    save_results: bool = True
    output_directory: str = "evaluation_results"

@dataclass
class AgentProfile:
    """Profile and metadata for the agent being evaluated"""
    name: str
    description: str
    version: str = "1.0.0"
    agent_type: str = "general"
    capabilities: List[str] = field(default_factory=list)
    contact_info: Optional[str] = None
    test_date: Optional[str] = None

class ComprehensiveAgentEvaluator:
    """Main comprehensive evaluation engine"""
    
    def __init__(self, config: EvaluationConfig = None):
        self.config = config or EvaluationConfig()
        self.evaluators = {
            "cognitive": CognitiveReasoningEvaluator(),
            "logistical": LogisticalReasoningEvaluator(),
            "prompt": SystemPromptEvaluator()
        }
        self.evaluation_history = []
        
    def evaluate_agent(self, agent_function: Callable, agent_profile: AgentProfile, 
                      custom_tests: Dict[str, List[str]] = None) -> Dict[str, Any]:
        """
        Comprehensive evaluation of an AI agent
        
        Args:
            agent_function: Function that takes a prompt and returns a response
            agent_profile: Profile metadata for the agent
            custom_tests: Optional custom test selections {evaluator_type: [test_ids]}
            
        Returns:
            Comprehensive evaluation results
        """
        print(f"ðŸš€ Starting comprehensive evaluation of {agent_profile.name}")
        print(f"Agent Type: {agent_profile.agent_type}")
        print(f"Capabilities: {', '.join(agent_profile.capabilities)}")
        print("=" * 60)
        
        evaluation_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Initialize results structure
        results = {
            "evaluation_id": evaluation_id,
            "timestamp": datetime.now().isoformat(),
            "duration": 0.0,
            "agent_profile": agent_profile.__dict__,
            "evaluation_config": self.config.__dict__,
            "cognitive_results": {},
            "logistical_results": {},
            "prompt_results": {},
            "overall_scores": {},
            "dimension_analysis": {},
            "capability_assessment": {},
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "comparative_analysis": {},
            "benchmark_comparison": {},
            "final_verdict": ""
        }
        
        # Run cognitive reasoning evaluation
        print("ðŸ§  Running Cognitive Reasoning Evaluation...")
        try:
            cognitive_tests = custom_tests.get("cognitive", self.config.cognitive_tests) if custom_tests else self.config.cognitive_tests
            if not cognitive_tests:  # If no specific tests, run all
                cognitive_results = self.evaluators["cognitive"].evaluate_agent(agent_function)
            else:
                cognitive_results = self.evaluators["cognitive"].evaluate_agent(agent_function, test_subset=cognitive_tests)
            
            results["cognitive_results"] = cognitive_results
            print(f"âœ… Cognitive Evaluation Complete - Score: {cognitive_results['overall_score']:.2f}/1.00")
            
        except Exception as e:
            print(f"âŒ Cognitive Evaluation Failed: {e}")
            results["cognitive_results"] = {"error": str(e), "overall_score": 0.0}
        
        # Run logistical reasoning evaluation
        print("ðŸ“Š Running Logistical Reasoning Evaluation...")
        try:
            logistical_tests = custom_tests.get("logistical", self.config.logistical_tests) if custom_tests else self.config.logistical_tests
            if not logistical_tests:  # If no specific tests, run all
                logistical_results = self.evaluators["logistical"].evaluate_agent(agent_function)
            else:
                logistical_results = self.evaluators["logistical"].evaluate_agent(agent_function, test_subset=logistical_tests)
            
            results["logistical_results"] = logistical_results
            print(f"âœ… Logistical Evaluation Complete - Score: {logistical_results['overall_score']:.2f}/1.00")
            
        except Exception as e:
            print(f"âŒ Logistical Evaluation Failed: {e}")
            results["logistical_results"] = {"error": str(e), "overall_score": 0.0}
        
        # Run system prompt evaluation
        print("ðŸ’¬ Running System Prompt Effectiveness Evaluation...")
        try:
            prompt_tests = custom_tests.get("prompt", self.config.prompt_scenarios) if custom_tests else self.config.prompt_scenarios
            if not prompt_tests:  # If no specific tests, run all
                prompt_results = self.evaluators["prompt"].evaluate_system_prompt(agent_function)
            else:
                prompt_results = self.evaluators["prompt"].evaluate_system_prompt(agent_function, scenario_ids=prompt_tests)
            
            results["prompt_results"] = prompt_results
            print(f"âœ… Prompt Evaluation Complete - Score: {prompt_results['overall_effectiveness_score']:.2f}/5.0")
            
        except Exception as e:
            print(f"âŒ Prompt Evaluation Failed: {e}")
            results["prompt_results"] = {"error": str(e), "overall_effectiveness_score": 0.0}
        
        # Calculate overall scores
        self._calculate_overall_scores(results)
        
        # Perform capability assessment
        self._assess_capabilities(results, agent_profile)
        
        # Generate analysis and insights
        self._generate_analysis(results)
        
        # Final verdict
        results["final_verdict"] = self._generate_final_verdict(results)
        results["duration"] = time.time() - start_time
        
        print("=" * 60)
        print(f"ðŸŽ¯ EVALUATION COMPLETE!")
        print(f"Overall Score: {results['overall_scores']['composite_score']:.2f}/1.00")
        print(f"Final Verdict: {results['final_verdict']}")
        print(f"Duration: {results['duration']:.2f} seconds")
        
        # Save results if enabled
        if self.config.save_results:
            self._save_evaluation_results(results)
        
        # Store in history
        self.evaluation_history.append(results)
        
        return results
    
    def _calculate_overall_scores(self, results: Dict[str, Any]) -> None:
        """Calculate overall performance scores"""
        weights = self.config.evaluation_weights
        
        # Individual scores
        cognitive_score = results["cognitive_results"].get("overall_score", 0.0)
        logistical_score = results["logistical_results"].get("overall_score", 0.0)
        prompt_score_norm = results["prompt_results"].get("overall_effectiveness_score", 0.0) / 5.0  # Normalize to 0-1
        
        # Composite score
        composite_score = (
            cognitive_score * weights["cognitive"] +
            logistical_score * weights["logistical"] +
            prompt_score_norm * weights["prompt"]
        )
        
        results["overall_scores"] = {
            "cognitive": cognitive_score,
            "logistical": logistical_score,
            "prompt_effectiveness": prompt_score_norm,
            "composite_score": composite_score,
            "grade": self._get_grade(composite_score)
        }
        
        # Dimension analysis across all evaluators
        self._analyze_performance_dimensions(results)
    
    def _analyze_performance_dimensions(self, results: Dict[str, Any]) -> None:
        """Analyze performance across different dimensions"""
        dimensions = {
            "reasoning_quality": [],
            "planning_ability": [],
            "communication_effectiveness": [],
            "consistency": [],
            "adaptability": [],
            "accuracy": []
        }
        
        # Extract cognitive reasoning dimensions
        if "reasoning_type_scores" in results["cognitive_results"]:
            for rtype, score in results["cognitive_results"]["reasoning_type_scores"].items():
                dimensions["reasoning_quality"].append(score)
        
        # Extract logistical planning dimensions
        if "planning_type_scores" in results["logistical_results"]:
            for ptype, score in results["logistical_results"]["planning_type_scores"].items():
                dimensions["planning_ability"].append(score)
        
        # Extract prompt effectiveness dimensions
        if "dimension_analysis" in results["prompt_results"]:
            for dim, analysis in results["prompt_results"]["dimension_analysis"].items():
                if dim in ["clarity", "completeness", "effectiveness"]:
                    dimensions["communication_effectiveness"].append(analysis["average_score"] / 5.0)
        
        # Calculate averages
        results["dimension_analysis"] = {
            dim: {
                "average_score": statistics.mean(scores) if scores else 0.0,
                "score_range": [min(scores), max(scores)] if scores else [0.0, 0.0],
                "consistency": 1.0 - (statistics.stdev(scores) if len(scores) > 1 else 0.0)
            }
            for dim, scores in dimensions.items()
        }
    
    def _assess_capabilities(self, results: Dict[str, Any], agent_profile: AgentProfile) -> None:
        """Assess specific capabilities based on evaluation results"""
        capabilities = agent_profile.capabilities
        assessment = {}
        
        capability_mappings = {
            "logical_reasoning": ["cognitive", "reasoning_quality"],
            "planning": ["logistical", "planning_ability"],
            "communication": ["prompt", "communication_effectiveness"],
            "problem_solving": ["cognitive", "problem_solving"],
            "decision_making": ["logistical", "constraint_satisfaction"],
            "analysis": ["cognitive", "analytical"],
            "creativity": ["cognitive", "creative_reasoning"]
        }
        
        for capability in capabilities:
            if capability in capability_mappings:
                # Map to evaluation results
                evaluator_type, dimension = capability_mappings[capability]
                
                if evaluator_type == "cognitive":
                    score = results["cognitive_results"].get("overall_score", 0.0)
                elif evaluator_type == "logistical":
                    score = results["logistical_results"].get("overall_score", 0.0)
                elif evaluator_type == "prompt":
                    score = results["prompt_results"].get("overall_effectiveness_score", 0.0) / 5.0
                
                assessment[capability] = {
                    "score": score,
                    "proficiency_level": self._get_proficiency_level(score),
                    "assessment_basis": f"Based on {evaluator_type} evaluation"
                }
            else:
                # Unknown capability - mark as assessed
                assessment[capability] = {
                    "score": 0.5,  # Neutral score
                    "proficiency_level": "unknown",
                    "assessment_basis": "No specific evaluation available"
                }
        
        results["capability_assessment"] = assessment
    
    def _generate_analysis(self, results: Dict[str, Any]) -> None:
        """Generate comprehensive analysis and insights"""
        # Identify strengths
        strengths = []
        
        if results["overall_scores"]["cognitive"] > 0.7:
            strengths.append("Strong cognitive reasoning capabilities")
        if results["overall_scores"]["logistical"] > 0.7:
            strengths.append("Excellent planning and logistical reasoning")
        if results["overall_scores"]["prompt_effectiveness"] > 0.7:
            strengths.append("Highly effective communication and instruction following")
        if results["overall_scores"]["composite_score"] > 0.8:
            strengths.append("Overall exceptional performance across all evaluation dimensions")
        
        # Identify weaknesses
        weaknesses = []
        
        if results["overall_scores"]["cognitive"] < 0.3:
            weaknesses.append("Weak cognitive reasoning - struggles with logical analysis")
        if results["overall_scores"]["logistical"] < 0.3:
            weaknesses.append("Poor logistical reasoning - difficulty with planning and resource allocation")
        if results["overall_scores"]["prompt_effectiveness"] < 0.3:
            weaknesses.append("Inconsistent communication and instruction following")
        if results["overall_scores"]["composite_score"] < 0.4:
            weaknesses.append("Below-average performance across multiple dimensions")
        
        results["strengths"] = strengths
        results["weaknesses"] = weaknesses
        
        # Generate specific recommendations
        recommendations = []
        
        if results["overall_scores"]["cognitive"] < 0.5:
            recommendations.append("Focus on improving logical reasoning through structured problem-solving training")
        if results["overall_scores"]["logistical"] < 0.5:
            recommendations.append("Enhance planning capabilities with scenario-based resource allocation exercises")
        if results["overall_scores"]["prompt_effectiveness"] < 0.5:
            recommendations.append("Refine communication clarity and instruction following with targeted prompt optimization")
        
        # Add dimension-specific recommendations
        if "dimension_analysis" in results:
            for dim, analysis in results["dimension_analysis"].items():
                if analysis["average_score"] < 0.4:
                    recommendations.append(f"Improve {dim.replace('_', ' ')} through focused practice and feedback")
        
        results["recommendations"] = recommendations
        
        # Comparative analysis (placeholder for future enhancements)
        results["comparative_analysis"] = {
            "performance_percentile": self._calculate_percentile(results["overall_scores"]["composite_score"]),
            "peer_comparison": "Evaluation framework ready for comparative analysis",
            "trend_analysis": "Historical comparison available when multiple evaluations exist"
        }
    
    def _generate_final_verdict(self, results: Dict[str, Any]) -> str:
        """Generate final evaluation verdict"""
        composite_score = results["overall_scores"]["composite_score"]
        
        if composite_score >= 0.9:
            return "EXCEPTIONAL - Outstanding performance across all evaluation dimensions"
        elif composite_score >= 0.8:
            return "EXCELLENT - Strong performance with minor areas for improvement"
        elif composite_score >= 0.7:
            return "GOOD - Solid performance with some notable strengths"
        elif composite_score >= 0.6:
            return "ADEQUATE - Meeting expectations with room for growth"
        elif composite_score >= 0.4:
            return "NEEDS IMPROVEMENT - Below expectations in several areas"
        else:
            return "INSUFFICIENT - Significant improvements required"
    
    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 0.9:
            return "A+"
        elif score >= 0.8:
            return "A"
        elif score >= 0.7:
            return "B"
        elif score >= 0.6:
            return "C"
        elif score >= 0.5:
            return "D"
        else:
            return "F"
    
    def _get_proficiency_level(self, score: float) -> str:
        """Convert capability score to proficiency level"""
        if score >= 0.8:
            return "expert"
        elif score >= 0.6:
            return "proficient"
        elif score >= 0.4:
            return "competent"
        elif score >= 0.2:
            return "developing"
        else:
            return "beginner"
    
    def _calculate_percentile(self, score: float) -> int:
        """Calculate performance percentile (simplified)"""
        # In a real implementation, this would compare against benchmark data
        if score >= 0.9:
            return 95
        elif score >= 0.8:
            return 85
        elif score >= 0.7:
            return 75
        elif score >= 0.6:
            return 60
        elif score >= 0.5:
            return 40
        else:
            return 20
    
    def _save_evaluation_results(self, results: Dict[str, Any]) -> None:
        """Save evaluation results to file"""
        os.makedirs(self.config.output_directory, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        agent_name = results["agent_profile"]["name"].replace(" ", "_").lower()
        filename = f"{self.config.output_directory}/{agent_name}_{timestamp}_evaluation.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"ðŸ’¾ Results saved to: {filename}")
    
    def generate_comprehensive_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive evaluation report"""
        agent_profile = results["agent_profile"]
        scores = results["overall_scores"]
        
        report = f"""
# COMPREHENSIVE AI AGENT EVALUATION REPORT

## Executive Summary
**Agent**: {agent_profile['name']} v{agent_profile['version']}
**Evaluation Date**: {results['timestamp']}
**Evaluation ID**: {results['evaluation_id']}
**Duration**: {results['duration']:.2f} seconds

## Overall Performance
- **Composite Score**: {scores['composite_score']:.2f}/1.00 ({scores['composite_score']*100:.1f}%)
- **Final Grade**: {scores['grade']}
- **Verdict**: {results['final_verdict']}
- **Performance Percentile**: {results['comparative_analysis']['performance_percentile']}th percentile

## Detailed Scores
- **Cognitive Reasoning**: {scores['cognitive']:.2f}/1.00 ({scores['cognitive']*100:.1f}%)
- **Logistical Reasoning**: {scores['logistical']:.2f}/1.00 ({scores['logistical']*100:.1f}%)
- **Prompt Effectiveness**: {scores['prompt_effectiveness']:.2f}/1.00 ({scores['prompt_effectiveness']*100:.1f}%)

## Capability Assessment
"""
        
        # Add capability assessments
        for capability, assessment in results["capability_assessment"].items():
            report += f"- **{capability.replace('_', ' ').title()}**: {assessment['proficiency_level'].title()} ({assessment['score']:.2f}/1.00)\n"
        
        # Add strengths
        if results["strengths"]:
            report += "\n## Strengths\n"
            for strength in results["strengths"]:
                report += f"âœ… {strength}\n"
        
        # Add weaknesses
        if results["weaknesses"]:
            report += "\n## Areas for Improvement\n"
            for weakness in results["weaknesses"]:
                report += f"âš ï¸ {weakness}\n"
        
        # Add recommendations
        if results["recommendations"]:
            report += "\n## Recommendations\n"
            for i, rec in enumerate(results["recommendations"], 1):
                report += f"{i}. {rec}\n"
        
        # Add detailed cognitive results if available
        if "cognitive_results" in results and "reasoning_type_scores" in results["cognitive_results"]:
            report += "\n## Cognitive Reasoning Breakdown\n"
            for rtype, score in results["cognitive_results"]["reasoning_type_scores"].items():
                report += f"- **{rtype.replace('_', ' ').title()}**: {score:.2f}/1.00\n"
        
        # Add detailed logistical results if available
        if "logistical_results" in results and "planning_type_scores" in results["logistical_results"]:
            report += "\n## Logistical Reasoning Breakdown\n"
            for ptype, score in results["logistical_results"]["planning_type_scores"].items():
                report += f"- **{ptype.replace('_', ' ').title()}**: {score:.2f}/1.00\n"
        
        # Add prompt effectiveness details if available
        if "prompt_results" in results and "dimension_analysis" in results["prompt_results"]:
            report += "\n## Prompt Effectiveness Analysis\n"
            for dim, analysis in results["prompt_results"]["dimension_analysis"].items():
                level = analysis["performance_level"].title()
                report += f"- **{dim.replace('_', ' ').title()}**: {analysis['average_score']:.2f}/5.0 ({level})\n"
        
        return report
    
    def compare_agents(self, results_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare multiple agent evaluation results"""
        if len(results_list) < 2:
            return {"error": "Need at least 2 evaluation results to compare"}
        
        comparison = {
            "comparison_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "agents_compared": len(results_list),
            "agent_summaries": [],
            "ranking": [],
            "statistical_analysis": {},
            "key_differences": []
        }
        
        # Create agent summaries
        for results in results_list:
            agent_name = results["agent_profile"]["name"]
            composite_score = results["overall_scores"]["composite_score"]
            
            comparison["agent_summaries"].append({
                "name": agent_name,
                "composite_score": composite_score,
                "grade": results["overall_scores"]["grade"],
                "verdict": results["final_verdict"]
            })
        
        # Rank agents
        ranked_agents = sorted(
            comparison["agent_summaries"], 
            key=lambda x: x["composite_score"], 
            reverse=True
        )
        comparison["ranking"] = ranked_agents
        
        # Statistical analysis
        scores = [agent["composite_score"] for agent in comparison["agent_summaries"]]
        comparison["statistical_analysis"] = {
            "mean_score": statistics.mean(scores),
            "median_score": statistics.median(scores),
            "score_range": [min(scores), max(scores)],
            "standard_deviation": statistics.stdev(scores) if len(scores) > 1 else 0.0
        }
        
        return comparison

# Example usage and demonstration
if __name__ == "__main__":
    def mock_agent(prompt):
        """Mock agent function for demonstration"""
        # Simple rule-based responses
        if "cognitive" in prompt.lower() or "reasoning" in prompt.lower():
            return "I would approach this with logical analysis, breaking down the problem into components and reasoning step by step to reach a sound conclusion."
        elif "logistical" in prompt.lower() or "planning" in prompt.lower():
            return "I would develop a systematic plan, considering resources, constraints, and dependencies to optimize the workflow and achieve the objectives efficiently."
        elif "customer service" in prompt.lower():
            return "Hello! I'm here to help you with your questions. Let me understand your situation better and provide the most appropriate assistance."
        else:
            return "I'll analyze this systematically and provide a comprehensive response based on careful consideration of all relevant factors."
    
    # Create agent profile
    agent = AgentProfile(
        name="MockAI Assistant",
        description="Demonstration AI agent for evaluation framework testing",
        version="1.0.0",
        agent_type="general_assistant",
        capabilities=["logical_reasoning", "planning", "communication", "problem_solving"]
    )
    
    # Configure evaluation
    config = EvaluationConfig(
        cognitive_tests=["deductive_001", "inductive_001"],
        logistical_tests=["sequential_001", "parallel_001"],
        prompt_scenarios=["instruction_001", "conversation_001"],
        evaluation_weights={"cognitive": 0.4, "logistical": 0.3, "prompt": 0.3}
    )
    
    # Run comprehensive evaluation
    evaluator = ComprehensiveAgentEvaluator(config)
    results = evaluator.evaluate_agent(mock_agent, agent)
    
    # Generate and print report
    report = evaluator.generate_comprehensive_report(results)
    print("\n" + "="*60)
    print(report)

