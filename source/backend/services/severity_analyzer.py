from __future__ import annotations

import json
import warnings
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama

from backend.core.config import settings


class SeverityAnalyzer:
    _instance: SeverityAnalyzer | None = None
    _llm: Ollama | None = None
    _parser: StrOutputParser | None = None

    def __init__(self) -> None:
        if SeverityAnalyzer._instance is not None:
            raise RuntimeError("Use get_instance() instead")
        self._initialize_llm()

    @classmethod
    def get_instance(cls) -> SeverityAnalyzer:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _initialize_llm(self) -> None:
        """Initialize Ollama LLM and output parser."""
        # Ollama/LLM is optional. If LangChain or Ollama is misconfigured/unavailable,
        # we keep the service running and fall back to a neutral severity.
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message=".*class `Ollama` was deprecated.*",
                )
                self._llm = Ollama(
                    base_url=settings.ollama_base_url,
                    model=settings.ollama_model,
                    temperature=0.3,
                )
            self._parser = StrOutputParser()
        except Exception:
            self._llm = None
            self._parser = None

    async def analyze_outbreak_severity(self, article_text: str, condition: str) -> dict[str, Any]:
        """
        Analyze disease outbreak severity from scraped news articles.

        Args:
            article_text: Combined text from scraped articles
            condition: Disease name

        Returns:
            Dict with keys: disease, severity_score (0-1), trend
        """
        if not article_text.strip():
            # No articles found, return neutral score
            return {
                "disease": condition,
                "severity_score": 0.3,
                "trend": "stable",
            }

        # If LLM isn't available, return neutral score
        if self._llm is None or self._parser is None:
            return {
                "disease": condition,
                "severity_score": 0.3,
                "trend": "stable",
            }

        prompt_template = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a medical data analyst. Analyze news articles about disease outbreaks "
                "and estimate the severity of the outbreak. Return ONLY a valid JSON object with "
                'keys: "disease" (string), "severity_score" (number 0-1), and "trend" (one of: "increasing", "stable", "decreasing").'
            ),
            (
                "human",
                "Analyze the following news articles about {condition} outbreaks and estimate "
                "the disease outbreak severity from 0 to 1.\n\n"
                "Articles:\n{articles}\n\n"
                "Return ONLY valid JSON: {{'disease': '...', 'severity_score': 0.0-1.0, 'trend': 'increasing|stable|decreasing'}}",
            ),
        ])

        chain = prompt_template | self._llm | self._parser

        try:
            result_str = await chain.ainvoke({
                "condition": condition,
                "articles": article_text[:8000],  # Limit input size
            })

            # Parse JSON from response
            # Try to extract JSON if it's wrapped in markdown code blocks
            if "```json" in result_str:
                result_str = result_str.split(
                    "```json")[1].split("```")[0].strip()
            elif "```" in result_str:
                result_str = result_str.split("```")[1].split("```")[0].strip()

            result = json.loads(result_str)

            # Validate and clamp severity_score
            if isinstance(result, dict):
                severity = float(result.get("severity_score", 0.3))
                result["severity_score"] = max(0.0, min(1.0, severity))
                result["disease"] = result.get("disease", condition)
                result["trend"] = result.get("trend", "stable")
                return result
            else:
                raise ValueError("Invalid result format")
        except Exception:
            # Fallback on any error (LangChain/LLM errors, JSON parse issues, etc.)
            return {
                "disease": condition,
                "severity_score": 0.3,
                "trend": "stable",
            }


async def analyze_outbreak_severity(article_text: str, condition: str) -> dict[str, Any]:
    """Convenience function to get singleton instance and analyze."""
    analyzer = SeverityAnalyzer.get_instance()
    return await analyzer.analyze_outbreak_severity(article_text, condition)
