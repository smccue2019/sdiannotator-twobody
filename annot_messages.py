#!/usr/bin/env python

import string

class message20():
    # Build the message for the text to be displayed
    def __init__(self, channel, zone, text2annot):

        startbyte = 0x02
        endbyte = 0x03
        cmd_byte = 0x20

        msg20 = "%02d%04d%s" % (zone, text2annot.__len__(), text2annot)
        #print msg20
        self.bytearr20 = bytearray()
        self.bytearr20.append(0x02)
        self.bytearr20.extend(channel)
        self.bytearr20.append(0x20)
        self.bytearr20.extend(msg20)
        self.bytearr20.append(endbyte)

    def get_msg(self):
        return self.bytearr20

class message21():
    # Build the message that sets font size
    def __init__(self, channel, zone, fontspec):

        startbyte = 0x02
        endbyte = 0x03
        cmd_byte = 0x21
        
        msg21 = "%02d%02d" % (zone,fontspec)
        self.bytearr21 = bytearray()
        self.bytearr21.append(startbyte)
        self.bytearr21.extend(channel)
        self.bytearr21.append(cmd_byte)
        self.bytearr21.extend(msg21)
        self.bytearr21.append(endbyte)

    def get_msg(self):
        return self.bytearr21

class message22():
    # Build the message that sets zone placement
    def __init__(self, channel, zone, x, y):

        startbyte = 0x02
        endbyte = 0x03
        cmd_byte = 0x22
        
        msg22 = "%02d%04d%04d" % (zone, x, y)
        self.bytearr22 = bytearray()
        self.bytearr22.append(startbyte)
        self.bytearr22.extend(channel)
        self.bytearr22.append(cmd_byte)
        self.bytearr22.extend(msg22)
        self.bytearr22.append(endbyte)

    def get_msg(self):
        return self.bytearr22

class message24():
    # Set up font color
    def __init__(self, channel, zone, fontcolorspec, fonttransparencyspec):

        startbyte = 0x02
        endbyte = 0x03
        cmd_byte = 0x24
        
        msg24 = "%02d%02d%02d" % (zone, fontcolorspec, fonttransparencyspec)   
        self.bytearr24 = bytearray()
        self.bytearr24.append(startbyte)
        self.bytearr24.extend(channel)
        self.bytearr24.append(cmd_byte)
        self.bytearr24.extend(msg24)
        self.bytearr24.append(endbyte)

    def get_msg(self):
        return self.bytearr24

class message25():
    # Build the message that sets zone background color and transparency
    def __init__(self, channel, zone, zonecolorspec, zonetransparencyspec):

        startbyte = 0x02
        endbyte = 0x03
        cmd_byte = 0x25

        msg25 = "%02d%02d%02d" % (zone, zonecolorspec, zonetransparencyspec)
        self.bytearr25 = bytearray()
        self.bytearr25.append(startbyte)
        self.bytearr25.extend(channel)
        self.bytearr25.append(cmd_byte)
        self.bytearr25.extend(msg25)
        self.bytearr25.append(endbyte)
        
    def get_msg(self):
        return self.bytearr25

class message27():

    def __init__(self, channel):

        startbyte = 0x02
        endbyte = 0x03
        cmd_byte = 0x27

        msg27 = "0000"
        self.bytearr27=bytearray()
        self.bytearr27.append(startbyte)
        self.bytearr27.extend(channel)
        self.bytearr27.append(cmd_byte)
        self.bytearr27.extend(msg27)
        self.bytearr27.append(endbyte)

    def get_msg(self):
        return self.bytearr27
