"""
AI Service abstraction for future LLM integration.

This abstraction allows connecting to different LLM providers
(OpenAI, Gemini, Anthropic, etc.) without coupling the rest
of the system to a specific provider.

Currently provides a no-op implementation that can be extended.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from pathfinder_ai.models import LearnerProfile


class AIService(ABC):
    """
    Abstract base class for AI/LLM services.
    
    Implement this interface to connect a specific LLM provider.
    
    Example implementations:
    - OpenAIService
    - GeminiService
    - AnthropicService
    """
    
    @abstractmethod
    def generate_explanation(
        self,
        context: Dict
    ) -> str:
        """
        Generate a natural language explanation.
        
        Args:
            context: Dict with explanation context
            
        Returns:
            Generated explanation string
        """
        pass
    
    @abstractmethod
    def summarize_learning_gap(
        self,
        gap_analysis: Dict
    ) -> str:
        """
        Summarize a learning gap in natural language.
        
        Args:
            gap_analysis: Skill gap analysis results
            
        Returns:
            Natural language summary
        """
        pass
    
    @abstractmethod
    def generate_learning_advice(
        self,
        profile: LearnerProfile,
        recommendations: list
    ) -> str:
        """
        Generate personalized learning advice.
        
        Args:
            profile: Learner profile
            recommendations: Ranked recommendations
            
        Returns:
            Personalized advice string
        """
        pass
    
    @abstractmethod
    def generate_progress_feedback(
        self,
        progress_report: Dict
    ) -> str:
        """
        Generate feedback on learner progress.
        
        Args:
            progress_report: Progress analysis report
            
        Returns:
            Feedback string
        """
        pass


class NoOpAIService(AIService):
    """
    No-operation AI service for development and testing.
    
    Returns template responses without calling any external service.
    Use this as a fallback or for development until a real LLM is connected.
    """
    
    def generate_explanation(self, context: Dict) -> str:
        """Generate template explanation."""
        skill = context.get("skill", "this skill")
        career = context.get("career", "your career goal")
        
        return (
            f"This resource will help you learn {skill}, "
            f"which is important for your {career} goal."
        )
    
    def summarize_learning_gap(self, gap_analysis: Dict) -> str:
        """Generate template learning gap summary."""
        missing = len(gap_analysis.get("missing_skills", []))
        weak = len(gap_analysis.get("weak_skills", []))
        
        parts = []
        if missing > 0:
            parts.append(f"You're missing {missing} key skills")
        if weak > 0:
            parts.append(f"You need to strengthen {weak} skills")
        
        summary = " and ".join(parts) if parts else "No significant gaps identified"
        
        return f"{summary} for your career goal."
    
    def generate_learning_advice(
        self,
        profile: LearnerProfile,
        recommendations: list
    ) -> str:
        """Generate template learning advice."""
        return (
            f"Based on your profile, focus on building skills in the recommended order. "
            f"Complete one resource at a time and assess your understanding before moving forward."
        )
    
    def generate_progress_feedback(self, progress_report: Dict) -> str:
        """Generate template progress feedback."""
        completion = progress_report.get("metrics", {}).get("completion_rate", 0)
        
        if completion < 0.2:
            feedback = "You're just getting started! Keep building momentum."
        elif completion < 0.5:
            feedback = "Good progress so far. Continue with the next recommended resources."
        elif completion < 0.8:
            feedback = "You're over halfway through! Maintain your pace."
        else:
            feedback = "Excellent progress! You're almost at your goals."
        
        return feedback


class MockAIService(AIService):
    """
    Mock AI service that returns predefined responses.
    
    Useful for testing without external dependencies.
    """
    
    def __init__(self, responses: Optional[Dict] = None):
        """
        Initialize with optional predefined responses.
        
        Args:
            responses: Dict mapping method names to response strings
        """
        self.responses = responses or {}
    
    def generate_explanation(self, context: Dict) -> str:
        """Return mocked explanation."""
        return self.responses.get(
            "explanation",
            "Mocked explanation response"
        )
    
    def summarize_learning_gap(self, gap_analysis: Dict) -> str:
        """Return mocked summary."""
        return self.responses.get(
            "gap_summary",
            "Mocked gap analysis summary"
        )
    
    def generate_learning_advice(
        self,
        profile: LearnerProfile,
        recommendations: list
    ) -> str:
        """Return mocked advice."""
        return self.responses.get(
            "advice",
            "Mocked learning advice"
        )
    
    def generate_progress_feedback(self, progress_report: Dict) -> str:
        """Return mocked feedback."""
        return self.responses.get(
            "feedback",
            "Mocked progress feedback"
        )


# Example: How to implement a real LLM service
class LLMServiceTemplate(AIService):
    """
    Template for implementing a real LLM service.
    
    To connect a real LLM:
    1. Inherit from AIService
    2. Implement all abstract methods
    3. Call your LLM provider's API
    4. Handle rate limiting, caching, etc.
    
    Example:
        class OpenAIService(AIService):
            def __init__(self, api_key: str, model: str):
                self.client = OpenAI(api_key=api_key)
                self.model = model
            
            def generate_explanation(self, context: Dict) -> str:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "..."},
                        {"role": "user", "content": f"...{context}..."}
                    ]
                )
                return response.choices[0].message.content
    """
    
    def generate_explanation(self, context: Dict) -> str:
        """Implement LLM call here."""
        raise NotImplementedError(
            "Use a real implementation like OpenAIService"
        )
    
    def summarize_learning_gap(self, gap_analysis: Dict) -> str:
        """Implement LLM call here."""
        raise NotImplementedError(
            "Use a real implementation like OpenAIService"
        )
    
    def generate_learning_advice(
        self,
        profile: LearnerProfile,
        recommendations: list
    ) -> str:
        """Implement LLM call here."""
        raise NotImplementedError(
            "Use a real implementation like OpenAIService"
        )
    
    def generate_progress_feedback(self, progress_report: Dict) -> str:
        """Implement LLM call here."""
        raise NotImplementedError(
            "Use a real implementation like OpenAIService"
        )
