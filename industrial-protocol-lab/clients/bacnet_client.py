from bacpypes.core import run, stop
from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject
from bacpypes.apdu import ReadPropertyRequest
from bacpypes.pdu import Address
from bacpypes.primitivedata import ObjectIdentifier

import time
import threading

# Create local BACnet device
device = LocalDeviceObject(
    objectName="ClientDevice",
    objectIdentifier=5999,
    maxApduLengthAccepted=1024,
    segmentationSupported="noSegmentation",
    vendorIdentifier=15
)

# Bind to local network
app = BIPSimpleApplication(device, "0.0.0.0")

# Target device (your server)
TARGET_DEVICE = Address("127.0.0.1")

def read_loop():
    while True:
        try:
            request = ReadPropertyRequest(
                objectIdentifier=("analogValue", 1),
                propertyIdentifier="presentValue"
            )
            request.pduDestination = TARGET_DEVICE

            iocb = app.request_io(request)
            time.sleep(1)

            if iocb.ioResponse:
                value = iocb.ioResponse.propertyValue.cast_out(float)
                print("BACnet Value:", value)

        except Exception as e:
            print("BACnet Error:", e)

        time.sleep(2)

threading.Thread(target=read_loop, daemon=True).start()

run()