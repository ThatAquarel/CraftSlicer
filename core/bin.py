import numpy as np

StringByte = 8


def get_array(other):
    if isinstance(other, StringBit):
        return other.bytes
    return other


class StringBit:
    def __init__(self, size: int, integer: int = None, string: str = None, array: np.ndarray = None):
        self.size = size
        self.bytes = np.array([False for _ in range(size)], dtype=bool)

        if integer is not None:
            string = np.binary_repr(integer)

        if string is not None:
            string = string[::-1]
            self.bytes[0: len(string)] = np.array(list(string), dtype=int).astype(bool)
        elif array is not None:
            self.bytes[0: array.shape[0]] = array.copy()

    def __str__(self):
        return "".join(str(i) for i in self.bytes * 1)[::-1]

    def pretty_string(self):
        string = str(self)

        return " ".join(string[i:i + 8] for i in range(0, len(string), 8))

    def __lshift__(self, other):
        if (pad_size := int(other)) == 0:
            return StringBit(size=self.size, array=self.bytes)
            # return self

        return StringBit(size=self.size,
                         array=np.pad(self.bytes, (pad_size, 0),
                                      "constant", constant_values=False)[:-pad_size])
        # self.bytes = np.pad(self.bytes, (pad_size, 0), "constant", constant_values=False)[:-pad_size]
        # return self

    def __rshift__(self, other):
        if (pad_size := other) == 0:
            return StringBit(size=self.size, array=self.bytes)
            # return self

        return StringBit(size=self.size,
                         array=np.pad(self.bytes, (0, pad_size),
                                      "constant", constant_values=False)[pad_size:])
        # self.bytes = np.pad(self.bytes, (0, pad_size), "constant", constant_values=False)[pad_size:]
        # return self

    def __or__(self, other):
        return StringBit(size=self.size,
                         array=np.bitwise_or(self.bytes, get_array(other)))

    def __and__(self, other):
        return StringBit(size=self.size,
                         array=np.bitwise_and(self.bytes, get_array(other)))

    def __xor__(self, other):
        return StringBit(size=self.size,
                         array=np.bitwise_xor(self.bytes, get_array(other)))

    def __invert__(self):
        return StringBit(size=self.size,
                         array=np.bitwise_not(self.bytes))


if __name__ == '__main__':
    string_byte = StringBit(4 * 8, integer=2)
    # string_byte1 = StringByte(2, integer=3)
    string_byte1 = StringBit(4 * 8, string="11")
    string_byte2 = StringBit(8 * StringByte, integer=(1 << 64) - 1)

    print(string_byte << 0)

    print(string_byte)
    print(string_byte1)
    print(string_byte2.pretty_string())
    print(string_byte << 1)
    print(string_byte << 14)
    print(string_byte >> 1)
    print(~string_byte)
    print(string_byte | string_byte1)
    print(string_byte & string_byte1)
    print(string_byte ^ string_byte1)
