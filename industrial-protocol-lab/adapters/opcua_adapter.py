from opcua import Client
from common.base_adapter import BaseAdapter

class OPCUAAdapter(BaseAdapter):

    def connect(self):
        try:
            self.client = Client(self.config["url"])
            self.client.connect()

            objects = self.client.get_objects_node()
            children = objects.get_children()

            self.node = None

            # 🔍 Find node by name (robust)
            for child in children:
                name = child.get_browse_name().Name
                if name == "Temperature":
                    self.node = child
                    break

            if self.node:
                print("OPC UA node found:", self.node)
            else:
                print("OPC UA node NOT found")

        except Exception as e:
            print("OPC UA connection failed:", e)
            self.node = None

    def read(self):
        if not self.node:
            return None

        try:
            val = self.node.get_value()

            return self.normalize({
                "temperature": val
            })

        except Exception as e:
            print("OPC UA read error:", e)
            return None