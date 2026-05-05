from app.vision_agents.base import BaseVisionAgent


class CompetitorPhotoAgent(BaseVisionAgent):
    def __init__(self, service=None):
        super().__init__("COMPETITOR_PHOTO", service=service, agent_name="competitor_photo_agent")
