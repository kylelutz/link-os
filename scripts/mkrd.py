#!/usr/bin/python
# Copyright (C) 2006 Kyle Lutz <kyle.r.lutz@gmail.com>


# Author: Kyle Lutz <kyle.r.lutz@gmail.com>
# MaKe RamDisk

import os
import sys
import struct
from binascii import hexlify

ENDINESS = "BIG"
#ENDINESS = "LITTLE"

# globals
headers = ""
data = ""
offset = 0

def ls(dir):
    flist = []
    for file in os.walk(dir):
        for f in file[2]:
            flist.append(dir + os.sep + f)
    return flist


def add_file(f):
    global data,headers,offset
    name = f.split('/')[-1:][0] + '\0'

    if name == '__directory_file'+'\0':
        name = '.'+'\0'

    size = os.stat(f)[6]
    file_data = open(f,"rb").read()
    
    name_offset = len(data)
    data += name
   
    if(len(data) & 1): data += '\0' # make sure data is aligned on an even boundry
    
    data_offset = len(data)
    data += file_data
    
    if ENDINESS == "LITTLE":
        headers += struct.pack("<LLL",name_offset,data_offset,size)
    elif ENDINESS == "BIG":
        headers += struct.pack(">LLL",name_offset,data_offset,size)
    else:
        headers += struct.pack("@LLL",name_offset,data_offset,size)
    
    print 'added file %s, size %d, name_offset=%d data_offset=%d' % (name,size,name_offset,data_offset)

def bin2ca(binf,caf):
    
    try: binf = open(binf,"rb")
    except IOError,e:
        print 'Failed to open file %s, %s' % (binf,e)
        return
    try: caf = open(caf,"w")
    except IOError,e:
        print 'Failed to open file %s, %s' % (caf,e)
        return
    
    COMMENT = "/* RamDisk File System generated by mkrd. */\n\n"
    caf.write(COMMENT)
    caf.write("unsigned char ramdisk[] = {")

    data = hexlify(binf.read())
    i = 0
    while i < len(data):
        if not i % 22:
            caf.write('\n   ')
        caf.write('0x%s,  ' % data[i:i+2])
        i += 2

    caf.write('0x00 };\n\n')
    binf.close()
    caf.close()

# usage mkrd.py <rd.h> <source directory>

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print "usage: mkrd.py <rd.h> <source directory>"
        sys.exit(-1)

    rd_h = sys.argv[1]
    src_dir = sys.argv[2]

    if src_dir[0] != os.sep:
        src_dir = os.getcwd() + os.sep + src_dir

    if not os.path.exists(src_dir):
        print 'could not open src_dir %s' % src_dir
        sys.exit(-1)

    print "creating ramdisk -- src_dir: %s" % src_dir

    # set up the temporary files
    rd = "rd.rd"
    rdf = open(rd,"wb")

    directory_file = open("__directory_file","w")

    nfiles = 0
    for f in ls(src_dir):
        add_file(f)
        directory_file.write(f.split('/')[-1:][0] +'\n')
        nfiles += 1
    
    directory_file.close()
    add_file("__directory_file")
    nfiles += 1
    os.system("rm __directory_file")
    
    size = len(data) + len(headers) + 6
    print "%s finished -- size: %dk, files: %d" % (rd_h,size/1024,nfiles)
    if ENDINESS == "LITTLE":
        rdf.write(struct.pack("<LH",0xFF33EE22,nfiles)) # add overall header
    elif ENDINESS == "BIG":
        rdf.write(struct.pack(">LH",0xFF33EE22,nfiles)) # add overall header
    rdf.write(headers)
    rdf.write(data)
    

    #if endiness == "BIG": header = struct.pack(">LL",0xF00F1FF1,12)
    #elif endiness == "LITTLE": header = struct.pack("<LL",0xF00F1FF1,12)
    #else: header = struct.pack("@LL",0xF00F1FF1,12)
    #rd.write(header)

    rdf.close()

    bin2ca(rd,rd_h)
    os.system("rm %s" % rd)

    


