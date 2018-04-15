from AdtToObjParser import *
from CASCParser import *
from ObjFromCASCParser import *


print 'Program Initialized'
Quit = False
#allfunctionarray = []
#cascparserlist = dir(CASCParser)
#adttoobjparserlist = dir(AdtToObjParser)
#objfromcascparserlist = dir(ObjFromCASCParser)

#for element in cascparserlist:
    #allfunctionarray.append(element.lower())
#for element in adttoobjparserlist:
    #allfunctionarray.append(element.lower())
#for element in adttoobjparserlist:
    #allfunctionarray.append(element.lower())


while Quit == False:
    firstanswer = raw_input('Program function, help or quit: ')
    if firstanswer.lower() == 'help':
        print 'Main Functions from AdtToObjParser: parseallADTindirectory, parseTerrain, parseWater, parseAllWMO, parseAllM2, parseM2, parseWMO'
        print 'Main Functions from CASCParser: parseAllNecessaryMapFile, parseWoWFile, getMapNames, getM2AndWMOUsingMaplistfile, readCASCData, encodeBLTEFile, Blizzhash, initializeNecessaryArrays, parseCDNConfig'
        print 'Main Functions from ObjFromCASCParser: parseAllAdtFromMapListfile, parseADTUsingCASC'
    elif firstanswer.lower() == 'quit':
        break
    else:
        try:
            exec (firstanswer)
        except Exception as e: print(e)

