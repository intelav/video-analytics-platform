# adapters/goose_adapter.py
from common.base_adapter import BaseAdapter
import random

class GOOSEAdapter(BaseAdapter):
    def connect(self):
        pass

    def read(self):
        # Replace with scapy parsing later
        return self.normalize({
            "event": random.randint(0, 1)
        })