import re
import struct
import math
import os
import time

global vertexesarray
global MCNKindexes
GRID_SIZE = 533.333333333
vertexesarray = []
MCNKindexes = []

def parseTerrain(adtfilename, outputfolder=None, useCASCParser=False, cascfileinput=None):
    global MCNKindexes
    global vertexesarray
    vertexesarray = []
    MCNKindexes = []
    holearray = []
    outputfile = adtfilename.split('.')
    outputfile[-1] = 'obj'
    outputfilename = '.'.join(outputfile)
    if outputfolder != None:
        fixpath = outputfilename.split('\\')[-1]
        outputfilename = outputfolder + fixpath

    mainrowconstant = -4.1666625
    subrowconstant = mainrowconstant / 2
    mystring = 'KNCM'
    if useCASCParser == False:
        f =open(adtfilename, 'rb')
        data = f.read()
    else:
        data = cascfileinput
    foundMCNK = re.finditer(mystring, data)
    if foundMCNK:
        for m in foundMCNK:
            kl = m.span()
            MCNKindexes.append(kl[0])
    print 'Parsing Terrain'
    for i in range(0, len(MCNKindexes)):
        startindex = MCNKindexes[i]
        chunkXIndex = startindex + 0x70
        chunkYIndex = startindex + 0x74
        chunkZIndex = startindex + 0x78
        chunkX = struct.unpack('f', data[chunkXIndex:chunkXIndex + 4])
        chunkY = struct.unpack('f', data[chunkYIndex:chunkYIndex + 4])
        chunkZ = struct.unpack('f', data[chunkZIndex:chunkZIndex + 4])
        #print chunkX[0]
        #print chunkY[0]
        #print chunkZ[0]

        MCVTChunkStart = startindex + 0x88
        floatindex = MCVTChunkStart + 0x8
        firstfloat = struct.unpack('f', data[floatindex:floatindex + 4])
        fixedheight = chunkZ[0] + firstfloat[0]
        fixedvertex = 'v %.7f %.7f %.7f' %(chunkY[0], fixedheight, chunkX[0])
        #fixedvertex = 'v %.7f %.7f %.7f' % (chunkX[0], chunkY[0], fixedheight)
        vertexesarray.append(fixedvertex)
        currentX = chunkX[0]
        currentY = chunkY[0]
        currentZ = chunkZ[0]
        for k in range(0, 17):
            if k == 0:
                for mk in range(0,9):
                    row = k
                    column = mk
                    Xmodifier = row * mainrowconstant
                    goodXmodifier = Xmodifier
                    Ymodifier = column * mainrowconstant
                    if row == 0 and column == 0:
                        pass
                    else:
                        floatindex += 0x4
                        thisfloat = struct.unpack('f', data[floatindex:floatindex + 4])
                        fixedheight = fixedheight + thisfloat[0]
                        fixedvertex = 'v %.7f %.7f %.7f' % (chunkY[0] + Ymodifier, currentZ + thisfloat[0], chunkX[0] + Xmodifier)
                        #fixedvertex = 'v %.7f %.7f %.7f' % (chunkX[0] + Xmodifier, chunkY[0] + Ymodifier, currentZ + thisfloat[0])
                        vertexesarray.append(fixedvertex)
            elif k % 2 != 0:
                for mk in range(0,8):
                    row = k
                    column = mk
                    #Xmodifier = ((row - 1) * mainrowconstant) + subrowconstant
                    Xmodifier = goodXmodifier + subrowconstant
                    Ymodifier = column * mainrowconstant + subrowconstant
                    floatindex += 0x4
                    thisfloat = struct.unpack('f', data[floatindex:floatindex + 4])
                    fixedheight = fixedheight + thisfloat[0]
                    fixedvertex = 'v %.7f %.7f %.7f' % (chunkY[0] + Ymodifier, currentZ + thisfloat[0], chunkX[0] + Xmodifier)
                    #fixedvertex = 'v %.7f %.7f %.7f' % (chunkX[0] + Xmodifier, chunkY[0] + Ymodifier, currentZ + thisfloat[0])
                    vertexesarray.append(fixedvertex)
            else:
                for mk in range(0,9):
                    row = k
                    column = mk
                    #Xmodifier = (row - 2) * mainrowconstant + mainrowconstant
                    Xmodifier = (row / 2) * mainrowconstant
                    goodXmodifier = Xmodifier
                    Ymodifier = column * mainrowconstant
                    floatindex += 0x4
                    thisfloat = struct.unpack('f', data[floatindex:floatindex + 4])
                    fixedheight = fixedheight + thisfloat[0]
                    fixedvertex = 'v %.7f %.7f %.7f' % (chunkY[0] + Ymodifier, currentZ + thisfloat[0], chunkX[0] + Xmodifier)
                    #fixedvertex = 'v %.7f %.7f %.7f' % (chunkX[0] + Xmodifier, chunkY[0] + Ymodifier, currentZ + thisfloat[0])
                    vertexesarray.append(fixedvertex)

        highresholechecker = startindex + 0x1C
        highreshole = data[highresholechecker:highresholechecker + 8]
        highresholeunpack = struct.unpack('q', highreshole)[0]
        if highresholeunpack != 0:
            # print repr(highreshole)
            # print repr(highreshole[::-1])
            mainfileindex = i * 145
            # print index
            # print hex(x)
            # print hex(highresholeunpack)
            # highresholetest = highreshole[::-1]
            for rowindex, x in enumerate(highreshole):
                bitrow = str(bin((struct.unpack('B', x)[0]))[2:])
                newbitrow = bitrow[::-1]
                while len(newbitrow) != 8:
                    newbitrow += '0'
                #print newbitrow
                for columnindex, y in enumerate(newbitrow):
                    if y == '0':
                        pass
                    elif y == '1':
                        centralvertex = mainfileindex + (9 * (rowindex + 1)) + (
                                (rowindex * 8) + columnindex)
                        # print centralvertex
                        # print vertexesarray[centralvertex]
                        holearray.append(centralvertex)
                    else:
                        print 'highreshole value error'

    testfile = open(outputfilename, 'w')
    for item in vertexesarray:
        testfile.write(item + '\n')
    testfile.write('\n')
    testfile.close()
    testfile = open(outputfilename, 'a')
    for ixis in range(0, len(MCNKindexes)):
        startindexio = (ixis * 145)
        if startindexio < 0:
            startindexio == 0
        for malo in range(0,8):
            for epix in range (0,8):
                row = startindexio + 9 * (malo + 1) + malo * 8
                column = epix
                stardconnectingindex = row + column
                if (stardconnectingindex) not in holearray:
                    triangleone = 'f %i %i %i' %((stardconnectingindex + 1), (stardconnectingindex + 1 - 9), (stardconnectingindex + 1 + 8))
                    triangletwo = 'f %i %i %i' % ((stardconnectingindex + 1), (stardconnectingindex + 1 - 8), (stardconnectingindex + 1 - 9))
                    trianglethree = 'f %i %i %i' % ((stardconnectingindex + 1), (stardconnectingindex + 1 + 9), (stardconnectingindex + 1 - 8))
                    trianglefour = 'f %i %i %i' % ((stardconnectingindex + 1), (stardconnectingindex + 1 + 8), (stardconnectingindex + 1 + 9))
                    testfile.write(triangleone + '\n')
                    testfile.write(triangletwo + '\n')
                    testfile.write(trianglethree + '\n')
                    testfile.write(trianglefour + '\n')
                else:
                    print 'highreshole found in vertex %i, triangle not written to file' %(stardconnectingindex + 1)

def parseWater(adtfilename, outputfolder=None, useCASCParser=False, cascfileinput=None):
    global MCNKindexes
    global vertexesarray
    outputfile = adtfilename.split('.')
    outputfile[-1] = 'obj'
    outputfilename = '.'.join(outputfile)
    if outputfolder != None:
        fixpath = outputfilename.split('\\')[-1]
        outputfilename = outputfolder + fixpath
    bluecolor = ' 0.0 0.0 1.0'
    mainfileindex = len(vertexesarray)
    containswater = 0
    watervertexarray = []
    waterfacesarray = []
    vertexchunksize = 145
    mainrowconstant = -4.1666625
    subrowconstant = mainrowconstant / 2
    MCNKindexes = []
    mystring = 'KNCM'
    mystringone = 'O2HM'
    if useCASCParser == False:
        f = open(adtfilename, 'rb')
        data = f.read()
    else:
        data = cascfileinput
    foundMCNK = re.finditer(mystring, data)
    foundMH20 = re.finditer(mystringone, data)
    if foundMCNK:
        for m in foundMCNK:
            kl = m.span()
            MCNKindexes.append(kl[0])
    firstwaterchunklocation = 0
    if foundMH20:
        for m in foundMH20:
            kl = m.span()
            firstwaterchunklocation = kl[0] + 0x8
            break
    print 'Parsing Water'
    if firstwaterchunklocation != 0:
        #MH2Ostart = data[firstwaterchunklocation: firstwaterchunklocation + 4]
        waterchunklocation = firstwaterchunklocation
        checkifwaterexists = data[waterchunklocation: waterchunklocation + 4]
        unpackwatercheck = struct.unpack('i', checkifwaterexists)
        watercheckarray = []
        watercheckarray.append(unpackwatercheck[0])
        for i in range(0, len(MCNKindexes) - 1):
            waterchunklocation += 0xC
            checkifwaterexists = data[waterchunklocation: waterchunklocation + 4]
            unpackwatercheck = struct.unpack('i', checkifwaterexists)
            watercheckarray.append(unpackwatercheck[0])
        waterstring = ''
        rowchecker = 0
        for k in range(0, len(watercheckarray)):
            watervertexarrayindexes = []
            currentvertexindex = k * vertexchunksize
            chunkrow = 1
            if k > 16:
                rowcheck = k
                while rowcheck > 16:
                    rowcheck -= 16
                    chunkrow += 1
                else:
                    chunkcolumn = rowcheck + 1
            else:
                chunkcolumn = k + 1

            if watercheckarray[k] != 0:

                watervertexarrayoffset = containswater * 145

                layercountstruct = firstwaterchunklocation + watercheckarray[k]
                watertype = data[layercountstruct: layercountstruct + 2]
                unpackwatertype = struct.unpack('h', watertype)[0]
                waterbitmapoffset = data[layercountstruct + 0x10: layercountstruct + 0x10 + 4]
                unpackbitmapoffset = struct.unpack('i', waterbitmapoffset)[0]
                vertexdataoffset = data[layercountstruct + 0x14: layercountstruct + 0x14 + 4]
                unpackvertexdataoffset = struct.unpack('i', vertexdataoffset)[0]
                minheightleveloffset = data[layercountstruct + 4: layercountstruct + 4 + 4]
                unpackminheightleveloffset = struct.unpack('f', minheightleveloffset)[0]
                heightoffset = firstwaterchunklocation + unpackvertexdataoffset
                #heightoffsetvalue = data[heightoffset: heightoffset + 4]
                #unpackedheightoffset = struct.unpack('f', heightoffsetvalue)[0]

                #print hex(unpackvertexdataoffset)
                #print unpackedheightoffset
                #print unpackvertexdataoffset

                #checkrandomshit = data[layercountstruct + 0xC + 3: layercountstruct + 0xC + 4]
                #unpackrandomshit = struct.unpack('b', checkrandomshit)[0]
                #print unpackrandomshit

                for ss in range(0, 145):
                    if (ss < 9 and ss >= 0) or (ss < 26 and ss >= 17) or (ss < 43 and ss >= 34) or (ss < 60 and ss >= 51) or (ss < 77 and ss >= 68) or (ss < 94 and ss >= 85) or (ss < 111 and ss >= 102) or (ss < 128 and ss >= 119) or (ss < 145 and ss >= 136):
                        heightoffsetvalue = data[heightoffset: heightoffset + 4]
                        unpackedheightoffset = struct.unpack('f', heightoffsetvalue)[0]
                        #wanted to replace 0 value in heigharrays with minheightlevel but it works fine with 0 there
                        if unpackedheightoffset == 234234234:
                            print 'here'
                            vertexstring = vertexesarray[currentvertexindex + ss]
                            splited = vertexstring.split(' ')
                            splited[2] = str(round(unpackminheightleveloffset, 5))
                            fixedsplited = ' '.join(splited)
                            fixedsplited += bluecolor
                            watervertexarray.append(fixedsplited)
                        else:
                            vertexstring = vertexesarray[currentvertexindex + ss]
                            splited = vertexstring.split(' ')
                            if unpackwatertype != 2:
                                splited[2] = str(round(unpackedheightoffset, 2))
                            else:
                                splited[2] = '0.0'
                            fixedsplited = ' '.join(splited)
                            fixedsplited += bluecolor
                            watervertexarray.append(fixedsplited)
                        heightoffset += 0x4
                    else:
                        vertexstring = vertexesarray[currentvertexindex + ss]
                        splited = vertexstring.split(' ')
                        if unpackwatertype != 2:
                            splited[2] = str(round(unpackminheightleveloffset, 5))
                        else:
                            splited[2] = '0.0'
                        fixedsplited = ' '.join(splited)
                        #fixedsplited = vertexstring
                        fixedsplited += bluecolor
                        watervertexarray.append(fixedsplited)

                generatetesttrianglesfromwatervertices = False
                if unpackbitmapoffset != 0:
                    bitmapfieldstart = data[firstwaterchunklocation + unpackbitmapoffset: firstwaterchunklocation + unpackbitmapoffset + 8]
                    #print 'Chunk row: %i column: %i' %(chunkrow, chunkcolumn)
                    for rowindex, x in enumerate(bitmapfieldstart):
                        bitrow = str(bin((struct.unpack('B', x)[0]))[2:])
                        newbitrow = bitrow[::-1]
                        while len(newbitrow) != 8:
                            newbitrow += '0'
                        #print newbitrow
                        for columnindex, y in enumerate(newbitrow):
                            if y == '0':
                                pass
                            elif y == '1':
                                centralvertex = watervertexarrayoffset + (9 * (rowindex + 1)) + ((rowindex * 8) + columnindex + 1) + mainfileindex
                                #print centralvertex
                                topleftvertex = centralvertex - 9
                                toprightvertex = centralvertex - 8
                                bottomleftvertex = centralvertex + 8
                                bottomrightvertex = centralvertex + 9



                                triangleone = 'f %i %i %i' % ((centralvertex ), (topleftvertex), (bottomleftvertex))
                                triangletwo = 'f %i %i %i' % ((centralvertex ), (toprightvertex), (topleftvertex ))
                                trianglethree = 'f %i %i %i' % ((centralvertex ), (bottomrightvertex), (toprightvertex))
                                trianglefour = 'f %i %i %i' % ((centralvertex), (bottomleftvertex), (bottomrightvertex))

                                waterfacesarray.append(triangleone)
                                waterfacesarray.append(triangletwo)
                                waterfacesarray.append(trianglethree)
                                waterfacesarray.append(trianglefour)
                            else:
                                print 'wrong bitmap value'
                        #print newbitrow

                else:
                    #print mainfileindex
                    #print 'Chunk row: %i column: %i is all in water!' %(chunkrow, chunkcolumn)
                    startindexio = watervertexarrayoffset
                    for malo in range(0, 8):
                        for epix in range(0, 8):
                            row = startindexio + 9 * (malo + 1) + malo * 8
                            column = (epix + 1)
                            stardconnectingindex = row + column + mainfileindex
                            #print stardconnectingindex

                            triangleone = 'f %i %i %i' % ((stardconnectingindex), (stardconnectingindex - 9), (stardconnectingindex + 8))
                            triangletwo = 'f %i %i %i' % ((stardconnectingindex), (stardconnectingindex - 8), (stardconnectingindex - 9))
                            trianglethree = 'f %i %i %i' % ((stardconnectingindex), (stardconnectingindex + 9), (stardconnectingindex - 8))
                            trianglefour = 'f %i %i %i' % ((stardconnectingindex), (stardconnectingindex + 8), (stardconnectingindex + 9))

                            waterfacesarray.append(triangleone)
                            waterfacesarray.append(triangletwo)
                            waterfacesarray.append(trianglethree)
                            waterfacesarray.append(trianglefour)
                    #print k + 1
                    #for watty in range(0, 8):
                        #waterows[watty] += '11111111'
                containswater += 1
                #print containswater
            else:
                pass
                #print 'Chunk row: %i column: %i has no water!' % (chunkrow, chunkcolumn)

        #watertest = open('watertest.obj', 'w')

        #for abc in watervertexarray:
            #watertest.write(abc + '\n')
        #watertest.write('\n')

        #for cxz in waterfacesarray:
            #watertest.write(cxz + '\n')

        #watertest.close()

        writewatertomainfile = open(outputfilename, 'r')
        mainfileread = writewatertomainfile.readlines()
        vertexesend = len(vertexesarray)
        vertexeswritestart = vertexesend
        for abc in watervertexarray:
            mainfileread.insert(vertexesend, abc + '\n')
            vertexesend += 1
        mainfileread.insert(vertexesend, '\n')
        writewatertomainfile.close()

        writewatertomainfile = open(outputfilename, 'w')
        writewatertomainfile.writelines(mainfileread)
        writewatertomainfile.close()


        generatetesttrianglesfromwatervertices = False
        if generatetesttrianglesfromwatervertices == True:

            writewatertomainfile = open(outputfilename, 'a')
            for cxz in waterfacesarray:
                writewatertomainfile.write(cxz + '\n')
            writewatertomainfile.close()

def parseHoles(adtfilename, outputfolder=None):
    global MCNKindexes
    global vertexesarray
    outputfile = adtfilename.split('.')
    outputfile[-1] = 'obj'
    outputfilename = '.'.join(outputfile)
    if outputfolder != None:
        fixpath = outputfilename.split('\\')[-1]
        outputfilename = outputfolder + fixpath
    holearray = []
    f = open(adtfilename, 'rb')
    data = f.read()
    print len(MCNKindexes)
    for index, x in enumerate(MCNKindexes):
        startindex = x
        highresholechecker = startindex + 0x1C
        highreshole = data[highresholechecker:highresholechecker + 8]
        highresholeunpack = struct.unpack('q', highreshole)[0]
        if highresholeunpack != 0:
            #print repr(highreshole)
            #print repr(highreshole[::-1])
            mainfileindex = index * 145
            #print index
            #print hex(x)
            #print hex(highresholeunpack)
            #highresholetest = highreshole[::-1]
            for rowindex, x in enumerate(highreshole):
                bitrow = str(bin((struct.unpack('B', x)[0]))[2:])
                newbitrow = bitrow[::-1]
                while len(newbitrow) != 8:
                    newbitrow += '0'
                #print newbitrow
                for columnindex, y in enumerate(newbitrow):
                    if y == '0':
                        pass
                    elif y == '1':
                        centralvertex = mainfileindex + (9 * (rowindex + 1)) + (
                                (rowindex * 8) + columnindex)
                        #print centralvertex
                        #print vertexesarray[centralvertex]
                        holearray.append(centralvertex)
                    else:
                        print 'highreshole value error'


        lowresholes = startindex + 0x40
        lowreshole = struct.unpack('h', data[lowresholes:lowresholes + 2])[0]
        if lowreshole != 0:
            print 'lowreshole detected!'
            #print index
            #print hex(x)
            #print hex(lowreshole)

    f.close()
    writeholestomainfile = open(outputfilename, 'r')
    mainfileread = writeholestomainfile.readlines()
    #print holearray
    fileholearray = []
    print fileholearray
    print holearray
    print len(mainfileread)
    print len(holearray)
    for holeindex, hole in enumerate(holearray):
        print 'checking hole: %i with index %i. Total holes: %i' %(hole, holeindex, len(holearray))
        for indexios, line in enumerate(mainfileread):
            if (' ' + str(hole) + ' ') in line and 'f' in line:
                fileholearray.append(indexios)
    for xe in fileholearray:
        #print mainfileread[xe]
        mainfileread[xe] = ''
        #print mainfileread[xe]

    #print fileholearray
    #print len(fileholearray)
    #print holearray
    writeholestomainfile.close()
    writeholestomainfile = open(outputfilename, 'w')
    writeholestomainfile.writelines(mainfileread)
    writeholestomainfile.close()


def parseM2(adtfilename, folderpath, filepath, posy, posz, posx, rotationy, rotationz, rotationx, scale, outputfolder=None, useCASCParser=False, cascfileinput=None):
    global MCNKindexes
    global vertexesarray
    outputfile = adtfilename.split('.')
    outputfile[-1] = 'obj'
    outputfilename = '.'.join(outputfile)
    if outputfolder != None:
        fixpath = outputfilename.split('\\')[-1]
        outputfilename = outputfolder + fixpath
    m2trianglearray = []
    m2vertexarray = []
    fileopened = False
    try:
        if useCASCParser == False:
            openm2 = open(folderpath + filepath, 'rb')
        else:
            openm2 = cascfileinput
    except:
        print ('M2 file not found!')
    else:
        if useCASCParser == False:
            readm2 = openm2.read()
        else:
            readm2 = openm2
        foundm2 = re.finditer('MD21', readm2)
        if foundm2:
            for m in foundm2:
                kl = m.span()
                m2index = kl[0]
                break
        else:
            print 'MD21 not found!'

        m2chunkstartoffset = m2index + 0x8


        m2triangleamountaddress = readm2[0xE0:0xE0 + 4]
        m2triangleamount = struct.unpack('i', m2triangleamountaddress)[0]
        m2trianglesoffsetaddress = readm2[0xE4:0xE4 + 4]
        m2trianglesoffset = struct.unpack('i', m2trianglesoffsetaddress)[0]
        m2vertexamountaddress = readm2[0xE8:0xE8 + 4]
        m2vertexamount = struct.unpack('i', m2vertexamountaddress)[0]
        m2vertexoffsetaddress = readm2[0xEC:0xEC + 4]
        m2vertexoffset = struct.unpack('i', m2vertexoffsetaddress)[0]
        #print m2trianglesoffset
        #print m2vertexoffset
        #print m2triangleamount
        #print m2vertexamount
        readtrianglesarray = readm2[m2chunkstartoffset + m2trianglesoffset:m2chunkstartoffset + m2trianglesoffset + 2]
        trianglevalue = struct.unpack('H', readtrianglesarray)[0]
        while len(m2trianglearray) < m2triangleamount:
            m2trianglearray.append(trianglevalue)
            m2trianglesoffset += 2
            readtrianglesarray = readm2[m2chunkstartoffset + m2trianglesoffset:m2chunkstartoffset + m2trianglesoffset + 2]
            trianglevalue = struct.unpack('H', readtrianglesarray)[0]

        readvertexarray = readm2[m2chunkstartoffset + m2vertexoffset:m2chunkstartoffset + m2vertexoffset + 4]
        vertexfloatvalue = struct.unpack('f', readvertexarray)[0]
        while len(m2vertexarray) < (m2vertexamount * 3):
            m2vertexarray.append(vertexfloatvalue)
            m2vertexoffset += 4
            readvertexarray = readm2[m2chunkstartoffset + m2vertexoffset:m2chunkstartoffset + m2vertexoffset + 4]
            vertexfloatvalue = struct.unpack('f', readvertexarray)[0]

        #print m2trianglearray
        #print len(m2trianglearray)
        #print m2vertexarray
        #print len(m2vertexarray)

        if scale != 1024.0:
            fixamount = (scale / 1024.0)
            for fixscaleindex, v in enumerate(m2vertexarray):
                m2vertexarray[fixscaleindex] = m2vertexarray[fixscaleindex] * fixamount


        if rotationz != 0 and len(m2vertexarray)!= 0:
            cosvalue = math.cos(math.radians(rotationz * -1.0))
            sinvalue = math.sin(math.radians(rotationz * -1.0))
            #print rotationz
            #if rotationz < 0:
                #rotationz += 360
            #elif rotationz < 0:
            helpercounter = 0

            for rotationindexfix, v in enumerate(m2vertexarray):
                if helpercounter == 0:
                    currenty = m2vertexarray[rotationindexfix]
                    currentx = m2vertexarray[rotationindexfix + 1]
                    currentz = m2vertexarray[rotationindexfix + 2]
                    #Y
                    #m2vertexarray[rotationindexfix] = posy + (m2vertexarray[rotationindexfix + 1] - posx) * math.cos(rotationz) - (m2vertexarray[rotationindexfix] - posy) * math.sin(rotationz)
                    #m2vertexarray[rotationindexfix] = posy + (m2vertexarray[rotationindexfix + 1] - posx)* math.sin(rotationz) + (m2vertexarray[rotationindexfix] - posy)* math.cos(rotationz)
                    m2vertexarray[rotationindexfix] = (currentx * sinvalue) + (currenty * cosvalue)
                    #m2vertexarray[rotationindexfix] = (m2vertexarray[rotationindexfix + 1] * math.cos(math.radians(1))) - (m2vertexarray[rotationindexfix] * math.sin(math.radians(1)))
                    helpercounter +=1
                elif helpercounter == 1:
                    #X
                    #m2vertexarray[rotationindexfix] = posx + (m2vertexarray[rotationindexfix] - posx) * math.sin(rotationz) + (m2vertexarray[rotationindexfix - 1] - posy) * math.cos(rotationz)
                    #m2vertexarray[rotationindexfix] = posx + (m2vertexarray[rotationindexfix] - posx) * math.cos(rotationz) - (m2vertexarray[rotationindexfix - 1] - posy) * math.sin(rotationz)
                    m2vertexarray[rotationindexfix] = (currentx * cosvalue) - (currenty * sinvalue)
                    #m2vertexarray[rotationindexfix] = (m2vertexarray[rotationindexfix] * math.sin(math.radians(1))) + (m2vertexarray[rotationindexfix - 1] * math.cos(math.radians(1)))
                    helpercounter +=1
                elif helpercounter == 2:
                    #Z
                    helpercounter -= 2
        #print m2vertexarray

        if rotationy != 0 and len(m2vertexarray)!= 0:
            cosvalue = math.cos(math.radians(rotationy * -1.0))
            sinvalue = math.sin(math.radians(rotationy * -1.0))
            #if rotationz > 0:
            #rotationz = -rotationz
            #elif rotationz < 0:
            helpercounter = 0

            for rotationindexfix, v in enumerate(m2vertexarray):
                if helpercounter == 0:
                    #Y
                    currenty = m2vertexarray[rotationindexfix]
                    currentx = m2vertexarray[rotationindexfix + 1]
                    currentz = m2vertexarray[rotationindexfix + 2]
                    helpercounter +=1
                elif helpercounter == 1:
                    #X
                    m2vertexarray[rotationindexfix] = (currentx * cosvalue) + (currentz * sinvalue)
                    helpercounter +=1
                elif helpercounter == 2:
                    #Z
                    m2vertexarray[rotationindexfix] = (-1 * currentx * sinvalue) + (currentz * cosvalue)
                    helpercounter -= 2
        #print m2vertexarray


        if rotationx != 0 and len(m2vertexarray)!= 0:
            cosvalue = math.cos(math.radians(rotationx * -1.0))
            sinvalue = math.sin(math.radians(rotationx * -1.0))
            #if rotationz > 0:
            #rotationz = -rotationz
            #elif rotationz < 0:
            helpercounter = 0

            for rotationindexfix, v in enumerate(m2vertexarray):
                if helpercounter == 0:
                    #Y
                    currenty = m2vertexarray[rotationindexfix]
                    currentx = m2vertexarray[rotationindexfix + 1]
                    currentz = m2vertexarray[rotationindexfix + 2]
                    m2vertexarray[rotationindexfix] = (currenty * cosvalue) - (currentz * sinvalue)
                    helpercounter +=1
                elif helpercounter == 1:
                    #X
                    helpercounter +=1
                elif helpercounter == 2:
                    #Z
                    m2vertexarray[rotationindexfix] = (currenty * sinvalue) + (currentz * cosvalue)
                    helpercounter -= 2
        #print m2vertexarray


        fixvertexpositionhelper = 0
        for indextofix, vex in enumerate(m2vertexarray):
            if fixvertexpositionhelper == 0:
                m2vertexarray[indextofix] = (vex * -1.0) + posx
                fixvertexpositionhelper +=1
            elif fixvertexpositionhelper == 1:
                m2vertexarray[indextofix] = (vex * -1.0) + posy
                fixvertexpositionhelper += 1
            elif fixvertexpositionhelper == 2:
                m2vertexarray[indextofix] = vex + posz
                fixvertexpositionhelper -= 2

        #print m2vertexarray

        if useCASCParser == False:
            openm2.close()
        openm2 = open(outputfilename, 'r')
        checklastvertexpositioninfile = openm2.readlines()
        vertexcounter = 0
        for singleline in checklastvertexpositioninfile:
            if 'v ' in singleline:
                vertexcounter += 1
        #print 'vertex counter is %i' %(vertexcounter)
        temparray = []
        openm2.close()
        openm2 = open(outputfilename, 'a')
        openm2.write('\n')
        for indexone, vertex in enumerate(m2vertexarray):
            if len(temparray) == 0:
                temparray.append('v')
            elif len(temparray) == 4:
                openm2.write(temparray[0] + temparray[2] + temparray[3] + temparray[1] + '\n')
                #openm2.write(temparray[0] + ' ' + str(posy + float(temparray[1])) + ' ' + str(posz + float(temparray[3])) + ' ' + str(posx + float(temparray[2])) + '\n')
                temparray = []
                temparray.append('v')
            #elif len(temparray) == 3:
                #temparray.append(' ' + str(vertex * -1))
                #continue
            temparray.append(' ' + str(vertex))
            if indexone == (len(m2vertexarray) - 1):
                openm2.write(temparray[0] + temparray[2] + temparray[3] + temparray[1] + '\n')
                #openm2.write(temparray[0] + ' ' + str(posy + float(temparray[1])) + ' ' + str(posz + float(temparray[3])) + ' ' + str(posx + float(temparray[2])) + '\n')
                temparray = []
        openm2.write('\n')
        temparray = []
        for indextwo, triangle in enumerate(m2trianglearray):
            if len(temparray) == 0:
                temparray.append('f')
            elif len(temparray) == 4:
                openm2.write(temparray[0] + temparray[1] + temparray[2] + temparray[3] + '\n')
                temparray = []
                temparray.append('f')
            temparray.append(' ' + str(triangle + 1 + vertexcounter))
            if indextwo == (len(m2trianglearray) - 1):
                openm2.write(temparray[0] + temparray[1] + temparray[2] + temparray[3] + '\n')
                temparray = []
        openm2.close()


def parseAllM2(filename, mapfolderlocation, outputfolderpath=None, useCASCParser=False, cascfileinput=None):
    global MCNKindexes
    global vertexesarray
    m2array = []
    if useCASCParser == False:
        fixinputfilename = filename.split('.')
        fixinputfilename[-2] += '_obj0'
        fixedname = '.'.join(fixinputfilename)
        #print fixedname
        openobjfile = open(fixedname, 'rb')
        readobjfile = openobjfile.read()
        openobjfile.close()
    else:
        readobjfile = cascfileinput
    foundMMDX = re.finditer('XDMM', readobjfile)
    if foundMMDX:
        for m in foundMMDX:
            kl = m.span()
            MDDXstart = kl[0]
            firstmddxstring = MDDXstart + 0x8
            break

    foundMMID = re.finditer('DIMM', readobjfile)
    if foundMMID:
        for m in foundMMID:
            kl = m.span()
            MMIDstart = kl[0]
            firstmmid = MMIDstart + 0x8
            break
            #print hex(MMIDstart)

    foundMDDF = re.finditer('FDDM', readobjfile)
    #foundMDDF = re.finditer('DDLM', readobjfile)
    if foundMDDF:
        for m in foundMDDF:
            kl = m.span()
            #print kl[0]
            MDDFstart = kl[0]
            firstmddf = MDDFstart + 0x8
            break
    itemIDaddress = readobjfile[firstmddf:firstmddf + 4]
    itemID = struct.unpack('i', itemIDaddress)[0]
    nextitemoffset = 0
    print 'Parsing All M2'
    while itemIDaddress != 'FDOM':
        temparray = []
        modelname = ''
        mmidaddressoffset = itemID * 4
        mmidaddress = readobjfile[firstmmid + mmidaddressoffset:firstmmid + mmidaddressoffset + 4]
        stringoffset = struct.unpack('i', mmidaddress)[0]
        #print stringoffset
        modelnamestring = readobjfile[firstmddxstring + stringoffset:firstmddxstring + stringoffset + 1]
        while modelnamestring != '\x00':
            modelname += modelnamestring
            stringoffset += 1
            modelnamestring = readobjfile[firstmddxstring + stringoffset:firstmddxstring + stringoffset + 1]
        temparray.append(modelname)
        posyoffset = readobjfile[firstmddf + nextitemoffset + 0x8:firstmddf + nextitemoffset + 0x8 + 4]
        unpackposy = struct.unpack('f', posyoffset)[0]
        poszoffset = readobjfile[firstmddf + nextitemoffset + 0xC:firstmddf + nextitemoffset + 0xC + 4]
        unpackposz = struct.unpack('f', poszoffset)[0]
        posxoffset = readobjfile[firstmddf + nextitemoffset + 0x10:firstmddf + nextitemoffset + 0x10 + 4]
        unpackposx = struct.unpack('f', posxoffset)[0]

        posy = 32 * GRID_SIZE - unpackposy
        posz = unpackposz
        posx = 32 * GRID_SIZE - unpackposx
        #print posy
        #print posz
        #print posx
        temparray.append(posy)
        temparray.append(posz)
        temparray.append(posx)

        rotatioyoffset = readobjfile[firstmddf + nextitemoffset + 0x14:firstmddf + nextitemoffset + 0x14 + 4]
        unpackrotationy = struct.unpack('f', rotatioyoffset)[0]
        rotatiozoffset = readobjfile[firstmddf + nextitemoffset + 0x18:firstmddf + nextitemoffset + 0x18 + 4]
        unpackrotationz = struct.unpack('f', rotatiozoffset)[0]
        rotatioxoffset = readobjfile[firstmddf + nextitemoffset + 0x1C:firstmddf + nextitemoffset + 0x1C + 4]
        unpackrotationx = struct.unpack('f', rotatioxoffset)[0]

        scaleoffset = readobjfile[firstmddf + nextitemoffset + 0x20:firstmddf + nextitemoffset + 0x20 + 4]
        unpackscale = struct.unpack('i', scaleoffset)[0]

        #checkboundingbox = adtinputfile.split('_')
        #checkxcorner = checkboundingbox[2].split('.')
        #startingycorner = 32 * GRID_SIZE - int(checkboundingbox[1]) * GRID_SIZE
        #startingxcorner = 32 * GRID_SIZE - int(checkxcorner[0]) * GRID_SIZE

        #Filter M2 OUTSIDE bounding box of current ADT. However when not generated some weird movements of other M2s
        #occured so I commented it out.

        #if (posy > startingycorner or posy < (startingycorner - GRID_SIZE)) or (posx > startingxcorner or posx < (startingxcorner - GRID_SIZE)):
            #print 'M2 outside bounding box'
            #temparray = []
            #nextitemoffset += 0x24
            #continue

        #print unpackrotationy
        #print unpackrotationz
        #print unpackrotationx

        temparray.append(unpackrotationy)
        temparray.append(unpackrotationz)
        temparray.append(unpackrotationx)
        temparray.append(unpackscale)

        nextitemoffset += 0x24
        itemIDaddress = readobjfile[firstmddf + nextitemoffset:firstmddf + nextitemoffset + 4]
        itemID = struct.unpack('i', itemIDaddress)[0]
        m2array.append(temparray)
        temparray = []

    if useCASCParser == False:
        for item in m2array:
            print item
            if outputfolderpath == None:
                parseM2(filename, mapfolderlocation, item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])
            else:
                parseM2(filename, mapfolderlocation, item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], outputfolderpath)
    else:
        return m2array
    #print len(m2array)


def parseWMO(adtfilename, folderpath, filepath, posy, posz, posx, rotationy, rotationz, rotationx, outputfolder=None, useCASCParser=False, cascfileinput=None):
    global MCNKindexes
    global vertexesarray
    outputfile = adtfilename.split('.')
    outputfile[-1] = 'obj'
    outputfilename = '.'.join(outputfile)
    if outputfolder != None:
        fixpath = outputfilename.split('\\')[-1]
        outputfilename = outputfolder + fixpath
    wmotrianglearray = []
    wmovertexarray = []
    wmotrianglecollisioncheck = []
    if useCASCParser == False:
        openwmo = open(folderpath + filepath, 'rb')
        readwmo = openwmo.read()
        openwmo.close()
    else:
        readwmo = cascfileinput
    foundMOVI = re.finditer('IVOM', readwmo)
    moviindex = 0
    movtindex = 0
    if foundMOVI:
        for m in foundMOVI:
            kl = m.span()
            moviindex = kl[0]
            break
    else:
        print 'MOVI not found'

    foundMOVT = re.finditer('TVOM', readwmo)
    if foundMOVT:
        for m in foundMOVT:
            kl = m.span()
            movtindex = kl[0]
            break
    else:
        print 'MOVT not found'
    mopyindex = 0
    foundMOPY = re.finditer('YPOM', readwmo)
    if foundMOPY:
        for m in foundMOPY:
            kl = m.span()
            mopyindex = kl[0]
            break
    else:
        print 'MOPY not found'
    mogpindex = 0
    foundMOGP = re.finditer('PGOM', readwmo)
    if foundMOGP:
        for m in foundMOGP:
            kl = m.span()
            mogpindex = kl[0]
            break
    else:
        print 'MOGP not found'

    foundmovt = 0
    foundMOVT = re.finditer('VTOM', readwmo)
    if foundMOVT:
        for m in foundMOVT:
            kl = m.span()
            foundmovt = kl[0]
            break
    else:
        print 'MOTV not found'

    checkflags = readwmo[mogpindex + 0x10: mogpindex + 0x10 + 0x4]
    checkflagarray = []
    for bit in checkflags:
        checkbit = struct.unpack('B', bit)[0]
        checkflagarray.append(checkbit)
    #if checkflagarray[0] == 128 and (checkflagarray[3] == 132 or checkflagarray[3] == 68 or checkflagarray[3] == 36 or checkflagarray[3] == 20):
    if checkflagarray[0] == 128:
        print 'This WMO group has Unreachable Flag, aborting!'
    elif foundmovt == 0:
        print 'MOTV chunk not found, WMO group doesnt exist or its antiportal, aborting!'
    else:
        if moviindex != 0 and movtindex != 0:
            movistartaddress = moviindex + 0x4
            trianglescountaddress = readwmo[movistartaddress:movistartaddress + 0x4]
            trianglecount = struct.unpack('i', trianglescountaddress)[0]
            #print trianglecount
            trianglevalueaddress = readwmo[movistartaddress + 0x4:movistartaddress + 0x4 + 0x2]
            trianglevalue = struct.unpack('H', trianglevalueaddress)[0]
            #print trianglevalue

            movtstartaddress = movtindex + 0x4
            vertexescountaddress = readwmo[movtstartaddress:movtstartaddress + 0x4]
            vertexamount = struct.unpack('i', vertexescountaddress)[0]
            #print vertexamount
            vertexvalueaddress = readwmo[movtstartaddress + 0x4: movtstartaddress + 0x4 + 0x4]
            vertexvalue = struct.unpack('f', vertexvalueaddress)[0]
            #print vertexvalue

            nextvertexoffset = 0
            mopystartaddress = mopyindex + 0x8
            trianglecollsiontexturecheckaddress = readwmo[mopystartaddress:mopystartaddress + 0x1]
            trianglecollisioncheck = struct.unpack('B', trianglecollsiontexturecheckaddress)[0]


            while len(wmovertexarray) < (vertexamount / 4):
                wmovertexarray.append(vertexvalue)
                nextvertexoffset += 0x4
                vertexvalueaddress = readwmo[movtstartaddress + 0x4 + nextvertexoffset: movtstartaddress + 0x4 + nextvertexoffset + 0x4]
                vertexvalue = struct.unpack('f', vertexvalueaddress)[0]



            nexttriangleoffset = 0
            nextcollisioncheckoffset = 0
            while len(wmotrianglearray) < (trianglecount / 2):
                wmotrianglearray.append(trianglevalue)
                nexttriangleoffset += 0x2
                trianglevalueaddress = readwmo[movistartaddress + 0x4 + nexttriangleoffset:movistartaddress + 0x4 + nexttriangleoffset + 0x2]
                trianglevalue = struct.unpack('H', trianglevalueaddress)[0]

            while len(wmotrianglecollisioncheck) < (trianglecount / (2 * 3)):
                wmotrianglecollisioncheck.append(trianglecollisioncheck)
                nextcollisioncheckoffset += 0x2
                trianglecollsiontexturecheckaddress = readwmo[mopystartaddress + nextcollisioncheckoffset :mopystartaddress + nextcollisioncheckoffset + 0x1]
                trianglecollisioncheck = struct.unpack('B', trianglecollsiontexturecheckaddress)[0]

            #print wmovertexarray
            #print len(wmovertexarray)
            #print wmotrianglearray
            #print len(wmotrianglearray)
            #print wmotrianglecollisioncheck
            #print len(wmotrianglecollisioncheck)

            countvertexestestfile = 0
            testwmofile = open(outputfilename, 'r')
            readwmofile = testwmofile.readlines()
            for line in readwmofile:
                if 'v ' in line:
                    countvertexestestfile +=1


            if rotationz != 0 and len(wmovertexarray)!= 0:
                cosvalue = math.cos(math.radians(rotationz))
                sinvalue = math.sin(math.radians(rotationz))
                #print rotationz
                #if rotationz < 0:
                    #rotationz += 360
                #elif rotationz < 0:
                helpercounter = 0

                for rotationindexfix, v in enumerate(wmovertexarray):
                    if helpercounter == 0:
                        currenty = wmovertexarray[rotationindexfix + 1]
                        currentx = wmovertexarray[rotationindexfix]
                        currentz = wmovertexarray[rotationindexfix + 2]
                        #X
                        wmovertexarray[rotationindexfix] = (currentx * cosvalue) - (currenty * sinvalue)
                        helpercounter +=1
                    elif helpercounter == 1:
                        #Y
                        wmovertexarray[rotationindexfix] = (currentx * sinvalue) + (currenty * cosvalue)
                        helpercounter +=1
                    elif helpercounter == 2:
                        #Z
                        helpercounter -= 2
            #print m2vertexarray

            if rotationy != 0 and len(wmovertexarray)!= 0:
                cosvalue = math.cos(math.radians(rotationy))
                sinvalue = math.sin(math.radians(rotationy))
                #if rotationz > 0:
                #rotationz = -rotationz
                #elif rotationz < 0:
                helpercounter = 0

                for rotationindexfix, v in enumerate(wmovertexarray):
                    if helpercounter == 0:
                        #X
                        currenty = wmovertexarray[rotationindexfix + 1]
                        currentx = wmovertexarray[rotationindexfix]
                        currentz = wmovertexarray[rotationindexfix + 2]
                        wmovertexarray[rotationindexfix] = (currentx * cosvalue) + (currentz * sinvalue)
                        helpercounter +=1
                    elif helpercounter == 1:
                        #Y
                        helpercounter +=1
                    elif helpercounter == 2:
                        #Z
                        wmovertexarray[rotationindexfix] = (-1 * currentx * sinvalue) + (currentz * cosvalue)
                        helpercounter -= 2
            #print m2vertexarray


            if rotationx != 0 and len(wmovertexarray)!= 0:
                cosvalue = math.cos(math.radians(rotationx))
                sinvalue = math.sin(math.radians(rotationx))
                #if rotationz > 0:
                #rotationz = -rotationz
                #elif rotationz < 0:
                helpercounter = 0

                for rotationindexfix, v in enumerate(wmovertexarray):
                    if helpercounter == 0:
                        #X
                        currenty = wmovertexarray[rotationindexfix + 1]
                        currentx = wmovertexarray[rotationindexfix]
                        currentz = wmovertexarray[rotationindexfix + 2]
                        helpercounter +=1
                    elif helpercounter == 1:
                        #Y
                        wmovertexarray[rotationindexfix] = (currenty * cosvalue) - (currentz * sinvalue)
                        helpercounter +=1
                    elif helpercounter == 2:
                        #Z
                        wmovertexarray[rotationindexfix] = (currenty * sinvalue) + (currentz * cosvalue)
                        helpercounter -= 2
            #print m2vertexarray



            fixvertexpositionhelper = 0
            for indextofix, vex in enumerate(wmovertexarray):
                if fixvertexpositionhelper == 0:
                    wmovertexarray[indextofix] = (vex * -1.0) + posx
                    fixvertexpositionhelper +=1
                elif fixvertexpositionhelper == 1:
                    wmovertexarray[indextofix] = (vex * -1.0) + posy
                    fixvertexpositionhelper += 1
                elif fixvertexpositionhelper == 2:
                    wmovertexarray[indextofix] = vex + posz
                    fixvertexpositionhelper -= 2


            testwmofile = open(outputfilename, 'a')

            counter = 0
            temparray = []
            for index, x in enumerate(wmovertexarray):
                if counter == 0:
                    temparray.append('v')
                    temparray.append(str(x))
                    counter += 1
                elif counter == 1:
                    temparray.append(str(x))
                    counter += 1
                elif counter == 2:
                    temparray.append(str(x))
                    testwmofile.write(temparray[0] + ' ' + temparray[2] + ' ' + temparray[3] + ' ' + temparray[1] + '\n')
                    temparray = []
                    counter -= 2

            testwmofile.write('\n')

            counter = 0
            tempstring = ''
            for index, x in enumerate(wmotrianglearray):
                if counter == 0:
                    #if index == 0:
                        #if wmotrianglecollisioncheck[index] == 102:
                            #print 'Collision Triangle detected, removing it'
                            #index += 2
                            #continue
                    #else:
                        #if wmotrianglecollisioncheck[index / 3] == 102:
                            #print 'Collision Triangle detected, removing it'
                            #index += 2
                            #continue
                    tempstring = 'f'
                    tempstring += ' '
                    tempstring += str(x + 1 + countvertexestestfile)
                    counter += 1
                elif counter == 1:
                    tempstring += ' '
                    tempstring += str(x + 1 + countvertexestestfile)
                    counter += 1
                elif counter == 2:
                    tempstring += ' '
                    tempstring += str(x + 1 + countvertexestestfile)
                    tempstring += '\n'
                    testwmofile.write(tempstring)
                    counter -= 2
            testwmofile.write('\n')


def parseAllWMO(filename, mapfolderlocation, outputfolderpath=None, highlevelofdetails=False, useCASCParser=False, cascfileinput=None):
    global MCNKindexes
    global vertexesarray
    wmoarray = []
    fixinputfilename = filename.split('.')
    fixinputfilename[-2] += '_obj0'
    fixedname = '.'.join(fixinputfilename)
    #print fixedname
    if useCASCParser == False:
        openobjfile = open(fixedname, 'rb')
        readobjfile = openobjfile.read()
        openobjfile.close()
    else:
        readobjfile = cascfileinput
    foundMWMO = re.finditer('OMWM', readobjfile)
    if foundMWMO:
        for m in foundMWMO:
            kl = m.span()
            MWMOstart = kl[0]
            firstmwmostring = MWMOstart + 0x8
            #print hex(MWMOstart)
            break

    foundMWID = re.finditer('DIWM', readobjfile)
    if foundMWID:
        for m in foundMWID:
            kl = m.span()
            MWIDstart = kl[0]
            firstmwid = MWIDstart + 0x8
            #print hex(MWIDstart)
            break

    foundMODF = re.finditer('FDOM', readobjfile)
    #foundMDDF = re.finditer('DDLM', readobjfile)
    if foundMODF:
        for m in foundMODF:
            kl = m.span()
            MODFstart = kl[0]
            firstmodf = MODFstart + 0x8
            #print hex(MODFstart)
            break
    itemIDaddress = readobjfile[firstmodf:firstmodf + 4]
    itemID = struct.unpack('i', itemIDaddress)[0]
    nextitemoffset = 0
    print 'Parsing All WMO'
    while itemID != 'KNCM' and itemIDaddress != 'KNCM':
        temparray = []
        modelname = ''
        mwidaddressoffset = itemID * 4
        #print mwidaddressoffset
        #print itemID
        mwiddaddress = readobjfile[firstmwid + mwidaddressoffset:firstmwid + mwidaddressoffset + 4]
        #print mwiddaddress
        stringoffset = struct.unpack('i', mwiddaddress)[0]
        #print stringoffset
        modelnamestring = readobjfile[firstmwmostring + stringoffset:firstmwmostring + stringoffset + 1]
        while modelnamestring != '\x00':
            modelname += modelnamestring
            stringoffset += 1
            modelnamestring = readobjfile[firstmwmostring + stringoffset:firstmwmostring + stringoffset + 1]
        temparray.append(modelname)
        posyoffset = readobjfile[firstmodf + nextitemoffset + 0x8:firstmodf + nextitemoffset + 0x8 + 4]
        unpackposy = struct.unpack('f', posyoffset)[0]
        poszoffset = readobjfile[firstmodf + nextitemoffset + 0xC:firstmodf + nextitemoffset + 0xC + 4]
        unpackposz = struct.unpack('f', poszoffset)[0]
        posxoffset = readobjfile[firstmodf + nextitemoffset + 0x10:firstmodf + nextitemoffset + 0x10 + 4]
        unpackposx = struct.unpack('f', posxoffset)[0]

        posy = 32 * GRID_SIZE - unpackposy
        posz = unpackposz
        posx = 32 * GRID_SIZE - unpackposx
        #print posy
        #print posz
        #print posx
        temparray.append(posy)
        temparray.append(posz)
        temparray.append(posx)

        rotatioyoffset = readobjfile[firstmodf + nextitemoffset + 0x14:firstmodf + nextitemoffset + 0x14 + 4]
        unpackrotationy = struct.unpack('f', rotatioyoffset)[0]
        rotatiozoffset = readobjfile[firstmodf + nextitemoffset + 0x18:firstmodf + nextitemoffset + 0x18 + 4]
        unpackrotationz = struct.unpack('f', rotatiozoffset)[0]
        rotatioxoffset = readobjfile[firstmodf + nextitemoffset + 0x1C:firstmodf + nextitemoffset + 0x1C + 4]
        unpackrotationx = struct.unpack('f', rotatioxoffset)[0]


        #checkboundingbox = adtinputfile.split('_')
        #checkxcorner = checkboundingbox[2].split('.')
        #startingycorner = 32 * GRID_SIZE - int(checkboundingbox[1]) * GRID_SIZE
        #startingxcorner = 32 * GRID_SIZE - int(checkxcorner[0]) * GRID_SIZE

        #Filter M2 OUTSIDE bounding box of current ADT. However when not generated some weird movements of other M2s
        #occured so I commented it out.

        #if (posy > startingycorner or posy < (startingycorner - GRID_SIZE)) or (posx > startingxcorner or posx < (startingxcorner - GRID_SIZE)):
            #print 'M2 outside bounding box'
            #temparray = []
            #nextitemoffset += 0x24
            #continue

        #print unpackrotationy
        #print unpackrotationz
        #print unpackrotationx

        temparray.append(unpackrotationy)
        temparray.append(unpackrotationz)
        temparray.append(unpackrotationx)

        nextitemoffset += 0x40
        itemIDaddress = readobjfile[firstmodf + nextitemoffset:firstmodf + nextitemoffset + 4]
        itemID = struct.unpack('i', itemIDaddress)[0]
        wmoarray.append(temparray)
        temparray = []
    if useCASCParser == True:
        return wmoarray
    for itemnumber, item in enumerate(wmoarray):
        print item[0]
        firstwmostringsplit = item[0].split('\\')
        wmofilename = firstwmostringsplit[-1]
        #print wmofilename
        del firstwmostringsplit[-1]
        fixedfolderwmopath = '\\'.join(firstwmostringsplit)
        realfolderpath = mapfolderlocation + fixedfolderwmopath
        allfiles = os.listdir(realfolderpath)
        #print allfiles
        counter = 0
        for index, file in enumerate(allfiles):
            #print file
            #print wmofilename
            if file.lower() == wmofilename.lower():
                startindex = index
                counter += 1
        #del allfiles[0]
        #print allfiles
        #print startindex
        for indexio, fileee in enumerate(allfiles):
            #print indexio
            #print (wmofilename.split('.')[0] + '_').lower()
            if counter == 0:
                print 'Missing file: %s' %(item[0])
                break
            if indexio == startindex:
                continue
            if indexio > startindex:
                if highlevelofdetails == True:
                    if ((((wmofilename.split('.')[0] + '_0').lower() in fileee.lower())) or \
                        ((wmofilename.split('.')[0] + '_0').lower() not in fileee.lower() and (wmofilename.split('.')[0] + '_1').lower() in fileee.lower()) or \
                        ((wmofilename.split('.')[0] + '_0').lower() not in fileee.lower() and (wmofilename.split('.')[0] + '_2').lower() in fileee.lower()) or \
                        ((wmofilename.split('.')[0] + '_0').lower() not in fileee.lower() and (wmofilename.split('.')[0] + '_3').lower() in fileee.lower()) or \
                            ((wmofilename.split('.')[0] + '_0').lower() not in fileee.lower() and (wmofilename.split('.')[0] + '_4').lower() in fileee.lower())):
                        wmochunkfilepath = fixedfolderwmopath + '\\' + fileee
                        print ("%s, %f, %f, %f, %f, %f, %f") % (
                        wmochunkfilepath, item[1], item[2], item[3], item[4], item[5], item[6])
                        if outputfolderpath == None:
                            parseWMO(filename, mapfolderlocation, wmochunkfilepath, item[1], item[2], item[3], item[4], item[5], item[6])
                        else:
                            parseWMO(filename, mapfolderlocation, wmochunkfilepath, item[1], item[2], item[3], item[4], item[5], item[6], outputfolderpath)
                else:
                    if ((((wmofilename.split('.')[0] + '_0').lower() in fileee.lower())) or \
                        ((wmofilename.split('.')[0] + '_0').lower() not in fileee.lower() and (wmofilename.split('.')[0] + '_1').lower() in fileee.lower()) or \
                        ((wmofilename.split('.')[0] + '_0').lower() not in fileee.lower() and (wmofilename.split('.')[0] + '_2').lower() in fileee.lower()) or \
                        ((wmofilename.split('.')[0] + '_0').lower() not in fileee.lower() and (wmofilename.split('.')[0] + '_3').lower() in fileee.lower()) or \
                        ((wmofilename.split('.')[0] + '_0').lower() not in fileee.lower() and (wmofilename.split('.')[0] + '_4').lower() in fileee.lower())) \
                            and '_lod'.lower() not in fileee.lower() and '.blp'.lower() not in fileee.lower():
                        wmochunkfilepath = fixedfolderwmopath + '\\' + fileee
                        print ("%s, %f, %f, %f, %f, %f, %f") %(wmochunkfilepath, item[1], item[2], item[3], item[4], item[5], item[6])
                        if outputfolderpath == None:
                            parseWMO(filename, mapfolderlocation, wmochunkfilepath, item[1], item[2], item[3], item[4], item[5], item[6])
                        else:
                            parseWMO(filename, mapfolderlocation, wmochunkfilepath, item[1], item[2], item[3], item[4],item[5], item[6], outputfolderpath)
        #write portal faces, dont use it, broken.
        #if outputfolderpath == None:
            #removePortalsInWMO(filename, mapfolderlocation, fixedfolderwmopath + '\\' + wmofilename, item[1], item[2], item[3], item[4], item[5], item[6])
        #else:
            #removePortalsInWMO(filename, mapfolderlocation, fixedfolderwmopath + '\\' + wmofilename, item[1], item[2], item[3], item[4], item[5], item[6], outputfolderpath)

    #print len(m2array)


def removePortalsInWMO(adtfilename, folderpath, filepath, posy, posz, posx, rotationy, rotationz, rotationx, outputfolder=None):
    global MCNKindexes
    global vertexesarray
    portalverticesarray = []
    outputfile = adtfilename.split('.')
    outputfile[-1] = 'obj'
    outputfilename = '.'.join(outputfile)
    if outputfolder != None:
        fixpath = outputfilename.split('\\')[-1]
        outputfilename = outputfolder + fixpath
    openwmo = open(folderpath + filepath, 'rb')
    readwmo = openwmo.read()
    openwmo.close()
    foundMOVP = re.finditer('VPOM', readwmo)
    foundMOPT = re.finditer('TPOM', readwmo)
    movpindex = 0
    if foundMOVP:
        for m in foundMOVP:
            kl = m.span()
            movpstartaddress = kl[0]
            movpindex = kl[0] + 0x8
            break
    if foundMOPT:
        for m in foundMOPT:
            kl = m.span()
            moptstartaddress = kl[0]
            moptindex = kl[0] + 0x8
            break
    moptindexcheck = readwmo[moptindex:moptindex +0x4]
    totalvertexcount = 0
    vertexcountarray = []
    if movpstartaddress != 0 and moptstartaddress != 0:
        while moptindexcheck != 'RPOM':
            startingvertexindexaddress = readwmo[moptindex: moptindex + 2]
            startingvertexindex = (struct.unpack('H', startingvertexindexaddress)[0])
            vertexcountaddress = readwmo[moptindex + 2: moptindex + 2 + 2]
            vertexcount = struct.unpack('H', vertexcountaddress)[0]
            vertexcountarray.append(vertexcount)
            firstportalfloataddress = readwmo[movpindex + startingvertexindex:movpindex + startingvertexindex + 4]
            firstfloat = struct.unpack('f', firstportalfloataddress)[0]
            portalverticesarray.append(firstfloat)

            startingvertexindex = startingvertexindex * 3 * vertexcount

            nextvertex = 0x4
            totalvertexcount += vertexcount
            fakecounter = 0
            while fakecounter < ((vertexcount * 3) - 1):
                floataddress = readwmo[movpindex + startingvertexindex + nextvertex:movpindex + startingvertexindex + nextvertex + 0x4]
                floatvalue = struct.unpack('f', floataddress)[0]
                portalverticesarray.append(floatvalue)
                nextvertex += 0x4
                fakecounter += 1
            moptindex += 0x14
            moptindexcheck = readwmo[moptindex:moptindex + 0x4]

        if rotationz != 0 and len(portalverticesarray)!= 0:
            cosvalue = math.cos(math.radians(rotationz))
            sinvalue = math.sin(math.radians(rotationz))
            #print rotationz
            #if rotationz < 0:
                #rotationz += 360
            #elif rotationz < 0:
            helpercounter = 0

            for rotationindexfix, v in enumerate(portalverticesarray):
                if helpercounter == 0:
                    currenty = portalverticesarray[rotationindexfix + 1]
                    currentx = portalverticesarray[rotationindexfix]
                    currentz = portalverticesarray[rotationindexfix + 2]
                    #X
                    portalverticesarray[rotationindexfix] = (currentx * cosvalue) - (currenty * sinvalue)
                    helpercounter +=1
                elif helpercounter == 1:
                    #Y
                    portalverticesarray[rotationindexfix] = (currentx * sinvalue) + (currenty * cosvalue)
                    helpercounter +=1
                elif helpercounter == 2:
                    #Z
                    helpercounter -= 2
        #print m2vertexarray

        if rotationy != 0 and len(portalverticesarray)!= 0:
            cosvalue = math.cos(math.radians(rotationy))
            sinvalue = math.sin(math.radians(rotationy))
            #if rotationz > 0:
            #rotationz = -rotationz
            #elif rotationz < 0:
            helpercounter = 0

            for rotationindexfix, v in enumerate(portalverticesarray):
                if helpercounter == 0:
                    #X
                    currenty = portalverticesarray[rotationindexfix + 1]
                    currentx = portalverticesarray[rotationindexfix]
                    currentz = portalverticesarray[rotationindexfix + 2]
                    portalverticesarray[rotationindexfix] = (currentx * cosvalue) + (currentz * sinvalue)
                    helpercounter +=1
                elif helpercounter == 1:
                    #Y
                    helpercounter +=1
                elif helpercounter == 2:
                    #Z
                    portalverticesarray[rotationindexfix] = (-1 * currentx * sinvalue) + (currentz * cosvalue)
                    helpercounter -= 2
        #print m2vertexarray


        if rotationx != 0 and len(portalverticesarray)!= 0:
            cosvalue = math.cos(math.radians(rotationx))
            sinvalue = math.sin(math.radians(rotationx))
            #if rotationz > 0:
            #rotationz = -rotationz
            #elif rotationz < 0:
            helpercounter = 0

            for rotationindexfix, v in enumerate(portalverticesarray):
                if helpercounter == 0:
                    #X
                    currenty = portalverticesarray[rotationindexfix + 1]
                    currentx = portalverticesarray[rotationindexfix]
                    currentz = portalverticesarray[rotationindexfix + 2]
                    helpercounter +=1
                elif helpercounter == 1:
                    #Y
                    portalverticesarray[rotationindexfix] = (currenty * cosvalue) - (currentz * sinvalue)
                    helpercounter +=1
                elif helpercounter == 2:
                    #Z
                    portalverticesarray[rotationindexfix] = (currenty * sinvalue) + (currentz * cosvalue)
                    helpercounter -= 2
        #print m2vertexarray



        fixvertexpositionhelper = 0
        for indextofix, vex in enumerate(portalverticesarray):
            if fixvertexpositionhelper == 0:
                portalverticesarray[indextofix] = (vex * -1.0) + posx
                fixvertexpositionhelper +=1
            elif fixvertexpositionhelper == 1:
                portalverticesarray[indextofix] = (vex * -1.0) + posy
                fixvertexpositionhelper += 1
            elif fixvertexpositionhelper == 2:
                portalverticesarray[indextofix] = vex + posz
                fixvertexpositionhelper -= 2

        createportallines = []
        temparray = []
        portalvertexcount = 0

        openwmo = open(outputfilename, 'rb')
        readwmolines = openwmo.readlines()
        openwmo.close()
        vertexcounter = 0
        for indexcount, vert in enumerate(readwmolines):
            if 'v ' in vert:
                vertexcounter += 1
        print vertexcounter

        openwmo = open(outputfilename, 'a')
        openwmo.write('\n')

        for portalvertex in portalverticesarray:
            if portalvertexcount == 0:
                temparray.append('v')
                temparray.append(str(portalvertex))
                portalvertexcount += 1
            elif portalvertexcount == 1:
                temparray.append(str(portalvertex))
                portalvertexcount += 1
            elif portalvertexcount == 2:
                temparray.append(str(portalvertex))
                openwmo.write(temparray[0] + ' ' + temparray[2] + ' ' + temparray[3] + ' ' + temparray[1] + '\n')
                temparray = []
                portalvertexcount -= 2
        #for portalindex, portallines in enumerate(readwmolines):
            #if portallines in createportallines:
                #print portalindex + 1
        openwmo.write('\n')


        for shape in vertexcountarray:
            illusioncounter = 0
            illusionfacearray = []
            while shape > illusioncounter:
                illusioncounter += 1
                if len(illusionfacearray) == 0:
                    illusionfacearray.append('f')
                illusionfacearray.append('' + str(vertexcounter + 1))
                vertexcounter += 1
            else:
                illusionfacearray.append('\n')
                openwmo.write(' '.join(illusionfacearray))
        openwmo.close()
        #time.sleep(300022)



def parseallADTindirectory(mainfolderpath, outputfolderpath, startfolderindex=0, endfolderindex=9999,overwritefiles=True, highlevelofdetails=False):
    global MCNKindexes
    global vertexesarray
    directorylist = os.listdir(mainfolderpath)
    overwritefilelist = os.listdir(outputfolderpath)
    if 'World' in directorylist:
        newlist = os.listdir(mainfolderpath + 'World\\')
        if 'Maps' in newlist:
            mainmapdirectorypath = mainfolderpath + 'World\\' + 'Maps\\'
            openmainmapdirectory = os.listdir(mainmapdirectorypath)
            for folderindex, mapfolder in enumerate(openmainmapdirectory):
                if startfolderindex <= folderindex and endfolderindex > folderindex:
                    currentmapfolder = os.listdir(mainmapdirectorypath + mapfolder)
                    for file in currentmapfolder:
                        fileexists = False
                        if overwritefiles == False:
                            for filetocheck in overwritefilelist:
                                if filetocheck.split('.')[0] in file:
                                    if '.adt' in file and '_obj0' not in file and '_obj1' not in file and '_tex0' not in file and '_lod' not in file:
                                        print '%s already exists in output folder, skipping parsing of %s' %(filetocheck, file)
                                    fileexists = True
                                    continue
                        if '.adt' in file and '_obj0' not in file and '_obj1' not in file and '_tex0' not in file and '_lod' not in file and fileexists==False:
                            adtfilestringinput = mainmapdirectorypath + mapfolder + '\\' + file
                            print adtfilestringinput
                            vertexesarray = []
                            MCNKindexes = []
                            parseTerrain(adtfilestringinput, outputfolderpath)
                            parseWater(adtfilestringinput, outputfolderpath)
                            #parseHoles(adtfilestringinput, outputfolderpath)
                            parseAllM2(adtfilestringinput, mainfolderpath, outputfolderpath)
                            if highlevelofdetails == False:
                                parseAllWMO(adtfilestringinput, mainfolderpath, outputfolderpath, False)
                            else:
                                parseAllWMO(adtfilestringinput, mainfolderpath, outputfolderpath, True)

global containlowresholes
containlowresholes = []
def holesChecker(adtfilename):
    global containlowresholes
    MCNKindexesfix = []
    mystring = 'KNCM'
    f =open(adtfilename, 'rb')
    data = f.read()
    foundMCNK = re.finditer(mystring, data)
    if foundMCNK:
        for m in foundMCNK:
            kl = m.span()
            MCNKindexesfix.append(kl[0])
    for i in range(0, len(MCNKindexesfix)):
        startindex = MCNKindexesfix[i]
        highresholechecker = startindex + 0x1C
        highreshole = data[highresholechecker:highresholechecker + 8]
        highresholeunpack = struct.unpack('q', highreshole)[0]
        #if highresholeunpack != 0:
            #print 'file %s contains at least 1 hole, remaking it!' %(adtfilename)
            #return True

        lowresholes = startindex + 0x40
        lowreshole = struct.unpack('h', data[lowresholes:lowresholes + 2])[0]
        if lowreshole != 0:
            print 'lowreshole detected!'
            containlowresholes.append(adtfilename)
    return False





def fixHoles(mainfolderpath, outputfolderpath, startfolderindex=0, endfolderindex=9999):
    global MCNKindexes
    global vertexesarray
    directorylist = os.listdir(mainfolderpath)
    overwritefilelist = os.listdir(outputfolderpath)
    if 'World' in directorylist:
        newlist = os.listdir(mainfolderpath + 'World\\')
        if 'Maps' in newlist:
            mainmapdirectorypath = mainfolderpath + 'World\\' + 'Maps\\'
            openmainmapdirectory = os.listdir(mainmapdirectorypath)
            for folderindex, mapfolder in enumerate(openmainmapdirectory):
                if startfolderindex <= folderindex and endfolderindex > folderindex:
                    currentmapfolder = os.listdir(mainmapdirectorypath + mapfolder)
                    for file in currentmapfolder:
                        fileexists = False
                        for filetocheck in overwritefilelist:
                            if filetocheck.split('.')[0] in file:
                                if '.adt' in file and '_obj0' not in file and '_obj1' not in file and '_tex0' not in file and '_lod' not in file:
                                    print '%s file exists, checking holes!' %(filetocheck.split('.')[0])
                                fileexists = True
                        if '.adt' in file and '_obj0' not in file and '_obj1' not in file and '_tex0' not in file and '_lod' not in file and fileexists == True:
                            adtfilestringinput = mainmapdirectorypath + mapfolder + '\\' + file
                            fixholesinfile = holesChecker(adtfilestringinput)
                            if fixholesinfile == True and fileexists == True:
                                print adtfilestringinput
                                vertexesarray = []
                                MCNKindexes = []
                                parseTerrain(adtfilestringinput, outputfolderpath)
                                parseWater(adtfilestringinput, outputfolderpath)
                                #parseHoles(adtfilestringinput, outputfolderpath)
                                parseAllM2(adtfilestringinput, mainfolderpath, outputfolderpath)
                                parseAllWMO(adtfilestringinput, mainfolderpath, outputfolderpath)




def fixOver100WMO():
    global MCNKindexes
    global vertexesarray
    print 'Getting WMO with over 100 groups for fixing and obj0 file list...'
    mapfolderpath = 'E:\\MapsLegion\\'
    outputfolder = 'E:\\MapsObjParserOutput\\'
    over100wmoarray = []
    objfilestocheckarray = []
    for path, subdirs, files in os.walk('E:\\MapsLegion\\'):
        for name in files:
            if '_100' in name and '.wmo' in name.lower():
                filetofix = os.path.join(path, name)
                over100wmoarray.append(filetofix)
            elif '_obj0.adt' in name.lower():
                filetocheck = os.path.join(path, name)
                objfilestocheckarray.append(filetocheck)

    fixedfilenamesarray = []
    for filetofixx in over100wmoarray:
        tempstring = filetofixx[14:]
        flipstring = tempstring[::-1]
        anothertempstring = flipstring[8:]
        flipagain = anothertempstring[::-1]
        flipagain += '.wmo'
        fixedfilenamesarray.append(flipagain)
    objarraywithbadfiles = []
    for objfile in objfilestocheckarray:
        print objfile
        openobjfile = open(objfile, 'rb')
        readobjfile = openobjfile.read()
        openobjfile.close()
        foundMWMO = re.finditer('OMWM', readobjfile)
        if foundMWMO:
            for m in foundMWMO:
                kl = m.span()
                MWMOstart = kl[0]
                firstmwmostring = MWMOstart + 0x8
                # print hex(MWMOstart)
                break

        foundMWID = re.finditer('DIWM', readobjfile)
        if foundMWID:
            for m in foundMWID:
                kl = m.span()
                MWIDstart = kl[0]
                firstmwid = MWIDstart + 0x8
                # print hex(MWIDstart)
                break

        foundMODF = re.finditer('FDOM', readobjfile)
        # foundMDDF = re.finditer('DDLM', readobjfile)
        if foundMODF:
            for m in foundMODF:
                kl = m.span()
                MODFstart = kl[0]
                firstmodf = MODFstart + 0x8
                # print hex(MODFstart)
                break
        itemIDaddress = readobjfile[firstmodf:firstmodf + 4]
        itemID = struct.unpack('i', itemIDaddress)[0]
        nextitemoffset = 0
        while itemID != 'KNCM' and itemIDaddress != 'KNCM':
            temparray = []
            modelname = ''
            mwidaddressoffset = itemID * 4
            # print mwidaddressoffset
            # print itemID
            mwiddaddress = readobjfile[firstmwid + mwidaddressoffset:firstmwid + mwidaddressoffset + 4]
            # print mwiddaddress
            stringoffset = struct.unpack('i', mwiddaddress)[0]
            # print stringoffset
            modelnamestring = readobjfile[firstmwmostring + stringoffset:firstmwmostring + stringoffset + 1]
            while modelnamestring != '\x00':
                modelname += modelnamestring
                stringoffset += 1
                modelnamestring = readobjfile[firstmwmostring + stringoffset:firstmwmostring + stringoffset + 1]
            for checkwmo in fixedfilenamesarray:
                if modelname.lower() == checkwmo.lower():
                    print 'MODELNAME FOUND!!!'
                    objarraywithbadfiles.append(objfile)
                    break
            nextitemoffset += 0x40
            itemIDaddress = readobjfile[firstmodf + nextitemoffset:firstmodf + nextitemoffset + 4]
            itemID = struct.unpack('i', itemIDaddress)[0]

    for xoxx in objarraywithbadfiles:
        MCNKindexes = []
        vertexesarray = []
        flipflip = xoxx[::-1]
        splitflip = flipflip[9:]
        flipagainn = splitflip[::-1]
        flipagainn += '.adt'
        print flipagainn
        parseTerrain(flipagainn, outputfolder)
        parseWater(flipagainn, outputfolder)
        parseAllM2(flipagainn, mapfolderpath, outputfolder)
        parseAllWMO(flipagainn, mapfolderpath, outputfolder)


#fixOver100WMO()
#lowreshole ['E:\\MapsLegion\\World\\Maps\\BlackrookHoldArena\\BlackrookHoldArena_28_29.adt']
#fixHoles('E:\\MapsLegion\\', 'E:\\MapsObjParserOutput\\', 0, 9999999)
#print containlowresholes
#626 FOLDERS TOTAL
#parseallADTindirectory('E:\\MapsLegion\\', 'E:\\MapsObjParserOutput\\', 617, 700, True)
#adtinputfile = 'Azeroth_32_48.adt'
#adtinputfile = 'Kalimdor_40_28.adt'
#mapfolderpath = 'E:\\MapsLegion\\'


#parseTerrain(adtinputfile)
#parseWater(adtinputfile)
#parseHoles(adtinputfile)
#for isx in range(61, 62):
    #if isx != 31:
        #if isx >= 10:
    #parseWMO(adtinputfile, mapfolderpath, 'World\wmo\Azeroth\Buildings\Stormwind\SW_CathedralDistrict_0' + str(isx) + '.wmo', 539.293620, 101.957008, -8931.638021, 0.0, 38.500000, 0.0)
        #else:
            #parseWMO(adtinputfile, mapfolderpath,'World\wmo\Azeroth\Buildings\Stormwind\SW_TradeDistrict_00' + str(isx) + '.wmo', 539.293620, 101.957008, -8931.638021, 0.0, 38.500000, 0.0)
#parseM2('Azeroth_32_48.adt', mapfolderpath, 'WORLD\\AZEROTH\\ELWYNN\\PASSIVEDOODADS\\TREES\\ELWYNNTREECANOPY03.M2', -174.83138021899867, 78.15018463134766, -9011.440755218999, 0.0, 232.0, 0.0)#parseAllM2(adtinputfile, mapfolderpath)
#parseAllM2(adtinputfile, mapfolderpath)
#parseAllWMO(adtinputfile, mapfolderpath)
#stringpath = 'World\\WMO\\AZEROTH\\BUILDINGS\\NSABBEY\\NSabbey_000.wmo'
#stringsplit = stringpath.split('_')
#for i in range(0, 13):
    #if i < 10:
        #stringsplited = stringsplit
        #stringsplited[1] = '00' + str(i) + '.wmo'
        #joinstring = '_'.join(stringsplited)
   # else:
        #stringsplited = stringsplit
        #stringsplited[1] = '0' + str(i) + '.wmo'
        #joinstring = '_'.join(stringsplited)
    #print joinstring
    #parseWMO(adtinputfile, mapfolderpath, joinstring)
    #parseWMO(adtinputfile, mapfolderpath, stringsplited)

#print hex(jenkins.hashlittle('World\Generic\PassiveDoodads\Misc\WheelBarrow\Wheelbarrow_cave01_128.blp', 128))
#thisvariable = salsa20.XSalsa20_xor(testtest, '6FA0420E902B4FBE', '27B750184E5329C4E4455CBD3E1FD5AB')


#CASCTester()


#CASCParser.getMapNames('C:\\World of Warcraft\\')
