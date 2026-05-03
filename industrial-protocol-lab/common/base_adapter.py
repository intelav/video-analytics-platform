from abc import ABC, abstractmethod
from typing import Dict, Any
import time

class BaseAdapter(ABC):
    def __init__(self, config: Dict):
        self.config = config
        self.device_id = config.get("device_id")

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def read(self) -> Dict[str, Any]:
        pass

    def normalize(self, data: Dict[str, Any]) -> Dict:
        return {
            "timestamp": time.time(),
            "device_id": self.device_id,
            "protocol": self.__class__.__name__,
            "metrics": data
        }