#!/usr/bin/env python

import sys
import signal
import socket
from PyQt4.QtCore import Qt, QTime, QTimer, QString, pyqtSignal
from PyQt4.QtNetwork import *
from PyQt4.QtGui import *
from ConfigParser import SafeConfigParser

class annot_controller():

    def __init__(self, config_file):
        self.do_initialization(config_file)
        # initialize fields so early execution doesn't break. Will be
        # overwritten by values from UDP.
        self.jdsdepth = "0"
        self.jdstime = "0"
        self.med_heading = "0"
        self.med_alt = "0"
        self.med_depth = "0"
        self.med_wraps = "0"
        self.jdsdate = "0"
        self.jdstime = "0"
        self.jdsdepth = "0"
        self.jdsalt = "0"
        self.delta = "0"

        self.hom_udp = 10506

        self.meta_receiver=UDPreceiver(self.src_udp)
        self.meta_receiver.new_jds.connect(self.on_new_jds)
        self.meta_receiver.new_mds.connect(self.on_new_mds)
        self.meta_receiver.new_odr.connect(self.on_new_odr)
        self.meta_receiver.new_ctm.connect(self.on_new_ctm)
        self.meta_receiver.new_oos.connect(self.on_new_oos)

        self.homer_receiver=UDPreceiver(self.hom_udp)
        self.homer_receiver.new_hom.connect(self.on_new_hom)

        self.annot_send = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

    def on_new_hom(self, udpstr):
        hn, hr, hd = parseHOM(udpstr)
        #print hr
        try:
            hn = int(hn)
            hr=float(hr)
            self.homer_str = "%d:%4.1f%s" % (hn, hr, hd)
        except ValueError:
            self.homer_str = "--:--:--"

        self.write2annot(self.med_channel, self.medhomerzone, self.homer_str)
        self.write2annot(self.butt_channel, self.butthomerzone, self.homer_str)
         
    def on_new_oos(self, udpstr):
        self.o2, self.o2temp = parseOOS(udpstr)
        self.oos_annot_str = "O2:%5.1fuM T:%4.2fC" % (self.o2, self.o2temp)
        #print "%s" % self.oos_annot_str
        self.write2annot(self.butt_channel, self.buttoptodezone, self.oos_annot_str)

    def on_new_mds(self, udpstr):
        mh, ma, md, mw = parseMDS(udpstr)
        self.med_depth = md
        self.medheading_str = "M=%03d" % int(float(mh))
        self.medalt_str = "Alt=%.1f" % float(ma)
        self.meddepth_str = "D=%d" % int(float(md))
        self.medwraps_str = "w=%4.1f" % float(mw)

        try:
            deltadawn = float(self.jdsdepth) - float(self.med_depth)
        except ValueError:
            deltadawn = "0"

        self.deltastr = "delta=%d" % deltadawn
        
        self.write2annot(self.med_channel, self.medmheadzone, self.medheading_str)
        self.write2annot(self.med_channel, self.medaltzone, self.medalt_str)
        self.write2annot(self.med_channel, self.meddepthzone, self.meddepth_str)
        self.write2annot(self.med_channel, self.medwrapszone, self.medwraps_str)
        self.write2annot(self.med_channel, self.meddelzone, self.deltastr)
        self.write2annot(self.butt_channel, self.buttdeltazone, self.deltastr)

    def on_new_jds(self, udpstr):
        jda, jt, jde, ja, jh = parseJDS(udpstr)
        self.jdsdate = jda
        self.jdsdepth = jde
        self.jdsalt = ja
        self.jdshead = jh
        
        jtf = removeZZZfromJDStime(jt)
        self.jdstime = "%s" % jtf.toAscii()
        
        try:
            deltadawn = float(self.jdsdepth) - float(self.med_depth)
        except ValueError:
            deltadawn = "0"

        self.jdsdepthstr = "J2D=%d" % int(float(self.jdsdepth))
        self.jdsaltstr = "Alt=%d" % int(float(self.jdsalt))
        self.jdsheadstr = "J=%03d" % int(float(self.jdshead))
        self.deltastr = "delta=%d" % int(deltadawn)
        self.write2annot(self.butt_channel, self.buttdatezone, self.jdsdate)
        self.write2annot(self.butt_channel, self.butttimezone, self.jdstime)
        self.write2annot(self.butt_channel, self.buttdepthzone, self.jdsdepthstr)
#        self.write2annot(butt_channel, buttaltzone, self.jdsaltstr)
        self.write2annot(self.butt_channel, self.buttdeltazone, self.deltastr)
        self.write2annot(self.med_channel, self.meddelzone, self.deltastr)
        self.write2annot(self.med_channel, self.medjheadzone, self.jdsheadstr)

    def on_new_odr(self, udpstr):
        odrdatestr, odrtimestr, lowid = parseODR(udpstr)
        self.write2annot(self.butt_channel, self.buttdivezone, lowid)

    def on_new_ctm(self, udpstr):
        ctmstr = parseCTM(udpstr)
        if ctmstr:
            self.ctm_str = "T=%s" % ctmstr.toAscii()
            self.write2annot(self.butt_channel, self.buttctmzone, self.ctm_str)
            self.write2annot(self.med_channel, self.medctmzone, self.ctm_str)

    def write2annot(self, chan, zone, text):

        if chan == self.med_channel:
            x = self.medx
            y = self.medy
            fontcolorspec=self.medfontcolorspec
        elif chan == self.butt_channel:
            x = self.buttx
            y = self.butty
            fontcolorspec=self.buttfontcolorspec
        else:
            print "Problem with assigning position vectors"

        m1=message21(chan, zone, self.fontspec)
        self.annot_send.sendto(m1.get_msg(), (self.dest_ip, self.dest_udp) )
        m2=message22(chan, zone, x[zone], y[zone])
        self.annot_send.sendto(m2.get_msg(), (self.dest_ip, self.dest_udp) )
        m3=message25(chan, zone, self.zonecolorspec, self.zonetransparencyspec)
        self.annot_send.sendto(m3.get_msg(), (self.dest_ip, self.dest_udp) )
        m4=message24(chan, zone, fontcolorspec, self.fonttransparencyspec)
        self.annot_send.sendto(m4.get_msg(), (self.dest_ip, self.dest_udp) )
        m5=message27(chan)
        self.annot_send.sendto(m5.get_msg(), (self.dest_ip, self.dest_udp) )
        m6=message20(chan, zone, text)
        self.annot_send.sendto(m6.get_msg(), (self.dest_ip, self.dest_udp) )

    def do_initialization(self, config_file):

        ini_parser = SafeConfigParser()
        ini_parser.read(config_file)

        self.src_udp = num(ini_parser.get('Ntwk','SRC_UDP'))
        self.dest_udp = num(ini_parser.get('Ntwk','DEST_UDP'))
#        self.dest_ip = ini_parser.get('Ntwk','DEST_IP')
        self.dest_ip="198.17.154.196"

        self.butt_channel = ini_parser.get('Annot', 'butt_channel')
        self.med_channel = ini_parser.get('Annot', 'med_channel')

        self.medaltzone=num(ini_parser.get('Annot', 'medaltzone'))
        self.medjheadzone=num(ini_parser.get('Annot', 'medjheadzone'))
        self.meddelzone=num(ini_parser.get('Annot', 'meddelzone'))
        self.meddepthzone=num(ini_parser.get('Annot', 'meddepthzone'))
        self.medmheadzone=num(ini_parser.get('Annot', 'medmheadzone'))
        self.medhomerzone=num(ini_parser.get('Annot', 'medhomerzone'))
        self.medctmzone=num(ini_parser.get('Annot', 'medctmzone'))
        self.medwrapszone=num(ini_parser.get('Annot', 'medwrapszone'))
        self.buttdivezone=num(ini_parser.get('Annot', 'buttdivezone'))
        self.buttdatezone=num(ini_parser.get('Annot', 'buttdatezone'))
        self.butttimezone=num(ini_parser.get('Annot', 'butttimezone'))
        self.buttctmzone=num(ini_parser.get('Annot', 'buttctmzone'))
        self.buttoptodezone=num(ini_parser.get('Annot', 'buttoptodezone'))
        self.butthomerzone=num(ini_parser.get('Annot', 'butthomerzone'))
        self.buttdepthzone=num(ini_parser.get('Annot', 'buttdepthzone'))
        self.buttdeltazone=num(ini_parser.get('Annot', 'buttdeltazone'))

        self.fontspec=num(ini_parser.get('Annot', 'fontspec'))
        self.zonecolorspec=num(ini_parser.get('Annot', 'zonecolorspec'))
        self.zonetransparencyspec=num(ini_parser.get('Annot', 'zonetransparencyspec'))
        self.fonttransparencyspec=num(ini_parser.get('Annot', 'fonttransparencyspec'))
        self.medfontcolorspec=num(ini_parser.get('Annot', 'medfontcolorspec'))
        self.buttfontcolorspec=num(ini_parser.get('Annot', 'buttfontcolorspec'))

        medx0=num(ini_parser.get('Annot','medx0'))
        medx1=num(ini_parser.get('Annot','medx1'))
        medx2=num(ini_parser.get('Annot','medx2'))
        medx3=num(ini_parser.get('Annot','medx3'))
        medx4=num(ini_parser.get('Annot','medx4'))
        medx5=num(ini_parser.get('Annot','medx5'))
        medx6=num(ini_parser.get('Annot','medx6'))
        medx7=num(ini_parser.get('Annot','medx7'))

        medy0=num(ini_parser.get('Annot','medy0'))
        medy1=num(ini_parser.get('Annot','medy1'))
        medy2=num(ini_parser.get('Annot','medy2'))
        medy3=num(ini_parser.get('Annot','medy3'))
        medy4=num(ini_parser.get('Annot','medy4'))
        medy5=num(ini_parser.get('Annot','medy5'))
        medy6=num(ini_parser.get('Annot','medy6'))
        medy7=num(ini_parser.get('Annot','medy7'))

        buttx0=num(ini_parser.get('Annot','buttx0')) 
        buttx1=num(ini_parser.get('Annot','buttx1')) 
        buttx2=num(ini_parser.get('Annot','buttx2')) 
        buttx3=num(ini_parser.get('Annot','buttx3')) 
        buttx4=num(ini_parser.get('Annot','buttx4')) 
        buttx5=num(ini_parser.get('Annot','buttx5')) 
        buttx6=num(ini_parser.get('Annot','buttx6')) 
        buttx7=num(ini_parser.get('Annot','buttx7')) 

        butty0=num(ini_parser.get('Annot','butty0')) 
        butty1=num(ini_parser.get('Annot','butty1')) 
        butty2=num(ini_parser.get('Annot','butty2')) 
        butty3=num(ini_parser.get('Annot','butty3')) 
        butty4=num(ini_parser.get('Annot','butty4')) 
        butty5=num(ini_parser.get('Annot','butty5')) 
        butty6=num(ini_parser.get('Annot','butty6')) 
        butty7=num(ini_parser.get('Annot','butty7')) 
        
        self.medx = [medx0, medx1, medx2, medx3, medx4, medx5, medx6, medx7]
        self.medy = [medy0, medy1, medy2, medy3, medy4, medy5, medy6, medy7]

        self.buttx = [buttx0, buttx1, buttx2, buttx3, buttx4, buttx5, buttx6, buttx7]
        self.butty = [butty0, butty1, butty2, butty3, butty4, butty5, butty6, butty7]

def num(s):
    try:
        return int(s)
    except ValueError as e:
        return float(s)

def sigint_handler(*args):
    sys.stderr.write('\r')
    QApplication.quit()


######################## Main ################################
        
if __name__ == '__main__':

    signal.signal(signal.SIGINT, sigint_handler)
    
    config_file = '/home/data/SDIannotator/annot.ini'
    
    try:
        execfile("/home/data/SDIannotator/udp_receiver.py")
    except Exception as e:
        print "error opening or running /home/data/SDIannotator/udp_receiver.py", e

    try:
        execfile("/home/data/SDIannotator/time_routines.py")
    except Exception as e:
        print "error opening or running /home/data/SDIannotator/time_routines.py", e

    try:
        execfile("/home/data/SDIannotator/parse_routines.py")
    except Exception as e:
        print "error opening or running /home/data/SDIannotator/parse_routines.py", e

    try:
        execfile("/home/data/SDIannotator/annot_messages.py")
    except Exception as e:
        print "error opening or running /home/data/SDIannotator/annot_messages.py", e

    qapp = QApplication(sys.argv)

    # hack to allow closing from the keyboard using sigint handler above
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    thisguy = annot_controller(config_file)

    #ver1.show()

    sys.exit(qapp.exec_())
