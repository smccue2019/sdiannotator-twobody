#!/usr/bin/env python

from PyQt4.QtCore import QString, QRegExp
import re

def parseJDS(jdspkt):
    jdspkt.chop(1)
    jdsfields  = jdspkt.split(" ")
    pktid = jdsfields[0].toAscii()
    jdsdate = jdsfields[1].toAscii()
    jdstime = jdsfields[2].toAscii()
    veh = jdsfields[3].toAscii()
    lat_deg = jdsfields[4].toAscii()
    lon_deg = jdsfields[5].toAscii()
    X_local = jdsfields[6].toAscii()
    Y_local = jdsfields[7].toAscii()
    oct_roll = jdsfields[8].toAscii()
    oct_pitch = jdsfields[9].toAscii()
    oct_heading = jdsfields[10].toAscii()
    jdsdepth = jdsfields[11].toAscii()
    unk1 = jdsfields[13].toAscii()
    unk2= jdsfields[14].toAscii()
    
    # Altitude can be wrong for several reasons. one
    # of them is that the vehicle is too high in th
    # water column. If it's not reporting a number,
    # then set it to something that's definitely
    # not-a-number.
    try:
        jdsalt = jdsfields[12].toAscii()
    except ValueError:
        jdsalt = "0"
    return(jdsdate, jdstime, jdsdepth, jdsalt, oct_heading)
    
def parseODR(odrpkt):
    # ODR 20120413 165239 JAS2 1.0 2.0 11 N001_McCue12 J2-000
    odrpkt.chop(1)
    odrfields = odrpkt.split(" ")
    odrdatestr = odrfields[1].toAscii()
    odrtimestr = odrfields[2].toAscii()
    origlat = odrfields[4].toAscii()
    origlon = odrfields[5].toAscii()
    utmzone = odrfields[6].toAscii()
    cruiseid = odrfields[7].toAscii()
    lowid = odrfields[8].toAscii()
    return odrdatestr, odrtimestr, lowid

def parseCTM(ctmpkt):
    # CTM    yyyy/mm/dd hh:mm:ss.zz  CTM    t.ttC
    # ctmpkt.chop(2)
    # ctmpkt.replace("\t"," ")
    # ctmpkt.replace("  "," ")
    # ctmfields = ctmpkt.split(" ");
    # ctm_tempstr = ctmfields[4]
    print ctmpkt
    pt=re.compile('^CTM\s*\d{4}/\d{2}/\d{2}\s*\d{2}:\d{2}:\d{2}.\d{2,3}\s*CTM\s*(\d+.\d{2}C).*')

    g = pt.match(ctmpkt)
    if g:
        ctm_tempstr = g.group(1)
        return ctm_tempstr

def parseMDS(mdspkt):
    mdspkt.chop(1)
    mdsfields = mdspkt.split(" ")
    # field 0 is 'MDS'
    mdsdate = mdsfields[1].toAscii()
    mdstime = mdsfields[2].toAscii()
    mdsveh = mdsfields[3].toAscii()
    mdslat = mdsfields[4].toAscii()
    mdslon = mdsfields[5].toAscii()
    mdsX = mdsfields[6].toAscii()
    mdsY = mdsfields[7].toAscii()
    mdsroll = mdsfields[8].toAscii()
    mdspitch = mdsfields[9].toAscii()
    mdsheading = mdsfields[10].toAscii()
    mdsdepth = mdsfields[11].toAscii()
    mdsaltitude = mdsfields[12].toAscii()
    mdselaspedtime = mdsfields[13].toAscii()
    mdswraps = mdsfields[14].toAscii()

    return mdsheading, mdsaltitude, mdsdepth, mdswraps

def parseHOM(hompkt):
    # print hompkt
    homfields = hompkt.split(" ")
    homdate = homfields[1]
    homtime = homfields[2]
    homchan_num = homfields[4]
    hom_range = homfields[5]
    hom_range.replace("m","")
    hom_dir = homfields[6].trimmed()
    hom_dir.replace("-","")
    #print hom_dir
    try:
	homchan_num = int(homchan_num)
    except ValueError:
	homchan_num="--"

    try:
        test = num(hom_range)
    except ValueError:
        hom_range="---"

    p = re.compile('<')
    f = re.compile('^')
    s = re.compile('>')

    if p.match(hom_dir):
        dir_str = "<<"
    elif f.match(hom_dir):
        dir_str = "^^"
    elif s.match(hom_dir):
        dir_str = ">>"
    else:
        dir_str = "??"

    return homchan_num, hom_range, dir_str

def parseOOS(oos_string):
    #print oos_string
    oos_string.trimmed()
    # get rid of non-alphanumerics that start sensor string
    oos_string.replace(33,3," ")
    a = oos_string.split(" ")
    b = a[4].split("\t")
    o2 = num(b[4])
    o2temp = num(b[8])
    return o2, o2temp

def num(s):
    try:
        return int(s)
    except ValueError as e:
        return float(s)
