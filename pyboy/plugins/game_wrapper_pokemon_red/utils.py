from .constants import ASCII_DELTA

def press_a(pyboy):
    # PRESS_BUTTON_A
    pyboy.send_input(5)
    pyboy.tick()
    # RELEASE_BUTTON_A
    pyboy.send_input(13)

def get_bit(value, count=1, index = 0):
    bits = bin(value).removeprefix("0b")
    nen = len(bits)
    return int(bits[nen-count:nen-index], 2)
def set_bits(value, new_value, index=0):
    set_bits = list(reversed(bin(new_value).removeprefix('0b')))
    for i, b in enumerate(list(set_bits)):
        if int(b) == 1:
            value |= (1 << index + i)
        else:
            value &= ~(1 << index+i)
    return value
def set_bit(value, index, state=1):
    if state == 0:
        return value & ~(1 << index)    
    return value | (1 << index)

def fill_range(pyboy, index, value: bytearray):
    for i, v in enumerate(value):
        pyboy.set_memory_value(index+i, v)
def read_range(pyboy, index, to=1):
    return [pyboy.get_memory_value(index + i) for i in range(to)]

def sequence_in(sequence, source):
    return any(sequence == source[i:i+len(sequence)] for i in range(len(source)))
def first(arr, default):
    if len(arr) > 0:
        return arr[0]
    return default

class String:
    table = [
        (0x4F, ""),
        (0x57, "#"),
        (0x52, "A1"),
        (0x53, "A2"),
        (0x54, "POKé"),
        (0x55, "+"),
        (0x58, "$"),
        (0x75, "..."),
        (0x7b, ""),
        # empty
        (0x7F, " "),
        (0x9A, "("),
        (0x9B, ")"),
        (0x9C, ":"),
        (0x9E, "["),
        (0x9F, "]"),
        (0xBA, "é"),
        (0xBB, "'d"),
        (0xBC, "'l"),
        (0xBD, "'s"),
        (0xBE, "'t"),
        (0xBF, "'v"),
        (0xE0, "'"),
        (0xE1, "PK"),
        (0xE2, "MN"),
        (0xE3, "-"),
        (0xE4, "'r"),
        (0xE5, "'m"),
        (0xE6, "?"),
        (0xE7, "!"),
        (0xE8, "."),
        # char to show current selectionn
        (0xED, "→"),
        # char to tell user to press button (bottom right when textbox)
        (0xEE, "↓"),
        (0xF4, ","),
        (0xF7, "\n"),
        (0xF5, "♀"),
        (0xF6, "0"),
        (0xF7, "1"),
        (0xF8, "2"),
        (0xF9, "3"),
        (0xFA, "4"),
        (0xFB, "5"),
        (0xFC, "6"),
        (0xFD, "7"),
        (0xFE, "8"),
        (0xFF, "9")
        
    ]

    @classmethod
    def decode_bytes(cls, value):
        return ' '.join(''.join([c for c in [cls.decode_char(x) for x in value] if c != "\u200b"]).split()).replace("\xad", "> ")
    @classmethod
    def encode_string(cls, value):
        return [cls.encode_char(s) for s in list(value)]

    @classmethod
    def encode_char(cls, value):
        return next(iter([e for e, d in cls.table if d == value]), ord(value) + ASCII_DELTA)
    @classmethod
    def decode_char(cls, value):
        # ignore border
        if value == 0x7C:
            return "" # "|"
        if value in [0, 7, 14, 21, 28, 35, 42, 2, 9, 16, 23, 30, 37, 44, 4, 11, 18, 25, 32, 39, 46]:
            return ""
        try:
            return next(iter([d for e, d in cls.table if e == value]), chr(value - ASCII_DELTA))
        except ValueError:
            # print("unknown", value)
            return "\u200b"