from app.vision_agents.base import BaseVisionAgent


class SupplierScreenshotAgent(BaseVisionAgent):
    def __init__(self, service=None):
        super().__init__("SUPPLIER_SCREENSHOT", service=service, agent_name="supplier_screenshot_agent")
