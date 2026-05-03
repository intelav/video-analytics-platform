from pymodbus.client.sync import ModbusTcpClient
from common.base_adapter import BaseAdapter

class ModbusAdapter(BaseAdapter):
    def connect(self):
        self.client = ModbusTcpClient(self.config["host"], port=self.config["port"])
        self.client.connect()

    def read(self):
        rr = self.client.read_holding_registers(0, 3)
        if rr.isError():
            return {}
        return self.normalize({
            "r1": rr.registers[0],
            "r2": rr.registers[1],
            "r3": rr.registers[2]
        })