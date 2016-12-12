import re

# This class parses Linux's input.h file into an object that is usable
# as if the header file were a class.
# All constants are accessible with <object>.<constant>
# For example:
# >>import input_header
# >>i = input_header.input_header()
# >>print i.BTN_A
# 304

# In general, this class parses the provided file and pulls out all
# lines that begin with #define and contain a Key-Value pair on the
# rest of the line. All values are stored as base-10 integers.
# Can successfully parse lines of the following formats:
# Simple integer:      #define KEY_0			11
# Variable reference:  #define KEY_SCREENLOCK		KEY_COFFEE
# Hexadecimal integer: #define BTN_A			0x130
# Variable Increment:  #define KEY_CNT			(KEY_MAX+1)

# Also provides a search(k) method which returns a list of keys parsed from
# the file that contain the specified string 'k'

'''
Copyright (c) 2010 Daniel Nemec
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''


class InputHeader:
    def __init__(self, filename='./temp/URConfigHeader.h'):
        self._inputmap = {}
        try:
            f = open(filename, 'r')
            for line in f:
                pass


        except IOError as fil:
            raise IOError(1, "Input file %s does not exist." % fil)

    def __getattr__(self, attr):
        try:
            ret = self._inputmap[attr]
        except KeyError:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (self.__class__.__name__, attr))
        return ret

    def search(self, key):
        ret = []
        for k in self._inputmap.keys():
            if key.lower() in k.lower():
                ret.append(k)
        return ret