from .siliconflow import SiliconFlow
from .model_platform import ModelPlatform
from .openai import OpenAI
from .volcengine_ark import VolcengineArk

PLATFORMNAMEMAP = {
    "SiliconFlow": SiliconFlow,
    "OpenAI": OpenAI,
    "VolcengineArk": VolcengineArk
}

__all__ = ["ModelPlatform", "PLATFORMNAMEMAP",
           "SiliconFlow", "OpenAI", "VolcengineArk"]

