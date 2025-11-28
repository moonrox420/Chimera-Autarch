#!/usr/bin/env python3
"""
CHIMERA NEXUS - AI Personality System
Dynamic personality modes that affect AI decision-making and behavior.
"""
import asyncio
import time
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import logging
import random

logger = logging.getLogger("chimera.personality")


class PersonalityMode(Enum):
    """Available personality modes"""
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"
    CREATIVE = "creative"
    ANALYST = "analyst"
    BALANCED = "balanced"


@dataclass
class PersonalityTraits:
    """Personality trait values (0.0 - 1.0)"""
    risk_tolerance: float  # 0.0 = avoid risk, 1.0 = embrace risk
    innovation: float  # 0.0 = stick to proven, 1.0 = try new things
    speed: float  # 0.0 = careful/slow, 1.0 = fast/decisive
    thoroughness: float  # 0.0 = quick checks, 1.0 = exhaustive analysis
    exploration: float  # 0.0 = exploit known, 1.0 = explore unknown
    collaboration: float  # 0.0 = independent, 1.0 = collaborative
    confidence: float  # 0.0 = cautious, 1.0 = confident
    adaptability: float  # 0.0 = rigid, 1.0 = flexible


@dataclass
class DecisionContext:
    """Context for AI decision-making"""
    task_type: str  # "optimization", "learning", "deployment", "analysis"
    importance: int  # 1-10
    time_pressure: bool
    stakes: str  # "low", "medium", "high", "critical"
    available_data: int  # Amount of data available
    confidence_required: float  # Minimum confidence threshold


@dataclass
class Decision:
    """AI decision result"""
    action: str
    confidence: float
    reasoning: str
    alternatives: List[str]
    risk_assessment: str
    personality_influence: Dict[str, float]
    timestamp: float = field(default_factory=time.time)


class PersonalityProfile:
    """A personality configuration"""

    PROFILES = {
        PersonalityMode.AGGRESSIVE: PersonalityTraits(
            risk_tolerance=0.9,
            innovation=0.8,
            speed=0.95,
            thoroughness=0.3,
            exploration=0.7,
            collaboration=0.4,
            confidence=0.9,
            adaptability=0.7
        ),
        PersonalityMode.CONSERVATIVE: PersonalityTraits(
            risk_tolerance=0.2,
            innovation=0.3,
            speed=0.4,
            thoroughness=0.95,
            exploration=0.3,
            collaboration=0.6,
            confidence=0.5,
            adaptability=0.4
        ),
        PersonalityMode.CREATIVE: PersonalityTraits(
            risk_tolerance=0.7,
            innovation=0.95,
            speed=0.6,
            thoroughness=0.5,
            exploration=0.9,
            collaboration=0.7,
            confidence=0.7,
            adaptability=0.9
        ),
        PersonalityMode.ANALYST: PersonalityTraits(
            risk_tolerance=0.4,
            innovation=0.5,
            speed=0.3,
            thoroughness=0.95,
            exploration=0.5,
            collaboration=0.8,
            confidence=0.6,
            adaptability=0.5
        ),
        PersonalityMode.BALANCED: PersonalityTraits(
            risk_tolerance=0.5,
            innovation=0.5,
            speed=0.5,
            thoroughness=0.5,
            exploration=0.5,
            collaboration=0.5,
            confidence=0.5,
            adaptability=0.5
        )
    }

    @classmethod
    def get(cls, mode: PersonalityMode) -> PersonalityTraits:
        """Get personality profile"""
        return cls.PROFILES[mode]

    @classmethod
    def blend(cls, mode1: PersonalityMode, mode2: PersonalityMode,
              weight: float = 0.5) -> PersonalityTraits:
        """Blend two personalities"""
        p1 = cls.get(mode1)
        p2 = cls.get(mode2)

        return PersonalityTraits(
            risk_tolerance=p1.risk_tolerance * weight +
            p2.risk_tolerance * (1 - weight),
            innovation=p1.innovation * weight + p2.innovation * (1 - weight),
            speed=p1.speed * weight + p2.speed * (1 - weight),
            thoroughness=p1.thoroughness * weight +
            p2.thoroughness * (1 - weight),
            exploration=p1.exploration * weight +
            p2.exploration * (1 - weight),
            collaboration=p1.collaboration * weight +
            p2.collaboration * (1 - weight),
            confidence=p1.confidence * weight + p2.confidence * (1 - weight),
            adaptability=p1.adaptability * weight +
            p2.adaptability * (1 - weight)
        )


class PersonalityEngine:
    """Engine that applies personality to decisions"""

    def __init__(self, mode: PersonalityMode = PersonalityMode.BALANCED):
        self.current_mode = mode
        self.traits = PersonalityProfile.get(mode)
        self.decision_history: List[Decision] = []
        self.mode_history: List[Dict[str, Any]] = []

    def set_mode(self, mode: PersonalityMode):
        """Change personality mode"""
        logger.info(
            f"Switching personality from {self.current_mode.value} to {mode.value}")

        self.mode_history.append({
            'from': self.current_mode.value,
            'to': mode.value,
            'timestamp': time.time()
        })

        self.current_mode = mode
        self.traits = PersonalityProfile.get(mode)

    def blend_mode(self, mode2: PersonalityMode, weight: float = 0.5):
        """Blend current mode with another"""
        logger.info(
            f"Blending {self.current_mode.value} with {mode2.value} (weight={weight})")
        self.traits = PersonalityProfile.blend(
            self.current_mode, mode2, weight)

    async def make_decision(self, context: DecisionContext,
                            options: List[str]) -> Decision:
        """Make a decision influenced by personality"""

        # Apply personality modifiers
        adjusted_context = self._apply_personality(context)

        # Score options based on personality
        scored_options = []
        for option in options:
            score = await self._score_option(option, adjusted_context)
            scored_options.append((option, score))

        # Sort by score
        scored_options.sort(key=lambda x: x[1], reverse=True)

        best_option = scored_options[0][0]
        best_score = scored_options[0][1]
        alternatives = [opt for opt, _ in scored_options[1:4]]

        # Generate reasoning
        reasoning = self._generate_reasoning(best_option, best_score, context)

        # Assess risk
        risk = self._assess_risk(best_option, context)

        # Calculate confidence based on personality
        confidence = self._calculate_confidence(best_score, context)

        decision = Decision(
            action=best_option,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=alternatives,
            risk_assessment=risk,
            personality_influence={
                'risk_tolerance': self.traits.risk_tolerance,
                'innovation': self.traits.innovation,
                'speed': self.traits.speed,
                'mode': self.current_mode.value
            }
        )

        self.decision_history.append(decision)

        logger.info(
            f"Decision: {best_option} (confidence={confidence:.2f}, mode={self.current_mode.value})")

        return decision

    def _apply_personality(self, context: DecisionContext) -> DecisionContext:
        """Apply personality modifiers to context"""

        # Aggressive: Lower confidence thresholds
        if self.current_mode == PersonalityMode.AGGRESSIVE:
            context.confidence_required *= 0.7

        # Conservative: Raise confidence thresholds
        elif self.current_mode == PersonalityMode.CONSERVATIVE:
            context.confidence_required *= 1.3

        # Creative: Embrace high stakes as opportunities
        elif self.current_mode == PersonalityMode.CREATIVE:
            if context.stakes in ['high', 'critical']:
                context.importance = min(10, context.importance + 2)

        # Analyst: Require more data
        elif self.current_mode == PersonalityMode.ANALYST:
            context.available_data = int(context.available_data * 1.5)

        return context

    async def _score_option(self, option: str, context: DecisionContext) -> float:
        """Score an option based on personality"""
        score = 0.5  # Base score

        # Analyze option characteristics (simplified)
        is_novel = "new" in option.lower() or "experimental" in option.lower()
        is_safe = "proven" in option.lower() or "stable" in option.lower()
        is_fast = "quick" in option.lower() or "immediate" in option.lower()
        is_thorough = "analyze" in option.lower() or "comprehensive" in option.lower()

        # Apply personality modifiers
        if is_novel:
            score += self.traits.innovation * 0.3

        if is_safe:
            score += (1.0 - self.traits.risk_tolerance) * 0.3

        if is_fast:
            score += self.traits.speed * 0.2

        if is_thorough:
            score += self.traits.thoroughness * 0.2

        # Context modifiers
        if context.time_pressure and is_fast:
            score += 0.2

        if context.stakes == "critical" and is_safe:
            score += 0.2

        # Add some randomness for exploration
        if self.traits.exploration > 0.7:
            score += random.uniform(-0.1, 0.1)

        return max(0.0, min(1.0, score))

    def _calculate_confidence(self, score: float, context: DecisionContext) -> float:
        """Calculate decision confidence"""
        base_confidence = score

        # Personality modifiers
        confidence = base_confidence * self.traits.confidence

        # Context modifiers
        if context.stakes == "critical":
            confidence *= 0.9

        if context.time_pressure:
            confidence *= 0.95

        if context.available_data < 10:
            confidence *= 0.8

        return max(0.1, min(0.99, confidence))

    def _generate_reasoning(self, option: str, score: float,
                            context: DecisionContext) -> str:
        """Generate human-readable reasoning"""

        mode_reasons = {
            PersonalityMode.AGGRESSIVE: "Moving fast and taking calculated risks",
            PersonalityMode.CONSERVATIVE: "Prioritizing safety and proven approaches",
            PersonalityMode.CREATIVE: "Exploring innovative solutions",
            PersonalityMode.ANALYST: "Based on thorough data analysis",
            PersonalityMode.BALANCED: "Balancing multiple factors"
        }

        base_reason = mode_reasons[self.current_mode]

        return f"{base_reason}. Option '{option}' scored {score:.2f} based on {context.task_type} requirements."

    def _assess_risk(self, option: str, context: DecisionContext) -> str:
        """Assess risk level"""

        # Base risk on personality and context
        risk_score = 0.5

        if self.traits.risk_tolerance > 0.7:
            risk_score += 0.2

        if context.stakes == "critical":
            risk_score += 0.3

        if "experimental" in option.lower():
            risk_score += 0.2

        if risk_score < 0.3:
            return "LOW: Minimal risk, proven approach"
        elif risk_score < 0.6:
            return "MEDIUM: Balanced risk-reward ratio"
        else:
            return "HIGH: Significant risk, high potential reward"

    def get_stats(self) -> Dict[str, Any]:
        """Get personality statistics"""
        return {
            'current_mode': self.current_mode.value,
            'traits': {
                'risk_tolerance': self.traits.risk_tolerance,
                'innovation': self.traits.innovation,
                'speed': self.traits.speed,
                'thoroughness': self.traits.thoroughness,
                'exploration': self.traits.exploration,
                'collaboration': self.traits.collaboration,
                'confidence': self.traits.confidence,
                'adaptability': self.traits.adaptability
            },
            'decisions_made': len(self.decision_history),
            'mode_changes': len(self.mode_history),
            'recent_decisions': [
                {
                    'action': d.action,
                    'confidence': d.confidence,
                    'risk': d.risk_assessment
                }
                for d in self.decision_history[-5:]
            ]
        }


class AdaptivePersonalityEngine(PersonalityEngine):
    """Personality that adapts based on outcomes"""

    def __init__(self, mode: PersonalityMode = PersonalityMode.BALANCED):
        super().__init__(mode)
        self.outcome_history: List[Dict[str, Any]] = []
        self.performance_by_mode: Dict[str, List[float]] = {
            mode.value: [] for mode in PersonalityMode
        }

    async def record_outcome(self, decision: Decision, success: bool,
                             actual_result: Any):
        """Record decision outcome for learning"""

        self.outcome_history.append({
            'decision': decision.action,
            'mode': self.current_mode.value,
            'confidence': decision.confidence,
            'success': success,
            'timestamp': time.time()
        })

        # Update performance tracking
        self.performance_by_mode[self.current_mode.value].append(
            1.0 if success else 0.0)

        # Adaptive learning
        await self._adapt_from_outcome(decision, success)

    async def _adapt_from_outcome(self, decision: Decision, success: bool):
        """Adapt personality based on outcome"""

        # If failed with high confidence, become more conservative
        if not success and decision.confidence > 0.8:
            logger.info("High-confidence failure - becoming more conservative")
            self.traits.risk_tolerance *= 0.9
            self.traits.thoroughness *= 1.1

        # If succeeded with low confidence, become more confident
        elif success and decision.confidence < 0.5:
            logger.info("Low-confidence success - boosting confidence")
            self.traits.confidence *= 1.1

        # Check if mode switch needed
        await self._consider_mode_switch()

    async def _consider_mode_switch(self):
        """Consider switching mode based on performance"""

        # Need at least 10 decisions per mode to evaluate
        if len(self.outcome_history) < 50:
            return

        # Calculate success rates
        current_success = self._calculate_success_rate(self.current_mode)

        # Check other modes
        best_mode = self.current_mode
        best_rate = current_success

        for mode in PersonalityMode:
            rate = self._calculate_success_rate(mode)
            if rate > best_rate + 0.1:  # At least 10% better
                best_mode = mode
                best_rate = rate

        # Switch if another mode is significantly better
        if best_mode != self.current_mode:
            logger.info(
                f"Switching to {best_mode.value} (success rate: {best_rate:.2%} vs {current_success:.2%})")
            self.set_mode(best_mode)

    def _calculate_success_rate(self, mode: PersonalityMode) -> float:
        """Calculate success rate for a mode"""
        outcomes = self.performance_by_mode.get(mode.value, [])
        if not outcomes:
            return 0.5  # Default

        recent = outcomes[-20:]  # Last 20 decisions
        return sum(recent) / len(recent)


# Integration with CHIMERA
class ChimeraPersonalityIntegration:
    """Integration layer for CHIMERA"""

    def __init__(self, heart_node):
        self.heart = heart_node
        self.engine = AdaptivePersonalityEngine(PersonalityMode.BALANCED)

    async def make_system_decision(self, decision_type: str,
                                   options: List[str],
                                   context: Dict[str, Any]) -> Decision:
        """Make a system-level decision with personality"""

        # Convert context
        decision_context = DecisionContext(
            task_type=decision_type,
            importance=context.get('importance', 5),
            time_pressure=context.get('urgent', False),
            stakes=context.get('stakes', 'medium'),
            available_data=context.get('data_points', 50),
            confidence_required=context.get('min_confidence', 0.7)
        )

        return await self.engine.make_decision(decision_context, options)

    def set_mode_for_task(self, task_type: str):
        """Auto-select personality mode for task type"""

        mode_map = {
            'optimization': PersonalityMode.AGGRESSIVE,
            'security': PersonalityMode.CONSERVATIVE,
            'research': PersonalityMode.CREATIVE,
            'analysis': PersonalityMode.ANALYST,
            'deployment': PersonalityMode.BALANCED
        }

        mode = mode_map.get(task_type, PersonalityMode.BALANCED)
        self.engine.set_mode(mode)

        logger.info(f"Set personality mode to {mode.value} for {task_type}")

