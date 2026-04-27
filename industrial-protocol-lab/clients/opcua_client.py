from opcua import Client

client = Client("opc.tcp://localhost:4840")
client.connect()

node = client.get_root_node().get_child(
    ["0:Objects", "2:Temperature"]
)

while True:
    print("OPC UA Data:", node.get_value())