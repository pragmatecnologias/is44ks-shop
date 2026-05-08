from __future__ import annotations

from typing import Any, Dict

from app.agents.base_agent import BaseAgent
from app.llm.base import LLMProvider


class MachineDecisionAgent(BaseAgent):
    """Evaluates machine candidates and produces BUY_MACHINE / WAIT / OUTSOURCE / REJECT decisions.

    The rule-based decision logic lives in ProductionService.run_machine_decision().
    This agent provides an optional LLM-enhanced analysis layer that can be used
    to generate richer reasoning and recommendations when an LLM provider is available.
    """

    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider, "machine_decision_agent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        machine = context.get("machine", {})
        evidence = context.get("evidence", [])
        families = context.get("families", [])
        scenarios = context.get("scenarios", [])
        rule_based = context.get("rule_based_decision", {})

        recommendation = rule_based.get("recommendation", "NEEDS_MORE_RESEARCH")
        hard_blockers = rule_based.get("hard_blockers", [])
        warnings = rule_based.get("warnings", [])

        summary = self._generate_summary(
            machine, evidence, families, scenarios, recommendation, hard_blockers, warnings
        )

        return {
            "agent_name": "machine_decision_agent",
            "output_json": {
                "recommendation": recommendation,
                "reason": "; ".join(hard_blockers + warnings) or "All gates passed",
                "confidence": rule_based.get("confidence", "MEDIUM"),
                "hard_blockers": hard_blockers,
                "warnings": warnings,
                "summary": summary,
            },
            "summary": summary,
            "confidence": rule_based.get("confidence", "MEDIUM"),
            "warnings": warnings,
        }

    def _generate_summary(
        self,
        machine: dict,
        evidence: list,
        families: list,
        scenarios: list,
        recommendation: str,
        blockers: list,
        warnings: list,
    ) -> str:
        parts = [f"Machine: {machine.get('name', 'Unknown')}"]
        parts.append(f"Evidence: {len(evidence)} items")
        parts.append(f"Product families: {len(families)}")
        parts.append(f"Cost scenarios: {len(scenarios)}")
        parts.append(f"Decision: {recommendation}")

        if blockers:
            parts.append(f"Blockers: {'; '.join(blockers[:3])}")
        if warnings:
            parts.append(f"Warnings: {'; '.join(warnings[:3])}")

        return " | ".join(parts)
