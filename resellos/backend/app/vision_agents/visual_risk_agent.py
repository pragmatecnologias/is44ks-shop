from app.vision_agents.base import BaseVisionAgent


class VisualRiskAgent(BaseVisionAgent):
    def __init__(self, service=None):
        super().__init__("VISUAL_RISK", service=service, agent_name="visual_risk_agent")
