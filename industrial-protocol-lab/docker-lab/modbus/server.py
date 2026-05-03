from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
import random
import threading
import time

store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [10, 20, 30])
)

context = ModbusServerContext(slaves=store, single=True)

def update():
    while True:
        values = [random.randint(0, 100) for _ in range(3)]
        context[0x00].setValues(3, 0, values)
        print("Modbus:", values)
        time.sleep(2)

threading.Thread(target=update, daemon=True).start()

print("Modbus server running on 5020")
StartTcpServer(context, address=("0.0.0.0", 5020))