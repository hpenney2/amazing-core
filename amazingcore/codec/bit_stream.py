import datetime as dt


class BitStream:

    def __init__(self, data: bytearray = None):
        self.data = data or bytearray()
        self.cursor = 0

    def __byte_index__(self):
        return self.cursor >> 3

    def __bit_mask__(self):
        return 0x80 >> (self.cursor % 8)

    def __read_bit__(self):
        byte = self.__byte_index__()
        bit = self.__bit_mask__()
        self.cursor += 1
        return self.data[byte] & bit

    def __read_align_byte__(self):
        while self.__bit_mask__() != 0x80:
            self.cursor += 1  # go to the next byte start
        byte = self.__byte_index__()  # current byte index
        self.cursor += 8  # aligh cursor to the next one
        return self.data[byte]

    def __read_size__(self, base: int):
        if self.__read_bit__() == 0:
            return 4  # min bits per value
        size_bits = 8  # 1 byte per every active bit
        while self.__read_bit__() != 0:
            size_bits += 8  # extra bits = 8, 16, 24, 32...
            if size_bits > (8 * base):  # 32 for int, 64 for long
                raise ValueError(f'size exceeds {base} bytes')
        return size_bits

    def __read_number__(self, size_bits: int):
        value = 0
        for _ in range(size_bits):
            value <<= 1  # shift the big endian
            value |= (self.__read_bit__() != 0)
        is_negative_mask = 1 << (size_bits - 1)
        if (value & is_negative_mask) != 0:  # the first bit stands for negative
            value |= -is_negative_mask  # signed two’s complement
        return value

    def read_int(self):
        if self.__read_bit__() == 0:  # number starts with 1
            raise ValueError('invalid number object')
        size_bits = self.__read_size__(4)  # int compressed
        return self.__read_number__(size_bits)

    def read_long(self):
        if self.__read_bit__() == 0:  # number starts with 1
            raise ValueError('invalid number object')
        size_bits = self.__read_size__(8)  # long compressed
        return self.__read_number__(size_bits)

    def read_start(self):  # message starts with 0
        return self.__read_bit__() == 0

    def read_str(self):
        size_bytes = self.read_int()
        if size_bytes == 0:  # string starts with size in bytes
            return None
        # characters are aligned on whole bytes
        bytes = [self.__read_align_byte__() for _ in range(size_bytes)]
        str_value = bytearray(bytes).decode('utf-8')
        return str_value

    def read_dt(self):
        if not self.read_start():
            return  # date starts with 0
        data = self.__read_number__(8 * 8)  # long uncompressed
        data = (data - 31622400) * 1000.0
        data = data if data > 0 else 0
        return dt.datetime(1, 3, 1) + dt.timedelta(milliseconds=data)

    def __write_bit__(self, active: int):
        byte = self.__byte_index__()
        bit = self.__bit_mask__()
        if bit == 0x80:  # cursor stands on the new byte
            self.data.append(0)
        if active != 0:  # set current bit
            self.data[byte] |= bit
        self.cursor += 1

    def __write_align_byte__(self, byte: int):
        while self.__bit_mask__() != 0x80:
            self.cursor += 1  # go to the next byte start
        self.data.append(byte)
        self.cursor += 8

    def __write_size__(self, value: int, base: int):
        if value > -9 and value < 8:  # from -8 to 7 inclusive
            self.__write_bit__(0)  # done with extra bits
            return 4  # 4 bits for value is enough

        size_bits = 8  # 1 byte is needed
        self.__write_bit__(1)  # each 1 will respresent additional 1 byte

        if value > 0:
            max_value = 127
            while value > max_value:
                # new max_value = 32767, 8388607, 2147483647...
                max_value = (128 << size_bits) - 1
                size_bits += 8  # extra bits = 8, 16, 24, 32...
                if size_bits > (8 * base):  # 32 for int, 64 for long
                    raise ValueError(f'size exceeds {base} bytes', value)
                self.__write_bit__(1)
        else:
            min_value = -128
            while value < min_value:
                # new max_value = -32768, -8388608, -2147483648...
                min_value = -128 << size_bits
                size_bits += 8  # extra bits = 8, 16, 24, 32...
                if size_bits > (8 * base):  # 32 for int, 64 for long
                    raise ValueError(f'size exceeds {base} bytes', value)
                self.__write_bit__(1)

        self.__write_bit__(0)  # done with extra bits
        return size_bits

    def __write_number__(self, value: int, size_bits: int):
        write_bit = (1 << (size_bits - 1))  # current write bit mask
        for _ in range(size_bits):
            bit = value & write_bit != 0
            self.__write_bit__(bit)
            write_bit >>= 1  # next write bit mask

    def write_int(self, value: int):
        if not value:
            value = 0
        self.__write_bit__(1)
        size_bits = self.__write_size__(value, 4)
        self.__write_number__(value, size_bits)

    def write_long(self, value: int):
        if not value:
            value = 0
        self.__write_bit__(1)
        size_bits = self.__write_size__(value, 8)
        self.__write_number__(value, size_bits)

    def write_start(self):
        self.__write_bit__(0)  # Message starts with 0

    def write_str(self, value: str):
        if not value:
            self.write_int(0)
            return  # string starts with size (0 if empty)
        str_bytes = value.encode('utf-8')
        self.write_int(len(str_bytes))
        for char_byte in str_bytes:
            self.__write_align_byte__(char_byte)  # write to the byte start

    def write_dt(self, valie: dt.datetime):
        raise NotImplementedError('writing datetime is not supported yet')
