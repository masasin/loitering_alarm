import time

from machine import I2C

from lib.utils import Pin

from .base import LCD


class AE_AQM0802_I2C(LCD):
    VALID_ADDRESSES = [
        [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07],
        [0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47],
    ]

    _CONTROL_BYTE_COMMAND = 0x00
    _CONTROL_BYTE_DATA = 0x40

    _ST7032_CHAR_MAP = {
        "→": 0x7E,
        "←": 0x7F,
        "°": 0xDF,
        "。": 0xA1,
        "「": 0xA2,
        "」": 0xA3,
        "、": 0xA4,
        "・": 0xA5,
        "ヲ": 0xA6,
        "ァ": 0xA7,
        "ィ": 0xA8,
        "ゥ": 0xA9,
        "ェ": 0xAA,
        "ォ": 0xAB,
        "ャ": 0xAC,
        "ュ": 0xAD,
        "ョ": 0xAE,
        "ッ": 0xAF,
        "ー": 0xB0,
        "ア": 0xB1,
        "イ": 0xB2,
        "ウ": 0xB3,
        "エ": 0xB4,
        "オ": 0xB5,
        "カ": 0xB6,
        "キ": 0xB7,
        "ク": 0xB8,
        "ケ": 0xB9,
        "コ": 0xBA,
        "サ": 0xBB,
        "シ": 0xBC,
        "ス": 0xBD,
        "セ": 0xBE,
        "ソ": 0xBF,
        "タ": 0xC0,
        "チ": 0xC1,
        "ツ": 0xC2,
        "テ": 0xC3,
        "ト": 0xC4,
        "ナ": 0xC5,
        "ニ": 0xC6,
        "ヌ": 0xC7,
        "ネ": 0xC8,
        "ノ": 0xC9,
        "ハ": 0xCA,
        "ヒ": 0xCB,
        "フ": 0xCC,
        "ヘ": 0xCD,
        "ホ": 0xCE,
        "マ": 0xCF,
        "ミ": 0xD0,
        "ム": 0xD1,
        "メ": 0xD2,
        "モ": 0xD3,
        "ヤ": 0xD4,
        "ユ": 0xD5,
        "ヨ": 0xD6,
        "ラ": 0xD7,
        "リ": 0xD8,
        "ル": 0xD9,
        "レ": 0xDA,
        "ロ": 0xDB,
        "ワ": 0xDC,
        "ン": 0xDD,
        "゛": 0xDE,
        "゜": 0xDF,
    }

    def __init__(
        self,
        clock_pin: int,
        data_pin: int,
        addr: int = 0x3E,
        reset_pin: int | None = None,
        initialize: bool = True,
        show_cursor: bool = False,
        blinking: bool = False,
    ):
        self.i2c = I2C(0, scl=Pin(clock_pin).pin, sda=Pin(data_pin).pin, freq=400_000)
        self.addr = addr

        if not self.is_available():
            print(f"LCD at address {hex(addr)} not found.")
            return

        self.reset_pin = Pin(reset_pin, Pin.OUT) if reset_pin else None
        self.full_length_bus = True
        self.single_line = False
        self.double_height_font = False
        self.instruction_table = 0
        if initialize:
            time.sleep_ms(50)
            self.function_set(instruction_table=1)
            self.internal_osc_frequency(high_bias=False, frequency=0x04)
            self.power_icon_ctrl_contrast_set(
                icon_display_on=False,
                booster_on=True,
                contrast=0x02,
            )
            self.set_contrast(contrast=0x00)
            self.follower_control(follower_on=True, amplified_ratio=0x04)
            time.sleep_ms(200)
            self.function_set(instruction_table=0)
            self.display_on_off(display=True, cursor=show_cursor, blink=blinking)
            self.clear()
            self.entry_mode_set(left_to_right=True, shift=False)

    def is_available(self) -> bool:
        devices = self.i2c.scan()
        return self.addr in devices

    def reset(self):
        if self.reset_pin is not None:
            self.reset_pin.low()
            time.sleep_us(100)
            self.reset_pin.high()
            time.sleep_ms(5)

    def clear(self):
        self.send_command(0x01)
        time.sleep_us(1100)

    def return_home(self):
        self.send_command(0x02)
        time.sleep_us(1100)

    def entry_mode_set(self, left_to_right=True, shift=False):
        cmd = 0x04
        if left_to_right:
            cmd |= 0x02
        if shift:
            cmd |= 0x01
        self.send_command(cmd)

    def display_on_off(self, display=True, cursor=False, blink=False):
        cmd = 0x08
        if display:
            cmd |= 0x04
        if cursor:
            cmd |= 0x02
        if blink:
            cmd |= 0x01
        self.send_command(cmd)

    def set_ddram_address(self, address: int):
        if not (0x00 <= address <= 0x7F):
            raise ValueError("DDRAM Address must be between 0x00 and 0x7F.")
        cmd = 0x80 | address
        self.send_command(cmd)

    def function_set(
        self,
        full_length_bus: bool | None = None,
        single_line: bool | None = None,
        double_height_font: bool | None = None,
        instruction_table: int = 0,
    ):
        current_instruction_table_state = self.instruction_table
        if full_length_bus is None:
            full_length_bus = self.full_length_bus
        if single_line is None:
            single_line = self.single_line
        if double_height_font is None:
            double_height_font = self.double_height_font
        cmd = 0x20
        if full_length_bus:
            cmd |= 0x10
        if not single_line:
            cmd |= 0x08
        if double_height_font:
            if single_line:
                cmd |= 0x04
            else:
                raise ValueError(
                    "Double height font is only valid for single line display mode (N=0)."
                )
        if instruction_table == 1:
            cmd |= 0x01
        elif instruction_table != 0:
            raise ValueError("instruction_table must be 0 or 1.")
        self.send_command(cmd)
        self.instruction_table = instruction_table
        if current_instruction_table_state != self.instruction_table:
            time.sleep_us(10)

    def shift_display_or_cursor(self, cursor: bool = False, right: bool = True):
        if self.instruction_table == 1:
            self.function_set(instruction_table=0)
        cmd = 0x10
        if not cursor:
            cmd |= 0x08
        if right:
            cmd |= 0x04
        self.send_command(cmd)

    def set_cgram_address(self, address: int):
        raise NotImplementedError(
            "CGRAM (custom characters) is not available on ST7032-0D (OPR1=1, OPR2=1)."
        )

    def internal_osc_frequency(self, high_bias: bool = False, frequency: int = 0x00):
        if self.instruction_table == 0:
            self.function_set(instruction_table=1)
        if not (0x00 <= frequency <= 0x07):
            raise ValueError("Frequency setting must be between 0x00 and 0x07.")
        cmd = 0x10
        if high_bias:
            cmd |= 0x08
        cmd |= frequency
        self.send_command(cmd)

    def set_icon_address(self, address: int):
        if self.instruction_table == 0:
            self.function_set(instruction_table=1)
        if not (0x00 <= address <= 0x0F):
            raise ValueError("ICON Address must be between 0x00 and 0x0F.")
        cmd = 0x40 | address
        self.send_command(cmd)

    def power_icon_ctrl_contrast_set(
        self,
        icon_display_on: bool = True,
        booster_on: bool = True,
        contrast: int = 0x00,
    ):
        if self.instruction_table == 0:
            self.function_set(instruction_table=1)
        if not (0x00 <= contrast <= 0x03):
            raise ValueError(
                "Contrast (upper bits C5,C4) must be between 0x00 and 0x03."
            )
        cmd = 0x50
        if icon_display_on:
            cmd |= 0x08
        if booster_on:
            cmd |= 0x04
        cmd |= contrast
        self.send_command(cmd)

    def follower_control(self, follower_on: bool = True, amplified_ratio: int = 0x00):
        if self.instruction_table == 0:
            self.function_set(instruction_table=1)
        if not (0x00 <= amplified_ratio <= 0x07):
            raise ValueError("Amplified ratio must be between 0x00 and 0x07.")
        cmd = 0x60
        if follower_on:
            cmd |= 0x08
        cmd |= amplified_ratio
        self.send_command(cmd)
        time.sleep_us(30)

    def set_contrast(self, contrast: int):
        if self.instruction_table == 0:
            self.function_set(instruction_table=1)
        if not (0x00 <= contrast <= 0x0F):
            raise ValueError(
                "Contrast (lower bits C3-C0) must be between 0x00 and 0x0F."
            )
        cmd = 0x70 | contrast
        self.send_command(cmd)

    def write(self, text: str):
        for char in text:
            if char in self._ST7032_CHAR_MAP:
                self.send_data(self._ST7032_CHAR_MAP[char])
            else:
                char_code = ord(char)
                if 0 <= char_code <= 0xFF:
                    self.send_data(char_code)

    def set_cursor(self, line: int, column: int):
        if not (
            0 <= line < len(self.VALID_ADDRESSES)
            and 0 <= column < len(self.VALID_ADDRESSES[line])
        ):
            raise ValueError(
                f"Cursor position ({line},{column}) out of bounds for 2x{len(self.VALID_ADDRESSES[0])} display."
            )
        self.set_ddram_address(self.VALID_ADDRESSES[line][column])

    def send_command(self, cmd_byte: int):
        self.i2c.writeto(self.addr, bytes([self._CONTROL_BYTE_COMMAND, cmd_byte]))
        time.sleep_us(30)

    def send_data(self, data_byte: int):
        self.i2c.writeto(self.addr, bytes([self._CONTROL_BYTE_DATA, data_byte]))
        time.sleep_us(30)
