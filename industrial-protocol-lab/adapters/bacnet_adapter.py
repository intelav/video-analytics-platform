# adapters/bacnet_adapter.py
from common.base_adapter import BaseAdapter
import random

class BACnetAdapter(BaseAdapter):
    def connect(self):
        pass

    def read(self):
        # Replace with real BACnet read later
        return self.normalize({
            "temperature": random.uniform(20, 40)
        })