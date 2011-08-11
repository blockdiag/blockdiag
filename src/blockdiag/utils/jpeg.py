# -*- coding: utf-8 -*-
#  Copyright 2011 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


class StreamReader(object):
    def __init__(self, stream):
        self.stream = stream
        self.pos = 0

    def read_byte(self):
        byte = self.stream[self.pos]
        self.pos += 1
        return ord(byte)

    def read_word(self):
        byte1, byte2 = self.stream[self.pos:self.pos + 2]
        self.pos += 2
        return (ord(byte1) << 8) + ord(byte2)

    def read_bytes(self, n):
        bytes = self.stream[self.pos:self.pos + n]
        self.pos += n
        return bytes


class JpegHeaderReader(StreamReader):
    M_SOI = 0xd8
    M_SOS = 0xda

    def read_marker(self):
        if self.read_byte() != 255:
            raise ValueError("error reading marker")
        return self.read_byte()

    def skip_marker(self):
        """Skip over an unknown or uninteresting variable-length marker"""
        length = self.read_word()
        self.read_bytes(length - 2)

    def __iter__(self):
        while True:
            if self.read_byte() != 255:
                raise ValueError("error reading marker")

            marker = self.read_byte()
            if marker == self.M_SOI:
                length = 0
                data = ''
            else:
                length = self.read_word()
                data = self.read_bytes(length - 2)

            yield (marker, data)

            if marker == self.M_SOS:
                raise StopIteration()


class JpegFile(object):
    M_SOF0 = 0xc0
    M_SOF1 = 0xc1

    @classmethod
    def get_size(self, filename):
        if isinstance(filename, (str, unicode)):
            image = open(filename, 'rb').read()
        else:
            image = filename.read()

        headers = JpegHeaderReader(image)
        for header in headers:
            if header[0] in (self.M_SOF0, self.M_SOF1):
                data = header[1]

                height = (ord(data[1]) << 8) + ord(data[2])
                width = (ord(data[3]) << 8) + ord(data[4])
                return (width, height)
