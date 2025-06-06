import machine
from lib.utils import Pin


def scan_i2c_devices(clock_pin: int, data_pin: int) -> None:
    i2c = machine.I2C(0, scl=Pin(clock_pin), sda=Pin(data_pin), freq=400_000)
    devices = i2c.scan()

    print("Scanning I2C addresses...")

    devices = i2c.scan()

    if not devices:
        print("No I2C devices found.")

    for device in i2c.scan():
        print(f"Found I2C device at address: {hex(device)}")
