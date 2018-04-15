import zlib
import os
import re
import struct
import jenkins
import time
import urllib2
import urllib
import hashlib
import requests

from multiprocess.dummy import Pool as ThreadPool

from ctypes import *
from ctypes.wintypes import *
import psutil
import win32security
import win32process


global hashkeyarray
global firstbytearray
global beuint32array
global sizeofdataarray
global indiciesarray
global md5contenthashes
global md5idxheaders
global rootmd5contentarray
global blizzhashfilekeyrootarray
global firststringblock
global secondarraymd5idxheaders
global secondarraystringblockoneindexes
global realindexmd5hashes
global realindexesfilesizes
global realindexesfileoffsets
global realindexesdatafilesnumbers
global areindiciesparsed

indiciesarray = []
hashkeyarray = []
firstbytearray = []
beuint32array = []
sizeofdataarray = []
md5contenthashes = []
md5idxheaders = []
rootmd5contentarray = []
blizzhashfilekeyrootarray = []
firststringblock = []
secondarraymd5idxheaders = []
secondarraystringblockoneindexes = []
areindiciesparsed = False



Psapi = WinDLL('Psapi.dll')

OpenProcess = windll.kernel32.OpenProcess
ReadProcessMemory = windll.kernel32.ReadProcessMemory
CloseHandle = windll.kernel32.CloseHandle
EnumProcessModulesEx = Psapi.EnumProcessModulesEx

PROCESS_ALL_ACCESS = 0x1F0FFF
READ_CONTROL = (0x00020000 | 0x0400 | 0x0010)

ReadProcessMemory.argtypes = [HANDLE, LPCVOID, LPVOID, c_size_t, POINTER(c_size_t)]
ReadProcessMemory.restype = BOOL

EnumProcessModulesEx.restype = c_bool
EnumProcessModulesEx.argtypes = [c_void_p, POINTER(c_void_p), c_ulong, POINTER(c_ulong), c_int]

def get_client_pid(process_name):
    pid = None
    wowpids = []
    for proc in psutil.process_iter():
        if proc.name() == process_name:
            pid = int(proc.pid)
            print "Found, PID = " + str(pid)
            wowpids.append(pid)
    if len(wowpids) > 1:
        print "Multiple processes found, choose one"
        while True:
            for wow in wowpids:
                print wow
                question = raw_input("Choose this process? Y/N ")
                if question == 'Y':
                    return wow
                elif question == 'N':
                    continue
                else:
                    print "Incorrect answer, try again"
                    break
    return pid


def setProcessHandle(pid, privilages=READ_CONTROL):
    processHandle = OpenProcess(privilages, False, pid)
    print 'Process Handle is %i' %(processHandle)
    return processHandle

def getBaseAddress(handle):
    processarray = (c_void_p *2056)()
    bytesReader = c_ulong()
    enumprocess = EnumProcessModulesEx(handle, processarray, sizeof(processarray), byref(bytesReader), 0x02)

    for module in processarray:
        getfilename = win32process.GetModuleFileNameEx(handle, module)
        if "Wow-64.exe" in getfilename and module != None:
            baseaddressraw = hex(module)
            baseaddressrawnoL = baseaddressraw.rstrip("L")
            baseaddress = int(baseaddressrawnoL, 16)
            return baseaddress


def readCASCData(firstbyte, beuint32, sizeofdata, mainwowfolderpath):
    shiftleft = firstbyte << 32
    oringtogether = shiftleft | beuint32
    thirtybitmask = 0x3fffffff
    realoffsetvalue = thirtybitmask & oringtogether
    datafilenumber = oringtogether >> 30

    if datafilenumber < 10:
        datafilenumber = '0' + str(datafilenumber)

    encodedfile = encodeBLTEFile(datafilenumber, realoffsetvalue, sizeofdata, mainwowfolderpath)
    return encodedfile


def encodeBLTEFile(datafilenumber,realoffsetvalue ,sizeofdata ,mainwowfolderpath,streamdata=False):
    compressedSizeArray = []
    if streamdata == False:
        realdatafilepath = mainwowfolderpath + 'Data\\data\\data.0' + str(datafilenumber)
        if sizeofdata != 0:
            with open(realdatafilepath, 'rb') as opendata:
                opendata.seek(realoffsetvalue)
                opendatapart = opendata.read(sizeofdata)
        else:
            with open(realdatafilepath, 'rb') as opendata:
                opendata.seek(realoffsetvalue)
                opendatapart = opendata.read()
    else:
        cdnfile = urllib2.urlopen('http://us.patch.battle.net:1119/wow/cdns')
        cdnfilecontent = cdnfile.read()
        goodcdnpart = ''
        splitcdnfile = cdnfilecontent.split('\n')
        for stringpart in splitcdnfile:
            if 'us' + '|' in stringpart:
                goodcdnpart = stringpart
                break
        getcdnurlarray = goodcdnpart.split('|')

        getsecondurlpart = getcdnurlarray[1]
        getfirsturlpart = getcdnurlarray[2].split(' ')[0]
        datafilename = datafilenumber

        url = 'http://%s/%s/data/%s/%s/%s' %(getfirsturlpart, getsecondurlpart, datafilename[:2], datafilename[2:4], datafilename)
        headers = {"Range": "bytes=%i-%i" %(realoffsetvalue, realoffsetvalue + sizeofdata)}
        getstreamdata = requests.get(url, headers=headers)
        opendatapart = getstreamdata.content

    foundBLTE = re.finditer('BLTE', opendatapart)
    BLTEarray = []
    firstBLTEoffset = 0
    if foundBLTE:
        for m in foundBLTE:
            kl = m.span()
            BLTEarray.append(kl[0])

    firstBLTEoffset = BLTEarray[0]
    if foundBLTE != 0:
        BLTEHeaderSizeAddress = opendatapart[firstBLTEoffset + 0x4:firstBLTEoffset + 0x4 + 4]
        BLTEHeaderSize = struct.unpack('>I', BLTEHeaderSizeAddress)[0]

        if BLTEHeaderSize == 0:
            fakefile = ''
            readunpackcode = opendatapart[firstBLTEoffset + 0x4 + 4:firstBLTEoffset + 0x4 + 4 + 1]
            thisdatachunk = opendatapart[firstBLTEoffset + 0x4 + 4 + 1:firstBLTEoffset + 0x4 + 4 + sizeofdata]
            if readunpackcode == 'Z':
                #print 'Zlib data detected'
                thisdatachunk = zlib.decompress(thisdatachunk)
            elif readunpackcode == 'N':
                #print 'plain data detected'
                pass
            elif readunpackcode == 'F':
                print 'data in recursivly encoded'
            elif readunpackcode == 'E':
                print 'data in encrypted'
            #print len(thisdatachunk)
            fakefile += thisdatachunk

            temporarydatafile = open('tempfile', 'wb')
            temporarydatafile.write(fakefile)
            temporarydatafile.close()
            return fakefile

        else:
            chunkCountAddress = opendatapart[firstBLTEoffset + 0x4 + 5:firstBLTEoffset + 0x4 + 8]
            unpackfirstchunkcountbyte = struct.unpack('B', chunkCountAddress[0])[0]
            if unpackfirstchunkcountbyte == 0:
                chunkCount = struct.unpack('>H', chunkCountAddress[1:])[0]
            else:
                secondChunkCountPart = struct.unpack('>H', chunkCountAddress[1:])[0]
                chunkCount = int(str(unpackfirstchunkcountbyte) + str(secondChunkCountPart))

            chunkInfoStart = firstBLTEoffset + 0xC
            nextoffsetvalue = 0



            while len(compressedSizeArray) < chunkCount:
                compressedSizeAddress = opendatapart[chunkInfoStart + nextoffsetvalue: chunkInfoStart + nextoffsetvalue + 4]
                compressedSize = struct.unpack('>I', compressedSizeAddress)[0]
                compressedSizeArray.append(compressedSize)
                nextoffsetvalue += 0x18
            remainingdatasize = sizeofdata
            for index, chunk in enumerate(compressedSizeArray):
                if sizeofdata != 0:
                    remainingdatasize -= chunk
                    if remainingdatasize <= 0:
                        finalindex = index
                        datasizeoflastchunk = remainingdatasize + chunk
                        break
                    elif index == (len(compressedSizeArray) - 1):
                        finalindex = index
                        datasizeoflastchunk = chunk
                else:
                    finalindex = len(compressedSizeArray) - 1
                    datasizeoflastchunk = compressedSizeArray[len(compressedSizeArray) - 1]
            firstDataChunkAddress = firstBLTEoffset + BLTEHeaderSize
            comulativechunksize = 0
            fakefile = ''
            for indexio, chunky in enumerate(compressedSizeArray):
                if finalindex >= indexio:
                    readunpackcode = opendatapart[firstDataChunkAddress + comulativechunksize:firstDataChunkAddress + comulativechunksize + 1]
                    thisdatachunk = opendatapart[firstDataChunkAddress + comulativechunksize + 1:firstDataChunkAddress + comulativechunksize + chunky]
                    if indexio == finalindex:
                        thisdatachunk = opendatapart[firstDataChunkAddress + comulativechunksize + 1:firstDataChunkAddress + comulativechunksize + datasizeoflastchunk]
                    comulativechunksize += chunky
                    if readunpackcode == 'Z':
                        thisdatachunk = zlib.decompress(thisdatachunk)
                    elif readunpackcode == 'N':
                        pass
                        #print 'plain data detected'
                    elif readunpackcode == 'F':
                        print 'data in recursivly encoded'
                    elif readunpackcode == 'E':
                        print 'data in encrypted'
                    fakefile += thisdatachunk

            print 'Length of file is: %i' %(len(fakefile))
            temporarydatafile = open('tempfile', 'wb')
            temporarydatafile.write(fakefile)
            temporarydatafile.close()
            return fakefile



def parseAllIDX(mainwowfolderpath):

    global hashkeyarray
    global firstbytearray
    global beuint32array
    global sizeofdataarray
    global indiciesarray
    global idxdictionary

    idxdictionary = {}
    indiciesarray = []
    hashkeyarray = []
    firstbytearray = []
    beuint32array = []
    sizeofdataarray = []
    maindatafolderpath = mainwowfolderpath + 'Data\\data\\'
    filelist = os.listdir(maindatafolderpath)
    idxfilearray = []
    for filee in filelist:
        if '.idx' in filee:
            idxfilearray.append(filee)
    print len(idxfilearray)
    for idxfile in idxfilearray:
        print idxfile
        openidx = open(maindatafolderpath + idxfile, 'rb')
        readidx = openidx.read()
        openidx.close()
        entriesSizeAddress = readidx[0x20:0x20 + 4]
        unpackEntriesSize = struct.unpack('I', entriesSizeAddress)[0]
        entriesStart = 0x28
        currentOffset = 0
        while currentOffset < unpackEntriesSize:
            hashKeyAddress = readidx[entriesStart + currentOffset:entriesStart + currentOffset + 9]
            temporalstring = ''
            tempbytearray = []

            for index, char in enumerate(hashKeyAddress):
                tempbyte = hex(struct.unpack('B', char)[0])
                tempbytearray.append(struct.unpack('B', char)[0])
                tempstring = tempbyte[2:]
                if len(tempstring) == 1:
                    tempstring = '0' + tempstring
                temporalstring += tempstring
            hashkeyarray.append(temporalstring)

            somenumber = tempbytearray[0] ^ tempbytearray[1] ^ tempbytearray[2] ^ tempbytearray[3] ^ tempbytearray[4] ^ tempbytearray[5] ^ tempbytearray[6] ^ tempbytearray[7] ^ tempbytearray[8]
            indicienumber = (somenumber & 0xf) ^ (somenumber >> 4)
            indiciesarray.append(indicienumber)

            firstByteAddress = readidx[entriesStart + currentOffset + 9:entriesStart + currentOffset + 10]
            unpackFirstByte = struct.unpack('B', firstByteAddress)[0]
            firstbytearray.append(unpackFirstByte)

            beunit32Address = readidx[entriesStart + currentOffset + 10:entriesStart + currentOffset + 14]
            unpackbeuint32 = struct.unpack('>I', beunit32Address)[0]
            beuint32array.append(unpackbeuint32)

            sizeOfdDataAddress = readidx[entriesStart + currentOffset + 14:entriesStart + currentOffset + 18]
            unpackSizeOfData = struct.unpack('I', sizeOfdDataAddress)[0]
            sizeofdataarray.append(unpackSizeOfData)

            idxdictionary[temporalstring] = [unpackFirstByte, unpackbeuint32, unpackSizeOfData, indicienumber]

            currentOffset += 0x12

def getEncodingFile(encodingcdnhash, mainwowfolder):
    global hashkeyarray
    for index, key in enumerate(hashkeyarray):
        if key in encodingcdnhash:
            print 'Encoding File found in IDX'
            encodingindexinidx = index
    encodingfile = readCASCData(firstbytearray[encodingindexinidx], beuint32array[encodingindexinidx], sizeofdataarray[encodingindexinidx], mainwowfolder)
    return encodingfile


def getEncodingFileWRONG(encodedhash, mainwowfolderpath):
    #WRONG APROACH, DONT USE IT!
    hashbytearray = []
    if len(encodedhash) == 31:
        encodedhash = '0' + encodedhash
    if len(encodedhash) == 32:
        hashcounter = 0
        while len(hashbytearray) < 16:
            hashbytearray.append(encodedhash[hashcounter:hashcounter + 2])
            hashcounter += 2
        bytestring = ''
        for value in hashbytearray:
            fixedbyte = '\\x' + value
            bytestring += fixedbyte
        print bytestring
        print repr(bytestring)
        maindatafolderpath = mainwowfolderpath + 'Data\\data\\'
        filelist = os.listdir(maindatafolderpath)
        datafilearray = []
        for filee in filelist:
            if 'data.' in filee:
                datafilearray.append(filee)
        for datafile in datafilearray:
            completedatapath = maindatafolderpath + datafile
            print 'Parsing Data File: %s' %(completedatapath)
            opendatafile = open(completedatapath, 'rb')
            readdata = opendatafile.read()
            opendatafile.close()
            foundEncodingFile = re.finditer(bytestring, readdata)
            encodingFileArray = []
            if foundEncodingFile:
                for m in foundEncodingFile:
                    kl = m.span()
                    encodingFileArray.append(kl[0])
            if len(encodingFileArray) == 0:
                continue
            else:
                datafileflip = datafile[::-1]
                slicedataoffset = datafileflip[:2]
                flipdataback = slicedataoffset[::-1]
                realencodingfile = encodeBLTEFile(flipdataback, encodingFileArray[0], 0, mainwowfolderpath)
                return realencodingfile

def parseEncodingFile(encodingfile, parseextrarrays=False):
    global md5contenthashes
    global md5idxheaders
    global firststringblock
    global secondarraymd5idxheaders
    global secondarraystringblockoneindexes
    global encodingdictionary

    encodingdictionary = {}
    md5contenthashes = []
    md5idxheaders = []
    firststringblock = []
    secondarraymd5idxheaders = []
    secondarraystringblockoneindexes = []

    foundEN = re.finditer('EN', encodingfile)
    foundENarray = []
    if foundEN:
        for m in foundEN:
            kl = m.span()
            foundENarray.append(kl[0])
    if len(foundENarray) == 0:
        print 'Encoding File Header not found.'
    else:
        encodingFileStart = foundENarray[0]

        firstArrayLengthAddress = encodingfile[encodingFileStart + 0x9:encodingFileStart + 0xD]
        firstArrayLength = struct.unpack('>I', firstArrayLengthAddress)[0]

        secondArrayLengthAddress = encodingfile[encodingFileStart + 0xD:encodingFileStart + 0x11]
        secondArrayLength = struct.unpack('>I', secondArrayLengthAddress)[0]

        #Skip 1 byte between secondArray and firstStringBlock lengths

        firstStringBlockLengthAddress = encodingfile[encodingFileStart + 0x12:encodingFileStart + 0x16]
        firstStringBlockLength = struct.unpack('>I', firstStringBlockLengthAddress)[0]

        firstArrayBlockStart = encodingFileStart + 0x16 + firstStringBlockLength + (firstArrayLength * 0x20)

        blockOffset = 0x1000
        for block in range(0, firstArrayLength):
            currentBlockOffset = block * blockOffset
            offsetValue = 0
            keyNumberAddress = encodingfile[firstArrayBlockStart:firstArrayBlockStart + 1]
            keyNumber = struct.unpack('B', keyNumberAddress)[0]
            while keyNumber != 0:
                md5ContentHashAddress = encodingfile[firstArrayBlockStart + currentBlockOffset + offsetValue + 6: firstArrayBlockStart + currentBlockOffset + offsetValue + 0x16]
                fakecontenthashstring = ''
                for byte in md5ContentHashAddress:
                    unpackByte = hex(struct.unpack('B', byte)[0])
                    cuthex = unpackByte[2:]
                    if len(cuthex) == 1:
                        cuthex = '0' + cuthex
                    fakecontenthashstring += cuthex
                md5contenthashes.append(fakecontenthashstring)

                md5IdxHeaderAddress = encodingfile[firstArrayBlockStart + currentBlockOffset + offsetValue + 0x16: firstArrayBlockStart + currentBlockOffset + offsetValue + 0x26]
                fakebytestring = ''
                for byte in md5IdxHeaderAddress:
                    unpackByte = hex(struct.unpack('B', byte)[0])
                    cuthex = unpackByte[2:]
                    if len(cuthex) == 1:
                        cuthex = '0' + cuthex
                    fakebytestring += cuthex
                md5idxheaders.append(fakebytestring)
                encodingdictionary[fakecontenthashstring] = fakebytestring

                if keyNumber > 1:
                    for key in range(0, keyNumber - 1):
                        offsetValue += 0x10
                        md5IdxHeaderAddress = encodingfile[firstArrayBlockStart + currentBlockOffset + offsetValue + 0x16: firstArrayBlockStart + currentBlockOffset + offsetValue + 0x26]
                        fakebytestring = ''
                        for byte in md5IdxHeaderAddress:
                            unpackByte = hex(struct.unpack('B', byte)[0])
                            cuthex = unpackByte[2:]
                            if len(cuthex) == 1:
                                cuthex = '0' + cuthex
                            fakebytestring += cuthex
                        md5idxheaders.append(fakebytestring)
                        md5contenthashes.append(fakecontenthashstring)
                        encodingdictionary[fakecontenthashstring] = fakebytestring
                offsetValue += 0x26
                keyNumberAddress = encodingfile[firstArrayBlockStart + currentBlockOffset + offsetValue:firstArrayBlockStart + currentBlockOffset + offsetValue + 1]
                keyNumber = struct.unpack('B', keyNumberAddress)[0]
        if parseextrarrays == True:

            firstStringBlockContent = encodingfile[encodingFileStart + 0x16:encodingFileStart + 0x16 + firstStringBlockLength]
            firststringarraynotfinished = firstStringBlockContent.split('\x00')

            secondArrayBlockStart = firstArrayBlockStart + (blockOffset * firstArrayLength) + (0x20 * secondArrayLength)
            for block in range(0, secondArrayLength):
                currentBlockOffset = block * blockOffset
                offsetValue = 0
                for entrtyy in range(0, 163):
                    if len(md5contenthashes) >= len(secondarraymd5idxheaders):
                        md5hashentry = encodingfile[secondArrayBlockStart + currentBlockOffset + offsetValue:secondArrayBlockStart + currentBlockOffset + offsetValue + 0x10]
                        fakestring = ''
                        for byte in md5hashentry:
                            unpackByte = hex(struct.unpack('B', byte)[0])
                            cuthex = unpackByte[2:]
                            if len(cuthex) == 1:
                                cuthex = '0' + cuthex
                            fakestring += cuthex
                        secondarraymd5idxheaders.append(fakestring)

                        stringIndexAddress = encodingfile[secondArrayBlockStart + currentBlockOffset + offsetValue + 0x10:secondArrayBlockStart + currentBlockOffset + offsetValue + 0x14]
                        unpackStringIndexOffset = struct.unpack('>I', stringIndexAddress)[0]
                        secondarraystringblockoneindexes.append(unpackStringIndexOffset)
                        offsetValue += 0x19


            for entry in firststringarraynotfinished:
                if 'b' in entry:
                    cutfront = entry[3:]
                    fliponce = cutfront[::-1]
                    cutback = fliponce[1:]
                    flipback = cutback[::-1]
                    if '{' not in flipback:
                        realdatapart = flipback.split(',')
                        firststringblock.append(realdatapart)
                    else:
                        realdatapart = flipback.split(':')
                        firststringblock.append(realdatapart)
                else:
                    pass




def getRootFile(roothash, mainwowfolderpath):
    global md5contenthashes
    global md5idxheaders
    global hashkeyarray
    global firstbytearray
    global beuint32array
    global sizeofdataarray

    encodingrootindex = None
    idxrootindex = None

    for indexx, hashh in enumerate(md5contenthashes):
        if hashh == roothash:
            print 'Found Root Location in Encoding'
            encodingrootindex = indexx
            print hashh

    if encodingrootindex != None:
        rootidxheader = md5idxheaders[encodingrootindex]
        print rootidxheader
        for indexio, hashik in enumerate(hashkeyarray):
            if hashik in rootidxheader:
                print 'Found Root Location in IDX'
                idxrootindex = indexio

    if idxrootindex != None:
        rootfile = readCASCData(firstbytearray[idxrootindex], beuint32array[idxrootindex], sizeofdataarray[idxrootindex], mainwowfolderpath)
        return rootfile

def parseRootFile(rootfile, specificlocale=None):
    global rootmd5contentarray
    global blizzhashfilekeyrootarray
    global rootdictionary

    rootdictionary = {}
    rootmd5contentarray = []
    blizzhashfilekeyrootarray = []
    globaloffset = 0
    localeFlag = 0
    localestartoffsetarray = []
    if specificlocale != None:
        flagstocheck = ''
        binarynumber = str(bin(int(specificlocale, 16)))[2:]
        while len(binarynumber) < 32:
            binarynumber = '0' + binarynumber
        flagstocheck += binarynumber
        print 'Checking for flags: %s' %(flagstocheck)
    while globaloffset < len(rootfile):
        if specificlocale == None:
            numberOfRootEntriesAddress = rootfile[globaloffset:globaloffset + 4]
            numberOfRootEntries = struct.unpack('I', numberOfRootEntriesAddress)[0]
            localestartoffsetarray.append(globaloffset)
            globaloffset += (0xC + (numberOfRootEntries * 4) + (numberOfRootEntries * 0x18))
            continue
        else:
            numberOfRootEntriesAddress = rootfile[globaloffset:globaloffset + 4]
            numberOfRootEntries = struct.unpack('I', numberOfRootEntriesAddress)[0]
            localContentFlagAddress = rootfile[globaloffset + 4:globaloffset + 8]
            localcontentflag = ''
            for index, byteee in enumerate(localContentFlagAddress):
                thisbyte = struct.unpack('B', byteee)[0]
                if index == 0:
                    localcontentflag += hex(thisbyte)
                else:
                    cuthex = hex(thisbyte)[2:]
                    if len(cuthex) == 1:
                        cuthex = '0' + cuthex
                    localcontentflag += cuthex
            localeFlagAddress = rootfile[globaloffset + 8:globaloffset + 0xC]
            flipLocaleFlags = localeFlagAddress[::-1]
            localeFlag = ''
            for bytee in flipLocaleFlags:
                binarynumber = str(bin(struct.unpack('B', bytee)[0]))[2:]
                while len(binarynumber) < 8:
                    binarynumber = '0' + binarynumber
                localeFlag += binarynumber
        for indexes, flag in enumerate(flagstocheck):
            if (flag == '1') and (localeFlag[indexes] == '1'):
                localestartoffsetarray.append(globaloffset)
                break
        globaloffset += (0xC + (numberOfRootEntries * 4) + (numberOfRootEntries * 0x18))

    if numberOfRootEntries <= 0:
        print 'Incorrect Root File Provided'
    else:
        for globaloffset in localestartoffsetarray:
            localOffset = 0
            numberOfRootEntriesAddress = rootfile[globaloffset:globaloffset + 4]
            numberOfRootEntries = struct.unpack('I', numberOfRootEntriesAddress)[0]
            localOffset += 0xC + (numberOfRootEntries * 4)

            for entry in range(0, numberOfRootEntries):
                rootMd5ContentAddress = rootfile[globaloffset + localOffset:globaloffset + localOffset + 0x10]
                fakemd5contentstring = ''
                for byte in rootMd5ContentAddress:
                    unpackByte = hex(struct.unpack('B', byte)[0])
                    cuthex = unpackByte[2:]
                    if len(cuthex) == 1:
                        cuthex = '0' + cuthex
                    fakemd5contentstring += cuthex
                rootmd5contentarray.append(fakemd5contentstring)

                blizzHashFileKeyAddress = rootfile[globaloffset + localOffset + 0x10:globaloffset + localOffset + 0x18]
                fakeblizzhashfilestring = ''
                reversedBlizzHashFile = blizzHashFileKeyAddress[::-1]
                for byte in reversedBlizzHashFile:
                    unpackByte = hex(struct.unpack('B', byte)[0])
                    cuthex = unpackByte[2:]
                    if len(cuthex) == 1:
                        cuthex = '0' + cuthex
                    fakeblizzhashfilestring += cuthex
                blizzhashfilekeyrootarray.append(fakeblizzhashfilestring)
                localOffset += 0x18
                rootdictionary[fakeblizzhashfilestring] = fakemd5contentstring

        print 'Root Entries for current locale: %i' %(len(blizzhashfilekeyrootarray))




def jenkins96(string):
    c, b = jenkins.hashlittle2(string)
    firsthashfix = c << 32
    realhash = firsthashfix | b
    return realhash


def Blizzhash(string, fixstring=True):
    if fixstring == True:
        fixedstring = string.upper()
        if '/' in string:
            fixedstring = fixedstring.replace('/', '\\')
        if '//' in string:
            fixedstring = fixedstring.replace('//', '\\')
    else:
        fixedstring = string
    stringhash = hex(jenkins96(fixedstring))
    cutfirstpart = stringhash[2:]
    reverseonce = cutfirstpart[::-1]
    cutsecondpart = reverseonce[1:]
    reversesecondtime = cutsecondpart[::-1]
    while len(reversesecondtime) < 16:
        reversesecondtime = '0' + reversesecondtime

    return reversesecondtime


def initializeNecessaryArrays(encodingCDNHash, rootEncodedHash, mainwowfolder, specificlocale=None):
    print 'Initializing necessary data/hash arrays'

    print 'Parsing IDX Files'
    parseAllIDX(mainwowfolder)
    print 'Gettting Encoding File'
    encodingfile = getEncodingFile(encodingCDNHash, mainwowfolder)
    print 'Parsing Encoding'
    parseEncodingFile(encodingfile)
    print 'Gettting Root File'
    rootfile = getRootFile(rootEncodedHash, mainwowfolder)
    print 'Parsing Root FIle'
    if specificlocale == None:
        parseRootFile(rootfile)
    else:
        parseRootFile(rootfile, specificlocale)

    print 'Initialization Completed!'


def parseWoWFileTest(namefromlistfile, mainwowfolder, fixstring=True):
    global rootdictionary
    global idxdictionary
    global encodingdictionary

    if len(blizzhashfilekeyrootarray) == 0:
        print 'Root blizzhash array is empty, remaking it'
        root, encoding = getEncodingAndRootFromLocalFiles(mainwowfolder)
        initializeNecessaryArrays(encoding, root, mainwowfolder, '0x202')


    if fixstring == True:
        filehashname = Blizzhash(namefromlistfile)
    else:
        filehashname = Blizzhash(namefromlistfile, False)

    if filehashname in rootdictionary:
        encodinghash = rootdictionary[filehashname]
    else:
        print 'Blizzhash not found in root'
        return None

    if encodinghash in encodingdictionary:
        idxhash = encodingdictionary[encodinghash]
        print 'IDXhash is %s' %(idxhash)
        shortidxhash = idxhash[:18]
    else:
        print 'Encoding hash not found in encoding'
        return None

    if shortidxhash in idxdictionary:
        paramsarray = idxdictionary[shortidxhash]
        parsefile = readCASCData(paramsarray[0], paramsarray[1], paramsarray[2],mainwowfolder)
        print 'File Parsed Successfully!'
        return parsefile




def parseWoWFile(namefromlistfile, mainwowfolder, fixstring=True, returnparamsarray=False):
    global hashkeyarray
    global firstbytearray
    global beuint32array
    global sizeofdataarray
    global indiciesarray
    global md5contenthashes
    global md5idxheaders
    global rootmd5contentarray
    global blizzhashfilekeyrootarray
    global areindiciesparsed
    global realindexmd5hashes
    global realindexesfilesizes
    global realindexesfileoffsets
    global realindexesdatafilesnumbers
    global areindiciesparsed

    if len(blizzhashfilekeyrootarray) == 0:
        print 'Root blizzhash array is empty, remaking it'
        root, encoding = getEncodingAndRootFromLocalFiles(mainwowfolder)
        initializeNecessaryArrays(encoding, root, mainwowfolder, '0x202')

    if fixstring == True:
        filehashname = Blizzhash(namefromlistfile)
    else:
        filehashname = Blizzhash(namefromlistfile, False)
    rootindex = None
    encodingindex = None
    idxindex = None
    cdnindex = None
    rootlocalblizzhashearray = []
    rootlocalemd5array = []

    for index, filehash in enumerate(blizzhashfilekeyrootarray):
        if filehashname == filehash:
            rootlocalblizzhashearray.append(index)

    if len(rootlocalblizzhashearray) == 0:
        print 'Blizzhash not found in root blizzhashfilekeyrootarray!'
        print filehashname
        return None
    else:
        for rootindex in rootlocalblizzhashearray:
            contenthash = rootmd5contentarray[rootindex]
            for indexx, md5hash in enumerate(md5contenthashes):
                if md5hash == contenthash:
                    rootlocalemd5array.append(indexx)
    if len(rootlocalemd5array) == 0:
        print 'Content hash was not found in md5contenthashesarray'
        return None
    else:
        for encodingindex in rootlocalemd5array:
            idxfullhash = md5idxheaders[encodingindex]
            for indexxx, idxhash in enumerate(hashkeyarray):
                if idxhash.lower() in idxfullhash.lower():
                    idxindex = indexxx
                    print 'Found, IDXIndex: %i' % (idxindex)
                    break
    if idxindex == None:
        print 'Header not found in idxhasharray'
        print 'IDX Fullhash: %s' %(idxfullhash)
        fakearray = []
        currentoffset = 0
        while len(fakearray) < 10:
            fixhex = '0x' + idxfullhash[currentoffset:currentoffset + 2]
            fakearray.append(int(fixhex, 16))
            currentoffset += 2
        somenumber = fakearray[0] ^ fakearray[1] ^ fakearray[2] ^ fakearray[3] ^ fakearray[4] ^ fakearray[5] ^ fakearray[6] ^ fakearray[7] ^ fakearray[8]
        indicienumber = (somenumber & 0xf) ^ (somenumber >> 4)

        if areindiciesparsed == False:
            print 'CDN Config not parsed, parsing...'
            parseCDNConfig(mainwowfolder)
        print 'Trying to find header in CDN indicies'
        for encodingindex in rootlocalemd5array:
            fullhash = md5idxheaders[encodingindex]
            for indexxxx, hashik in enumerate(realindexmd5hashes):
                if fullhash == hashik:
                    cdnindex = indexxxx
                    print 'Found matching hash!'
                    break
        if cdnindex == None:
            print 'Header not found in realindexmd5hashes'
            return None
        else:
            parsefile = encodeBLTEFile(realindexesdatafilesnumbers[cdnindex], realindexesfileoffsets[cdnindex], realindexesfilesizes[cdnindex], mainwowfolder, True)
            print 'File Parsed Successfully!'
            return parsefile
    else:
        if returnparamsarray == False:
            parsefile = readCASCData(firstbytearray[idxindex], beuint32array[idxindex], sizeofdataarray[idxindex], mainwowfolder)
            print 'File Parsed Successfully!'
            return parsefile
        else:
            paramsarray = []
            paramsarray.append(firstbytearray[idxindex])
            paramsarray.append(beuint32array[idxindex])
            paramsarray.append(sizeofdataarray[idxindex])
            return paramsarray

def getEncodingAndRootFromServer(region, customcdnurl=None, customconfigurl=None):
    print 'Getting Root and Encoding Hashes from server!'
    fixedregion = region.lower()
    if (fixedregion != 'eu') and (fixedregion != 'tw') and (fixedregion != 'us') and (fixedregion != 'kr') and (fixedregion != 'cn'):
        print 'Wrong region. Available regions: eu, tw, us, kr, cn'
    else:
        if customcdnurl != None:
            cdnfile = urllib2.urlopen(customcdnurl)
        else:
            cdnfile = urllib2.urlopen('http://us.patch.battle.net:1119/wow/cdns')
        cdnfilecontent = cdnfile.read()

        if customconfigurl != None:
            versionfile = urllib2.urlopen(customconfigurl)
        else:
            versionfile = urllib2.urlopen('http://us.patch.battle.net:1119/wow/versions')
        versionfilecontent = versionfile.read()

        goodcdnpart = ''
        splitcdnfile = cdnfilecontent.split('\n')
        for stringpart in splitcdnfile:
            if fixedregion + '|' in stringpart:
                goodcdnpart = stringpart
                break
        getcdnurlarray = goodcdnpart.split('|')

        getsecondurlpart = getcdnurlarray[1]
        getfirsturlpart = getcdnurlarray[2].split(' ')[0]

        goodversionpart = ''
        splitconfigfile = versionfilecontent.split('\n')
        for stringpart in splitconfigfile:
            if fixedregion + '|' in stringpart:
                goodversionpart = stringpart
                break
        print goodversionpart

        fullhash = goodversionpart.split('|')[1]
        shorthashone = fullhash[:2]
        shorthashtwo = fullhash[2:4]

        buildfullurl = 'http://' + getfirsturlpart + '/' + getsecondurlpart + '/config/' + shorthashone + '/' + shorthashtwo + '/' + fullhash
        configfile = urllib2.urlopen(buildfullurl)
        readconfigfile = configfile.read()
        print readconfigfile

        splitconfig = readconfigfile.split('\n')

        for index, line in enumerate(splitconfig):
            if 'root ' in line:
                rootline = splitconfig[index]
            elif 'encoding ' in line:
                encodingline = splitconfig[index]

        roothash = rootline.split(' ')[2][1:]
        encodinghash = encodingline.split(' ')[3][1:]

        print roothash
        print encodinghash
        return roothash, encodinghash


def getEncodingAndRootFromLocalFiles(mainwowfolder):
    configfolder = mainwowfolder + 'Data\\config'
    filelist = os.listdir(configfolder)
    latestdate = 0
    latestconfigpath = None
    encodinghash = None
    roothash = None
    for filee in filelist:
        modificationtime = os.path.getctime(configfolder + '\\' + filee)
        if latestdate < modificationtime:
            nextfolder = os.listdir(configfolder + '\\' + filee + '\\')
            lastfolder = os.listdir(configfolder + '\\' + filee + '\\' + nextfolder[0] + '\\')
            thisfilefullpath = configfolder + '\\' + filee + '\\' + nextfolder[0] + '\\' + lastfolder[0]
            openfile = open(thisfilefullpath, 'r')
            readfile = openfile.read()
            openfile.close()
            if 'Build Configuration' in readfile:
                latestdate = modificationtime
                latestconfigpath = thisfilefullpath

    openlatestbuildconfig = open(latestconfigpath, 'r')
    readlatestconfig = openlatestbuildconfig.read()
    openlatestbuildconfig.close()
    splitconfig = readlatestconfig.split('\n')

    for index, line in enumerate(splitconfig):
        if 'root ' in line:
            rootline = splitconfig[index]
        elif 'encoding ' in line:
            encodingline = splitconfig[index]

    roothash = rootline.split(' ')[2]
    encodinghash = encodingline.split(' ')[3]

    print 'Root Hash: %s' %(roothash)
    print 'Encoding Hash: %s' %(encodinghash)
    return roothash, encodinghash


def parseCDNConfig(mainwowfolder, fixedregion='us', customcdnurl=None):
    global realindexmd5hashes
    global realindexesfilesizes
    global realindexesfileoffsets
    global realindexesdatafilesnumbers
    global areindiciesparsed

    realindexmd5hashes = []
    realindexesfilesizes = []
    realindexesfileoffsets = []
    realindexesdatafilesnumbers = []


    if (fixedregion != 'eu') and (fixedregion != 'tw') and (fixedregion != 'us') and (fixedregion != 'kr') and (fixedregion != 'cn'):
        print 'Wrong region. Available regions: eu, tw, us, kr, cn'
    else:
        if customcdnurl != None:
            cdnfile = urllib2.urlopen(customcdnurl)
        else:
            cdnfile = urllib2.urlopen('http://us.patch.battle.net:1119/wow/cdns')
        cdnfilecontent = cdnfile.read()

    goodcdnpart = ''
    splitcdnfile = cdnfilecontent.split('\n')
    for stringpart in splitcdnfile:
        if fixedregion + '|' in stringpart:
            goodcdnpart = stringpart
            break
    getcdnurlarray = goodcdnpart.split('|')

    getsecondurlpart = getcdnurlarray[1]
    getfirsturlpart = getcdnurlarray[2].split(' ')[0]


    configfolder = mainwowfolder + 'Data\\config'
    filelist = os.listdir(configfolder)
    latestdate = 0
    lastestcdnconfig = None
    for filee in filelist:
        modificationtime = os.path.getctime(configfolder + '\\' + filee)
        if latestdate < modificationtime:
            nextfolder = os.listdir(configfolder + '\\' + filee + '\\')
            lastfolder = os.listdir(configfolder + '\\' + filee + '\\' + nextfolder[0] + '\\')
            thisfilefullpath = configfolder + '\\' + filee + '\\' + nextfolder[0] + '\\' + lastfolder[0]
            openfile = open(thisfilefullpath, 'r')
            readfile = openfile.read()
            openfile.close()
            if 'CDN Configuration' in readfile:
                latestdate = modificationtime
                lastestcdnconfig = thisfilefullpath

    openlatestbuildconfig = open(lastestcdnconfig, 'r')
    readlatestconfig = openlatestbuildconfig.read()
    openlatestbuildconfig.close()
    splitconfig = readlatestconfig.split('\n')

    for index, line in enumerate(splitconfig):
        if ('archives ' in line) and ('-archives ' not in line):
            archivecdns = splitconfig[index]

    archiveindexesarray = archivecdns.split(' ')[2:]
    #print archiveindexesarray
    print 'Parsing %i indicies files, it may take a while...' %(len(archiveindexesarray))

    localindiciesfolder = mainwowfolder + 'Data\\indices'
    localindiciesarray = os.listdir(localindiciesfolder)

    cdnfilesize = 268435456
    datafilesize = 4 * cdnfilesize


    cachechecker = False
    for indexio, archive in enumerate(archiveindexesarray):
        fullindexname = archive + '.index'
        if fullindexname in localindiciesarray:
            openindex = open(localindiciesfolder + '\\' + fullindexname, 'rb')
        elif fullindexname not in localindiciesarray:
            print '%s was not found in local indicies folder. Trying to download it from CDN.' %(fullindexname)
            cdnurlpath = 'http://' + getfirsturlpart + '/' + getsecondurlpart + '/data/' + fullindexname[:2] + '/' + fullindexname[2:4] + '/' + fullindexname
            downloadfile = urllib.URLopener()
            if not os.path.exists('indexcache'):
                os.makedirs('indexcache')
            downloadfile.retrieve(cdnurlpath, 'indexcache\\' + fullindexname)
            cachechecker = True
            openindex = open('indexcache\\' + fullindexname, 'rb')
        readindex = openindex.read()
        openindex.close()

        globaloffset = 0
        while globaloffset < len(readindex):
            localoffset = 0
            while localoffset < 4096:
                readmd5hash = readindex[globaloffset + localoffset:globaloffset + localoffset + 0x10]
                fakestring = ''
                for byteee in readmd5hash:
                    uncodebyte = struct.unpack('B', byteee)[0]
                    cuthex = hex(uncodebyte)[2:]
                    if len(cuthex) == 1:
                        cuthex = '0' + cuthex
                    fakestring += cuthex
                if fakestring == ('0' * 32):
                    break
                elif (localoffset == 0) and (fakestring in realindexmd5hashes):
                    break
                realindexmd5hashes.append(fakestring)

                readsizeoffile = readindex[globaloffset + localoffset + 0x10:globaloffset + localoffset + 0x14]
                sizeoffile = struct.unpack('>I', readsizeoffile)[0]
                realindexesfilesizes.append(sizeoffile)

                readfileoffset = readindex[globaloffset + localoffset + 0x14:globaloffset + localoffset + 0x18]
                fileoffset = struct.unpack('>I', readfileoffset)[0]
                realindexesfileoffsets.append(fileoffset)

                realindexesdatafilesnumbers.append(archive)

                localoffset += 0x18
            globaloffset += 4096
    areindiciesparsed = True


def getMapNames(wowfolderpath):
    global blizzhashfilekeyrootarray
    stringarray = []
    if len(blizzhashfilekeyrootarray) == 0:
        print 'Root blizzhash array is empty, remaking it'
        root, encoding = getEncodingAndRootFromLocalFiles(wowfolderpath)
        initializeNecessaryArrays(encoding, root, wowfolderpath, '0x202')
    mapdb2 = parseWoWFile('DBFilesClient\Map.db2', wowfolderpath)
    if mapdb2 == None:
        print 'Something went wrong... try again'
    else:
        db2headersize = 0x54
        readdb2 = mapdb2
        getStingSizeAddress = readdb2[0x10:0x14]
        getStingSize = struct.unpack('I', getStingSizeAddress)[0]
        if getStingSize > 0:
            getFieldCountAddress = readdb2[0x8:0xC]
            getFieldCount = struct.unpack('I', getFieldCountAddress)[0]

            getRecordCountAddress = readdb2[0x4:0x8]
            getRecordCount = struct.unpack('I', getRecordCountAddress)[0]

            getRecordSizeAddress = readdb2[0xC:0x10]
            getRecordSize = struct.unpack('I', getRecordSizeAddress)[0]

            stringStartOffset = db2headersize + (getFieldCount * 4) + (getRecordCount * getRecordSize)
            offsetcounter = 0
            stringkeeper = ''
            while getStingSize > offsetcounter:
                checkCurrentByte = readdb2[stringStartOffset + offsetcounter:stringStartOffset + offsetcounter + 1]
                if checkCurrentByte == '\x00':
                    if len(stringkeeper) > 0:
                        stringarray.append(stringkeeper)
                        stringkeeper = ''
                    offsetcounter += 1
                    continue
                else:
                    stringkeeper += checkCurrentByte
                    offsetcounter += 1
        print len(stringarray)
        print stringarray

        existingstringsarray = []
        if len(stringarray) > 0:
            for thisstring in stringarray:
                trystringname = 'World\Maps\%s\%s.wdl' %(thisstring, thisstring)
                tryanotherstringname = 'World\Maps\%s\%s.wdt' %(thisstring, thisstring)
                tryonemorename = 'World\Maps\%s\%s.tex' % (thisstring, thisstring)
                getblizzhash = Blizzhash(trystringname)
                getsecondblizzhash = Blizzhash(tryanotherstringname)
                getthirdblizzhash = Blizzhash(tryonemorename)
                for md5 in blizzhashfilekeyrootarray:
                    if (md5 == getblizzhash) or (md5 == getsecondblizzhash) or (md5 == getthirdblizzhash):
                        existingstringsarray.append(thisstring)
                        continue
        removeduplicates = set(existingstringsarray)
        fixedstringarray = sorted(list(removeduplicates), key=str.lower)
        print len(fixedstringarray)
        print fixedstringarray

        print 'Generating dictionary for string to check...'
        generatedblizzhashesdictionary = {}
        for directory in fixedstringarray:
            print 'Generating strings for %s directory' %(directory)
            fakearray = []
            fakearray.append('World\Maps\%s\%s.wdl' %(directory, directory))
            fakearray.append('World\Maps\%s\%s.wdt' % (directory, directory))
            fakearray.append('World\Maps\%s\%s.tex' % (directory, directory))
            fakearray.append('World\Maps\%s\%s_lgt.wdt' % (directory, directory))
            fakearray.append('World\Maps\%s\%s_occ.wdt' % (directory, directory))
            for number in range(0, 64):
                for secondarynumber in range(0, 64):
                    fakearray.append('World\Maps\%s\%s_%s_%s.adt' % (directory, directory, str(number), str(secondarynumber)))
                    fakearray.append('World\Maps\%s\%s_%s_%s_lod.adt' % (directory, directory, str(number), str(secondarynumber)))
                    fakearray.append('World\Maps\%s\%s_%s_%s_obj0.adt' % (directory, directory, str(number), str(secondarynumber)))
                    fakearray.append('World\Maps\%s\%s_%s_%s_obj1.adt' % (directory, directory, str(number), str(secondarynumber)))
                    fakearray.append('World\Maps\%s\%s_%s_%s_tex0.adt' % (directory, directory, str(number), str(secondarynumber)))

            for fakestring in fakearray:
                generatedblizzhashesdictionary[Blizzhash(fakestring)] = fakestring

        blizzhasharrayset = set(blizzhashfilekeyrootarray)
        generatedblizzhashesdictionaryset = set(generatedblizzhashesdictionary)
        print len(blizzhasharrayset)
        print len(generatedblizzhashesdictionaryset)
        finalset = blizzhasharrayset & generatedblizzhashesdictionaryset
        print len(finalset)

        truestinglist = []
        maplistfile = open('maplistfile.txt', 'w')
        for goodblizzhash in list(finalset):
            truestinglist.append(generatedblizzhashesdictionary[goodblizzhash])
        for filename in sorted(truestinglist, key=str.lower):
            maplistfile.write(filename + '\n')
        maplistfile.close()
        print 'Done!'


def getM2AndWMOUsingMaplistfile(mainwowfolder, remakemaplistfile=False, workernumber=1):
    global blizzhashfilekeyrootarray
    mainstringarray = []

    def helperFunction(fileentry):
        print 'Getting M2 and WMO string from %s' % (fileentry)
        readobj0 = parseWoWFile(fileentry, mainwowfolder)
        firstmddxstring = 0
        MDDXstart = 0
        firstmwmostring = 0
        MWMOstart = 0
        localm2offset = 0
        localwmooffset = 0
        tempstring = ''
        previousbyte = ''
        continuetowmo = False
        continuetonextfile = False
        foundMMDX = re.finditer('XDMM', readobj0)
        if foundMMDX:
            for m in foundMMDX:
                kl = m.span()
                MDDXstart = kl[0]
                firstmddxstring = MDDXstart + 0x8
                break
        if MDDXstart != 0:
            modelnamestring = readobj0[firstmddxstring + localm2offset:firstmddxstring + localm2offset + 1]
            while continuetowmo == False:
                if modelnamestring != '\x00':
                    tempstring += modelnamestring
                else:
                    if previousbyte != '\x00':
                        if len(tempstring) != 0 and '.m2' in tempstring.lower():
                            mainstringarray.append(tempstring)
                        tempstring = ''
                    else:
                        continuetowmo = True
                localm2offset += 1
                previousbyte = modelnamestring
                modelnamestring = readobj0[firstmddxstring + localm2offset:firstmddxstring + localm2offset + 1]
        foundMWMO = re.finditer('OMWM', readobj0)
        if foundMWMO:
            for m in foundMWMO:
                kl = m.span()
                MWMOstart = kl[0]
                firstmwmostring = MWMOstart + 0x8
                break
        if MWMOstart != 0:
            modelnamestring = readobj0[firstmwmostring + localwmooffset:firstmwmostring + localwmooffset + 1]
            while continuetonextfile == False:
                if modelnamestring != '\x00':
                    tempstring += modelnamestring
                else:
                    if previousbyte != '\x00':
                        if len(tempstring) != 0 and '.wmo' in tempstring.lower():
                            mainstringarray.append(tempstring)
                            splitwmofile = tempstring.split('.')[0]
                            for x in range(0, 1000):
                                fixx = str(x)
                                while len(fixx) < 3:
                                    fixx = '0' + fixx
                                stringtocheck = splitwmofile + '_' + fixx + '.wmo'
                                blizzhash = Blizzhash(stringtocheck)
                                if blizzhash in blizzhashfilekeyrootarray:
                                    mainstringarray.append(stringtocheck)
                                else:
                                    break
                        tempstring = ''
                    else:
                        continuetonextfile = True
                localwmooffset += 1
                previousbyte = modelnamestring
                modelnamestring = readobj0[firstmwmostring + localwmooffset:firstmwmostring + localwmooffset + 1]


    if len(blizzhashfilekeyrootarray) == 0:
        root, encoding = getEncodingAndRootFromLocalFiles(mainwowfolder)
        initializeNecessaryArrays(encoding, root, mainwowfolder, '0x202')


    mainstringarray = []
    currentdir = os.listdir(os.curdir)
    if remakemaplistfile == True or ('maplistfile.txt' not in currentdir):
        print 'Maplistfile.txt not found or option to remake has been choosen. It may take few minutes...'
        getMapNames(mainwowfolder)
    with open('maplistfile.txt', 'r') as openmaplist:
        openmaplistfile = openmaplist.read()
    splitentries = openmaplistfile.split('\n')
    obj0array = []

    for filex in splitentries:
        if '_obj0.adt' in filex:
            obj0array.append(filex)

    pool = ThreadPool(workernumber)
    pool.map(helperFunction, obj0array)
    pool.close()
    pool.join()

    openm2andwmolistfile = open('m2andwmolistfile.txt', 'w')
    print 'Lenght of array is %i, removing duplicates' % (len(mainstringarray))
    mainstringarrayset = set(mainstringarray)
    sortedarray = sorted(list(mainstringarrayset), key=str.lower)
    for entry in sortedarray:
        openm2andwmolistfile.write(entry + '\n')
    print 'm2andwmolistfile.txt generated successfully!'

def parseAllNecessaryMapFile(mainwowfolder, outputfolder, workernumber=4):
    global blizzhashfilekeyrootarray

    def innerHelper(stringinput):
        print 'Parsing file %s' % (stringinput)
        splitfile = stringinput.split('\\')
        filename = splitfile[-1]
        del splitfile[-1]
        filepath = '\\'.join(splitfile)
        fullfilepath = outputfolder + filepath + '\\'
        parsefile = parseWoWFile(stringinput, mainwowfolder)
        if parsefile != None:
            opendestinationfile = open(fullfilepath + filename, 'wb')
            opendestinationfile.write(parsefile)
            opendestinationfile.close()


    pool = ThreadPool(workernumber)
    thisdirectory = os.listdir(os.curdir)
    if 'maplistfile.txt' not in thisdirectory:
        print 'maplistfile.txt not found in current directory, use getMapNames function to generate it'
        return None
    elif 'm2andwmolistfile.txt' not in thisdirectory:
        print 'm2andwmolistfile.txt not found in current directory, use getM2AndWMOUsingMaplistfile function to generate it (very long, around 3-4 hours) or provide your own list'
        return None
    else:
        readmaplistfilee = open('maplistfile.txt', 'r')
        readmaplistfile = readmaplistfilee.read()
        readmaplistfilee.close()
        splitmaplistfile = readmaplistfile.split('\n')

        readm2andwmolistfilee = open('m2andwmolistfile.txt', 'r')
        readm2andwmolistfile = readm2andwmolistfilee.read()
        readm2andwmolistfilee.close()
        splitm2andwmolistfile = readm2andwmolistfile.split('\n')

        adtm2andwmoarray = []
        for filee in splitmaplistfile:
            if filee != '':
                adtm2andwmoarray.append(filee)
        for filee in splitm2andwmolistfile:
            if filee != '':
                adtm2andwmoarray.append(filee)
        if len(blizzhashfilekeyrootarray) == 0:
            root, encoding = getEncodingAndRootFromLocalFiles(mainwowfolder)
            initializeNecessaryArrays(encoding, root, mainwowfolder, '0x202')

        for fikus in adtm2andwmoarray:
            splitfile = fikus.split('\\')
            del splitfile[-1]
            filepath = '\\'.join(splitfile)
            fullfilepath = outputfolder + filepath + '\\'
            if not os.path.exists(fullfilepath):
                os.makedirs(fullfilepath)

        pool.map(innerHelper, adtm2andwmoarray)
        pool.close()
        pool.join()





def compareMapsFolders():
    with open('maplistfile.txt', 'r') as maplist:
        readfile = maplist.read()
    splitreadfile = readfile.split('\n')
    goodfilearray = []
    for f in splitreadfile:
        if f != '':
            forss = f.split('\\')
            goodfilearray.append(forss[3].lower())

    directoryfilearray = []
    emapfolder = os.listdir('E:\MapsLegion\World\Maps')
    for foldertocheck in emapfolder:
        eachfolderlist = os.listdir('E:\MapsLegion\World\Maps\\' + foldertocheck)
        for filee in eachfolderlist:
            directoryfilearray.append(filee.lower())

    for fe in goodfilearray:
        if fe not in directoryfilearray:
            print fe



def getDB2FileListFromWowClient(mainwowfolder, currentversion='7.3.5.26124', currentversionoffset=0x129D588, currentdb2offset=0x1815EB0):
    #To get currentdb2offset look for DBFilesClient in IDA strings. Fallow the string to subroutine and open it in pseudocode view. Fallow parrent function to find this offset table.
    global blizzhashfilekeyrootarray

    if type(currentversionoffset) != int and type(currentversionoffset) == str:
        currentversionoffset = int(currentversionoffset, 16)
    if type(currentdb2offset) != int and type(currentdb2offset) == str:
        currentdb2offset = int(currentdb2offset, 16)

    if type(currentversion) != str:
        print 'currentversion type is wrong, provide string'
        return None

    db2stringsarray = []
    wowversionoffset = currentversionoffset
    db2wowclientarrayoffset = currentdb2offset
    currentWowversion = currentversion

    #Get pid for active WoW Client
    wowpid = get_client_pid('Wow-64.exe')
    #Set privilages for parser
    currentProcessHandle = windll.kernel32.GetCurrentProcess()
    flags = win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
    currentProcessToken = win32security.OpenProcessToken(currentProcessHandle, flags)
    id1 = win32security.LookupPrivilegeValue(None, "seDebugPrivilege")
    newPrivileges = [(id1, win32security.SE_PRIVILEGE_ENABLED)]
    win32security.AdjustTokenPrivileges(currentProcessToken, 0, newPrivileges)
    if wowpid != 0:
        #Get handle from pid, if it doesn't work try setting privilages to PROCESS_ALL_ACCESS
        wowprocesshandle = setProcessHandle(wowpid)
        if wowprocesshandle == 0:
            wowprocesshandle = setProcessHandle(wowpid, PROCESS_ALL_ACCESS)
        if wowprocesshandle == 0:
            print 'Couldnt retrieve handle to active Wow process'
        else:
            #Get module base address from handle
            baseaddress = getBaseAddress(wowprocesshandle)
            if baseaddress:
                versionbuffer = c_char_p('')
                bytesRead = c_ulonglong(0)
                #Read version from client memory, check if its correct
                if ReadProcessMemory(wowprocesshandle, baseaddress + wowversionoffset, versionbuffer, 32, byref(bytesRead)):
                    if versionbuffer.value != currentWowversion:
                        print 'Wrong WoW version, current program can get DB2 string list only for version %s. Update offsets!' %(currentWowversion)
                        print 'Current Version Buffer value is: %s (should be %s)' %(versionbuffer.value, currentWowversion)
                    else:
                        print 'Version check passed!'
                        addressbuffer = c_longlong()
                        db2stringbuffer = c_char_p('')
                        localoffset = 0
                        fakecounter = 0
                        while ReadProcessMemory(wowprocesshandle, baseaddress + db2wowclientarrayoffset + localoffset, byref(addressbuffer), 8,byref(bytesRead)):
                            ReadProcessMemory(wowprocesshandle, addressbuffer.value + 0x8, byref(addressbuffer), 8,byref(bytesRead))
                            ReadProcessMemory(wowprocesshandle, addressbuffer.value, byref(addressbuffer), 8,byref(bytesRead))
                            ReadProcessMemory(wowprocesshandle, addressbuffer.value, db2stringbuffer, 100, byref(bytesRead))
                            db2stringsarray.append(db2stringbuffer.value)
                            localoffset += 0x8
                            fakecounter += 1
                            if db2stringbuffer.value == 'ZoneStory':
                                pass
                        print 'Generated DB2StringArray with %i elements' %(len(db2stringsarray))
                        print 'Checking if all entries exist in root!'
                        if len(blizzhashfilekeyrootarray) == 0:
                            print 'Blizzhash root keys array is empty, remaking it using local files.'
                            root, encoding = getEncodingAndRootFromLocalFiles(mainwowfolder)
                            initializeNecessaryArrays(encoding, root, mainwowfolder, '0x202')
                        db2blizzhashdictionary = {}
                        for db2 in db2stringsarray:
                            fullpath = 'DBFilesClient\%s.db2' %(db2)
                            db2blizzhashdictionary[Blizzhash(fullpath)] = fullpath

                        rootblizzhashset = set(blizzhashfilekeyrootarray)
                        db2blizzhashset = set(db2blizzhashdictionary)
                        compareblizzhashes = rootblizzhashset & db2blizzhashset
                        print 'Found %i db2 string in root!' %(len(compareblizzhashes))

                        existingdb2paths = []
                        for blizzhash in list(compareblizzhashes):
                            existingdb2paths.append(db2blizzhashdictionary[blizzhash])

                        opendb2listfile = open('db2listfile.txt', 'w')
                        for entry in sorted(existingdb2paths, key=str.lower):
                            opendb2listfile.write(entry + '\n')
                        opendb2listfile.close()
                        print 'DB2 Listfile Created!'
                        return sorted(existingdb2paths, key=str.lower)



def getAllStringFromDB2Files(db2listfilepath, mainwowfolder):
    with open(db2listfilepath, 'r') as db2listopen:
        opendb2listfile = db2listopen.read()
    splitentries = opendb2listfile.split('\n')
    for index, element in enumerate(splitentries):
        if element != '':
            continue
        else:
            del splitentries[index]
    alldb2filesdictionary = {}
    for db2string in splitentries:
        print db2string
        stringarray = []
        readdb2 = parseWoWFile(db2string, mainwowfolder)
        db2headersize = 0x54
        getStingSizeAddress = readdb2[0x10:0x14]
        getStingSize = struct.unpack('I', getStingSizeAddress)[0]
        if getStingSize > 0:
            getFieldCountAddress = readdb2[0x8:0xC]
            getFieldCount = struct.unpack('I', getFieldCountAddress)[0]

            getRecordCountAddress = readdb2[0x4:0x8]
            getRecordCount = struct.unpack('I', getRecordCountAddress)[0]

            getRecordSizeAddress = readdb2[0xC:0x10]
            getRecordSize = struct.unpack('I', getRecordSizeAddress)[0]

            stringStartOffset = db2headersize + (getFieldCount * 4) + (getRecordCount * getRecordSize)
            offsetcounter = 0
            stringkeeper = ''
            while getStingSize > offsetcounter:
                checkCurrentByte = readdb2[stringStartOffset + offsetcounter:stringStartOffset + offsetcounter + 1]
                if checkCurrentByte == '\x00':
                    if len(stringkeeper) > 0:
                        stringarray.append(stringkeeper)
                        stringkeeper = ''
                    offsetcounter += 1
                    continue
                else:
                    stringkeeper += checkCurrentByte
                    offsetcounter += 1
        print '%s file array has %i elements' %(db2string, len(stringarray))
        alldb2filesdictionary[db2string] = stringarray

    print 'Initialization completed.'
    openstringfile = open('db2stringlist', 'w')
    for db2stringvalue, thisstringarray in sorted(alldb2filesdictionary.items()):
        openstringfile.write(db2stringvalue + '\n' + '\n')
        for value in thisstringarray:
            openstringfile.write(value + '\n')
    openstringfile.close()


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()



#Functions end here. Trash used for testing below.


#parseAllNecessaryMapFile('C:\\World of Warcraft\\', 'E:\\Supertest\\', 13)
#getM2AndWMOUsingMaplistfile('C:\\World of Warcraft\\')
#majquier = False
#if majquier == True:
    #compareMapsFolders()
    #print Blizzhash('World\Maps\Kalimdor\Kalimdor_29_39.adt')
    #wowfolderpath = 'C:\\World of Warcraft\\'
    #wowfolderpath = raw_input('Wow main folder path: ')
    #if wowfolderpath == '':
        #wowfolderpath = 'C:\\World of Warcraft\\'
    #realindexmd5hashes = []
    #parseCDNConfig(wowfolderpath)
    #keytocheck = 'ba607fb006865f5312e23269b45ce919'
    #for index, key in enumerate(realindexmd5hashes):
        #if key == keytocheck:
        #if key in 'ba607fb006865f5312e23269b45ce919':
            #print 'got it'
            #print index
            #print key
    #parseAllNecessaryMapFile(wowfolderpath, 'E:\\Supertest\\', 13)
    #getDB2FileListFromWowClient(wowfolderpath)
    #getAllStringFromDB2Files('db2listfile.txt', wowfolderpath)


    #getMapNames(wowfolderpath)

    #print realindexmd5hashes[257323]
    #print realindexesfileoffsets[257323]
    #print realindexesfilesizes[257323]
    #print realindexesdatafilesnumbers[257323]

    #encodeBLTEFile('2662abfc954b9c7c709c49f0c715cd4c',59734802,25276,wowfolderpath,True)
    #parseRootFile('tempfile', 0x202)
    #root, encoding = getEncodingAndRootFromServer('EU')
    #root, encoding = getEncodingAndRootFromLocalFiles(wowfolderpath)
    #initializeNecessaryArrays(encoding, root, wowfolderpath)
    #locale = raw_input('Specific Locale: (press enter to parse all)')
    #if locale == '':
        #locale = None
    #customencodinghash = raw_input('Custom Encoding Hash: ')
    #customroothash = raw_input('Custom Root Hash: ')
    #if customencodinghash == '' and customroothash == '':
        #initializeNecessaryArrays(encoding, root, wowfolderpath, locale)
    #elif customencodinghash == '':
        #initializeNecessaryArrays(encoding, customroothash, wowfolderpath, locale)
    #elif customroothash == '':
        #initializeNecessaryArrays(customencodinghash, root, wowfolderpath, locale)
    #else:
        #initializeNecessaryArrays(customencodinghash, customroothash, wowfolderpath, locale)


    #while True:
        #asker = raw_input('File Name or Quit: ')
        #if asker == 'Quit':
            #break
        #else:
            #parseWoWFile(asker, wowfolderpath)


#jenkins96('Earth, wind and fire; heed my call!')
#testhash = Blizzhash('source\\game\\core\\Keyring.cpp')
#print testhash
#encodingfile = getEncodingFile('18224fb3b78d6324f1846993718316af', 'C:\\World of Warcraft\\')
#parseEncodingFile(encodingfile, True)
#rootfile = getRootFile('2532a4ddca7cff85c2cd4d418853014b', 'C:\\World of Warcraft\\')
#getRootFile('e1e6b5f0ad34f2b41e31a54d17e12af8', 'C:\\World of Warcraft\\')
#parseRootFile(rootfile)


#print testfilehash | secondreturn
#print realhash
#sliceonce = realhash[2:]
#fliponce = sliceonce[::-1]
#slicetwice = fliponce[1:]
#finalhashformat = slicetwice[::-1]

#parseAllIDX(wowfolderpath)

#majonez = False
#while majonez == True:
    #for indexx, array in enumerate(firststringblock):
        #for key in array:
            #if 'DFA390137F107EE0' in key:
                #for indexxx, keyy in enumerate(secondarraystringblockoneindexes):
                    #if keyy == indexx:
                        #print 'Found entry including encoded data'
                        #print secondarraystringblockoneindexes[indexxx]
                        #print secondarraymd5idxheaders[indexxx]
                        #print array


#encodedindexinstring = firststringblock[24]
#encodedidxhash = '9336ab3bb310fc8081fe063a4b4b2483'
#print encodedindexinstring

#keytocheck = 'ba607fb006865f5312e23269b45ce919'
#print len(hashkeyarray)





#print firstbytearray[1217753]
#print beuint32array[1217753]
#print sizeofdataarray[1217753]


#readCASCData(firstbytearray[1148725], beuint32array[1148725], sizeofdataarray[1148725], 'C:\\World of Warcraft\\')
#print finalhashformat
#print len(finalhashformat)
#for index, size in enumerate(sizeofdataarray):
    #if size >= 10000000:
        #print 'found, index %s' %(str(index))
        #print size
        #readCASCData(firstbytearray[index], beuint32array[index], sizeofdataarray[index], 'C:\\World of Warcraft\\')
        #break
#testmd5 = readCASCData(firstbytearray[235988], beuint32array[235988], sizeofdataarray[235988], 'C:\\World of Warcraft\\')

#readCASCData(0x7, 0x5BF6CEDF, 0x7ff7, 'C:\\World of Warcraft\\')

#readCASCData(0x2, 0xF0D8515C, 0xe16, 'C:\\World of Warcraft\\')
#majo = False
#if majo == True:
    #testfileopen = open('tempfile', 'Ub').read()
    #keyfile_name = '05B0C94E0F811358'
    #encodingkey = 'D83BBCB46CC438B17A48E76C4F5654A3'
    #encodingkeyreversed = '82608B28AD0F699E9AD92D14438BBE01'
    #IV = '13EB9BF3'
    #decodesalsa = salsa20.Salsa20_xor(testmd5, IV, encodingkey)
    #decodesalsa = salsa20.Salsa20_xor(testfileopen, '01CD09D4', 'E5C6F2BCAE34A240E54ACECBCFDFF79C')
    #decodesalsa = salsa20.Salsa20_xor(testfileopen, '01CD09D4', '01BE8B43142DD99A9E690FAD288B6082')
    #newtestfile = open('tempfile1', 'w')
    #newtestfile.write(decodesalsa)
    #newtestfile.close()
    #majo = False


#md5hash = hashlib.sha256(decodesalsa)
#print md5hash.hexdigest()
#print len(md5hash.hexdigest())

#md5hash = hashlib.sha256('PASSWORD.DLL')
#print md5hash.hexdigest()
#ff = False
#if ff == True:
    #openweirdfile = open('7974ea5c27914feca1cf5558422a205df9fc84dc6f4fe133658c063e948b1891.wows', 'rb')
    #readit = openweirdfile.read()
    #openweirdfile.close()
    #decompress = zlib.decompress(readit[0x10:])
    #opennew = open('weirdfile1', 'w')
    #opennew.write(decompress)
    #opennew.close()