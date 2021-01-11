#!/usr/bin/env python
import sys, re, time, threading
from math import isnan
from PyQt4.QtCore import Qt, QTime, QTimer, QString, pyqtSignal, QFile
from PyQt4 import QtNetwork

class UDPreceiver(QDialog):

    new_jds = pyqtSignal(QString, name = 'new_jds')
    new_odr = pyqtSignal(QString, name = 'new_odr')
    new_csv = pyqtSignal(QString, name = 'new_csv')
    new_pwhdop = pyqtSignal(float, int, name = 'new_pwhdop')
    new_mds = pyqtSignal(QString, name = 'new_mds')
    new_ctm = pyqtSignal(QString, name = 'new_ctm')
    new_hom = pyqtSignal(QString, name = 'new_hom')
    new_oos = pyqtSignal(QString, name = 'new_oos')

    def __init__(self, listen_port, parent=None):
        super(UDPreceiver, self).__init__(parent)

        self.ListenPort = listen_port
#	print "Listening on UDP port %d" % listen_port

        self.udpSocket = QtNetwork.QUdpSocket(self)
        self.udpSocket.bind(QtNetwork.QHostAddress.Any, self.ListenPort)
        self.udpSocket.readyRead.connect(self.processPendingDatagrams)

    def processPendingDatagrams(self):
        while self.udpSocket.hasPendingDatagrams():
            udpstr, host, port = \
               self.udpSocket.readDatagram(self.udpSocket.pendingDatagramSize())

#            t = re.compile('.TM')
#            if t.match(udpstr):
#            print udpstr

            u = datagram2packetID(udpstr)
            id_string = u.identify_datagram()
            if id_string == 'JDS':
                self.parseJDS(udpstr)
            elif id_string == 'ODR':
                self.new_odr.emit(udpstr)
            elif id_string == 'CSV':
                self.new_csv.emit(udpstr)
            elif id_string == 'PWHDOP':
                dop_alt=self.parsePWHDOP(udpstr)
            elif id_string == 'MDS':
                self.new_mds.emit(udpstr)
            elif id_string == 'CTM':
                self.new_ctm.emit(udpstr)
            elif id_string == 'HOM':
                self.new_hom.emit(udpstr)
            elif id_string == 'OOS':
                self.new_oos.emit(udpstr)
            else:
                # Other packets don't matter
                pass

    def parsePWHDOP(self,pwhdoppkt):
        pwhdoppkt.rstrip('\n')
        pwhdop_fields = pwhdoppkt.split(",")
        try:
            dop_alt = float(pwhdop_fields[6])
        except ValueError:
            dop_alt = nan
        try:
            lock_status = int(pwhdop_fields[10])
        except ValueError:
            lock_status = nan
 
        self.new_pwhdop.emit(dop_alt, lock_status)
        return dop_alt, lock_status

    def parseJDS(self, jdspkt):
# "JDS 2012/04/13 16:52:39 JAS2 11.6877602 -58.5421899 851.68 6020.31 0.0 -3.2 244.02 1327.99 0.81 24356.0 -0.5."

#        print jdspkt
        jdspkt.rstrip('\n')
        jdsfields  = jdspkt.split(" ")
        pktid = jdsfields[0]
        jdsdate = jdsfields[1]
        jdstime = jdsfields[2]
        veh = jdsfields[3]
        latitude_deg = float(jdsfields[4])
        longitude_deg = float(jdsfields[5])
        X_local = float(jdsfields[6])
        Y_local = float(jdsfields[7])
        octans_roll = float(jdsfields[8])
        octans_pitch = float(jdsfields[9])
        octans_heading = float(jdsfields[10])
        depth = float(jdsfields[11])
        unk1 = jdsfields[13]
        unk2= jdsfields[14]

        # Altitude can be wrong for several reasons. one
        # of them is that the vehicle is too high in th
        # water column. If it's not reporting a number,
        # then set it to something that's definitely
        # not-a-number.
        try:
            altitude = float(jdsfields[12])
        except ValueError:
            altitude = nan

        #self.new_altitude.emit(altitude, depth)
        self.new_jds.emit(jdspkt)

        return altitude


class datagram2packetID():

    def __init__(self, datagram):

        self.datagram = datagram
        self.o = re.compile('^ODR')
        self.j = re.compile('^JDS')
        self.c = re.compile('^CSV')
        self.d = re.compile('^\$PWHDOP')
        self.m = re.compile('^MDS')
	self.t = re.compile('^CTM')
        self.h = re.compile('^HOM')
        self.o2 = re.compile('^OOS')

    def identify_datagram(self):

        if self.o.match(self.datagram):
            return('ODR')
        elif self.j.match(self.datagram):
            return('JDS')
        elif self.c.match(self.datagram):
            return('CSV')
        elif self.d.match(self.datagram):
            return('PWHDOP')
        elif self.m.match(self.datagram):
            return('MDS')
	elif self.t.match(self.datagram):
	    return('CTM')
        elif self.h.match(self.datagram):
            return('HOM')
        elif self.o2.match(self.datagram):
            return('OOS')
        else:
            return None
