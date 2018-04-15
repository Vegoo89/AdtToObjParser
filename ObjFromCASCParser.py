import AdtToObjParser
import CASCParser
import os
import time

global temporarym2dictionary
temporarym2dictionary = {}

def parseADTUsingCASC(adtfilenamefromlistfile, wowfolderpath, outputfolder=None):
    global temporarym2dictionary
    fixadtfilename = adtfilenamefromlistfile.split('\\')[-1]
    obj0filename = adtfilenamefromlistfile.split('.')
    obj0filename[-2] += '_obj0'
    obj0listfilename = '.'.join(obj0filename)

    mainadtfile = CASCParser.parseWoWFile(adtfilenamefromlistfile, wowfolderpath)
    obj0file = CASCParser.parseWoWFile(obj0listfilename, wowfolderpath)

    if mainadtfile != None and obj0file != None:
        AdtToObjParser.parseTerrain(fixadtfilename, outputfolder, True, mainadtfile)
        AdtToObjParser.parseWater(fixadtfilename, outputfolder, True, mainadtfile)
        m2array = AdtToObjParser.parseAllM2(fixadtfilename, None, None, True, obj0file)
        if len(m2array) != 0:
            for item in m2array:
                print item
                if item[0] not in temporarym2dictionary:
                    openm2file = CASCParser.parseWoWFile(item[0], wowfolderpath)
                    temporarym2dictionary[item[0]] = openm2file
                AdtToObjParser.parseM2(fixadtfilename, None, item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], outputfolder, True, temporarym2dictionary[item[0]])

        wmoarray = AdtToObjParser.parseAllWMO(fixadtfilename, None, None, False, True, obj0file)
        if len(wmoarray) != 0:
            for item in wmoarray:
                for x in range(0, 1000):
                    fixedx = str(x)
                    while len(fixedx) < 3:
                        fixedx = '0' + fixedx
                    wmolistfilestring = item[0].split('.')
                    wmolistfilestring[0] = wmolistfilestring[0] + '_' + fixedx
                    fixedwmostring = '.'.join(wmolistfilestring)
                    print fixedwmostring
                    openwmo = CASCParser.parseWoWFile(fixedwmostring, wowfolderpath)
                    if openwmo == None:
                        'This WMO doest exist in local files, moving to next WMO'
                        break
                    else:
                        AdtToObjParser.parseWMO(fixadtfilename, None, None, item[1], item[2], item[3], item[4], item[5], item[6], outputfolder, True, openwmo)



def parseAllAdtFromMapListfile(mainwowfolder, outputfolder=None, recreatemaplistfile=False, overwritefiles=False, startindex=0, stopindex=999999):
    getfilesfromcurrentdirectory = os.listdir(os.curdir)
    if outputfolder != None:
        getlistofilesfromoutputfolder = os.listdir(outputfolder)
    else:
        getlistofilesfromoutputfolder = getfilesfromcurrentdirectory
    for indexx, x in enumerate(getlistofilesfromoutputfolder):
        getlistofilesfromoutputfolder[indexx] = x.lower()
    #print getfilesfromcurrentdirectory
    if (recreatemaplistfile == True) or ('maplistfile.txt' not in getfilesfromcurrentdirectory):
        print 'Maplistfile.txt was not found in current directory or option to recreate it was choosen. It may take few minutes... '
        CASCParser.getMapNames(mainwowfolder)
    openmaplistfile = open('maplistfile.txt', 'r').read()
    splitentries = openmaplistfile.split('\n')
    for index, fileentry in enumerate(splitentries):
        if (len(fileentry) > 0) and (startindex <= index) and (stopindex > index):
            realfilename = fileentry.split('\\')[-1]
            objname = realfilename.split('.')[0] + '.obj'
            if (objname.lower() in getlistofilesfromoutputfolder) and (overwritefiles == False):
                print 'File already exists in output folder and overwrite files function is off. Continuing to next file.'
                continue
            if '.adt' in fileentry and '_obj0' not in fileentry and '_obj1' not in fileentry and '_tex0' not in fileentry and '_lod' not in fileentry:
                print 'Parsing file %s' %(fileentry)
                parseADTUsingCASC(fileentry, mainwowfolder, outputfolder)








#parseADTUsingCASC('World\\Maps\\7_DungeonExteriorNeltharionsLair\\7_DungeonExteriorNeltharionsLair_27_27.adt', 'C:\\World of Warcraft\\', 'E:\\Testfoldercascparser\\')
#parseAllAdtFromMapListfile('C:\\World of Warcraft\\', 'E:\\Testfoldercascparser\\', False, False, 0, 55)