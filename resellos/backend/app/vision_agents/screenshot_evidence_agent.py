from app.vision_agents.base import BaseVisionAgent


class ScreenshotEvidenceAgent(BaseVisionAgent):
    def __init__(self, service=None):
        super().__init__("MARKETPLACE_SCREENSHOT", service=service, agent_name="screenshot_evidence_agent")
