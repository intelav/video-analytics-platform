from pymodbus.client.sync import ModbusTcpClient
import time

client = ModbusTcpClient("localhost", port=5020)

if not client.connect():
    print("Unable to connect to Modbus server")
    exit(1)

while True:
    rr = client.read_holding_registers(0, 3)

    if rr.isError():
        print("Error reading:", rr)
    else:
        print("Modbus Data:", rr.registers)

    time.sleep(2)