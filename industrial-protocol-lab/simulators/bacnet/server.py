from bacpypes.core import run
from bacpypes.app import BIPSimpleApplication
from bacpypes.object import AnalogValueObject
from bacpypes.local.device import LocalDeviceObject
import random

device = LocalDeviceObject(
    objectName="BACnetDevice",
    objectIdentifier=599,
    maxApduLengthAccepted=1024,
    segmentationSupported="noSegmentation",
    vendorIdentifier=15
)

app = BIPSimpleApplication(device, "0.0.0.0")

analog = AnalogValueObject(
    objectIdentifier=("analogValue", 1),
    objectName="Temperature",
    presentValue=25.0
)

app.add_object(analog)

def update():
    import time
    while True:
        analog.presentValue = random.uniform(20, 40)
        print("BACnet Temp:", analog.presentValue)
        time.sleep(2)

import threading
threading.Thread(target=update, daemon=True).start()

run()