import json
import datetime
import boto3
from ...models import DevicesModel
from ..security_controllers.utils import generate_salt, hash_token

def add_device(body, devices_model: DevicesModel):
    salt = generate_salt()

    device = {
        "deviceName": body["deviceName"],
        "macAddress": body["macAddress"],
        "connectionId": None,
        "salt": salt,
        "hashToken": hash_token(body["token"], salt)
    }

    return devices_model.add_device(device)