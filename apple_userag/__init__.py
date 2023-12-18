from pydantic import BaseModel
from pathlib import Path
import json
from typing import TypedDict
from datetime import datetime, timedelta, timezone
import random

_data_path = Path(__file__).parent / "data.json"

if _data_path.exists() is False:
    print("Run `python -m apple_usera update`, some files are missing.")
    exit()

def _strip_at_number(string: str) -> str:
    result = ""
    for character in string:
        if character.isnumeric():
            break
        else:
            result += character
    return result

_firmware_name = {
    "iPhone": "iOS",
    "iPad": "iPadOS",
    "Watch": "watchOS",
    "AppleTV": "tvOS",
    "MacBookPro": "MacOS",
    "MacBookAir": "MacOS",
    "Macmini": "MacOS",
    "iMac": "MacOS",
    "Mac": "MacOS",
}

def get_os_for_model(model: str) -> str:
    """Returns the OS name for the given model name. Ex: `iPhone` -> `iOS`.

    Args:
        model (str): The model name.

    Raises:
        ValueError: Raised if it doesn't find an OS for it.

    Returns:
        str: The OS name.
    """
    try:
        return _firmware_name[model]
    except KeyError as error:
        raise KeyError('No OS name exists for this device') from error

class Firmware(BaseModel):
    version: str
    """`9.3.6`, `17.0.3`, ... ."""

    buildid: str
    """`7E18`, `21A360`, ... ."""

    releasedate: None | datetime
    """Time of release, can be `None` for very old firmwares."""

    uploaddate: datetime
    """Time it got uploaded to https://ipsw.me."""

    signed: bool
    """Is the firmwire still signed ?"""

class AppleDevice(BaseModel):
    name: str
    """`iPhone 2G`, `iPhone 4 (GSM)`, `MacBook Pro (M1 Max, 14-inch, 2021)`, ... ."""
    
    identifier: str
    """`iPhone1,1`, `iPhone4,1`, `MacBookPro18,4`, ... ."""

    @property
    def device_type(self) -> str:
        """`iPhone`, `iPad`, ... ."""
        return _strip_at_number(self.identifier)

    firmwares: list[Firmware]
    """List of firmwares ever available on the device."""

    @property
    def first_firmware(self) -> Firmware:
        """The first firmware to ever be available on the device."""
        return min(self.firmwares)
    
    @property
    def latest_firmware(self) -> Firmware:
        """The latest firmware to ever be available on the device."""
        return max(self.firmwares)
    
    @property
    def random_firmware(self) -> Firmware:
        """Returns a random firmware the device ever supported."""
        return random.choice(self.firmwares)
    
    @property
    def random_signed_firmware(self) -> Firmware | None:
        """Returns a random firmware still signed (in the db). Will
        return `None` instead of `Firmware` if none have been found."""
        if signed_firmwares := [ firmware for firmware in self.firmwares
                                 if firmware.signed ]:
            return random.choice(signed_firmwares)
    
    def is_outdated(self, days: int = 365) -> bool:
        """Tells if the latest firmware is older than the given days.

        Args:
            days (int, optional): The amount of days without new firmware over which you \
                consider the device as outdated. Defaults to 365.

        Returns:
            bool: Is the device outdated ?
        """
        threshold_date = datetime.now(timezone.utc) - timedelta(days=days)
        return all( releasedate < threshold_date for firmware in self.firmwares
                    if (releasedate := firmware.releasedate) is not None )
    
_AppleDeviceList = list[AppleDevice]
class _DevicesType(TypedDict):
    iPhone: _AppleDeviceList
    iPod: _AppleDeviceList
    iPad: _AppleDeviceList
    AppleTV: _AppleDeviceList
    Watch: _AppleDeviceList
    AudioAccessory: _AppleDeviceList
    iBridge: _AppleDeviceList
    MacBookPro: _AppleDeviceList
    MacBookAir: _AppleDeviceList
    ADP: _AppleDeviceList
    Macmini: _AppleDeviceList
    iMac: _AppleDeviceList
    Mac: _AppleDeviceList
    VirtualMac: _AppleDeviceList

devices: _DevicesType = {}

with open(_data_path, "r") as _read:
    _content = json.load(_read)

for _raw_device in _content:
    _device = AppleDevice(**_raw_device)
    _device_type = _device.device_type
    if _device_type not in devices:
        devices[_device_type] = []
    devices[_device_type].append(_device)

del _AppleDeviceList, _DevicesType, _content, _raw_device, _device_type, _read

def available_devices() -> list[str]:
    """Returns the list of device types available."""
    return list(devices.keys())

def get_non_outdated_devices(device_type: str, days: int = 365) -> list[AppleDevice]:
    """Returns a list of non outdated devices of the given device type.

    Args:
        device_type (str): Device type to get.
        days (int, optional): The amount of days without new firmware over which \
            you consider the device as outdated. Defaults to 365.
    Raises:
        KeyError: Raise if the device type does not exist.

    Returns:
        list[AppleDevice]: The list of non outdated devices.
    """
    try:
        selected_devices: list[AppleDevice] = devices[device_type]
    except KeyError as error:
        raise KeyError( 'The device type does not exist, check the available '
                        'ones with `available_devices()`.' ) from error
    return [ device for device in selected_devices
             if device.is_outdated(days=days) is False ]
    
def get_random_non_outdated_devices(device_type: str, days: int = 365) -> AppleDevice:
    """Returns a random non outdated device of the given device type.

    Args:
        device_type (str): Device type to get.
        days (int, optional): The amount of days without new firmware over which \
            you consider the device as outdated. Defaults to 365.
    Raises:
        KeyError: Raise if the device type does not exist.

    Returns:
        AppleDevice: The random non outdated device.
    """
    return random.choice(get_non_outdated_devices(device_type=device_type, days=days))