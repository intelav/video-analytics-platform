from opcua import Server
import random
import time

server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4840")

idx = server.register_namespace("lab")
objects = server.get_objects_node()

temp = objects.add_variable(idx, "Temperature", 25)
temp.set_writable()

server.start()
print("OPC UA server running on 4840")

while True:
    value = random.randint(20, 100)
    temp.set_value(value)
    print("OPC UA:", value)
    time.sleep(2)