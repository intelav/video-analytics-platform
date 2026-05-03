# common/factory.py

from adapters.modbus_adapter import ModbusAdapter
from adapters.opcua_adapter import OPCUAAdapter
from adapters.bacnet_adapter import BACnetAdapter
from adapters.goose_adapter import GOOSEAdapter

def get_adapter(device):
    t = device["type"]
    if t == "modbus":
        return ModbusAdapter(device)
    elif t == "opcua":
        return OPCUAAdapter(device)
    elif t == "bacnet":
        return BACnetAdapter(device)
    elif t == "goose":
        return GOOSEAdapter(device)
    else:
        raise ValueError("Unknown type")