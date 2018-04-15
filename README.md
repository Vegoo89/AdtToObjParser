# ADTtoOBJ with CASC File Parser

This program is simple parser of World of Warcraft adt files. It's using WoW Legion version 7.3.5.26124
It's creating geometry that later can be used for example in Recast to create navigation mesh.
Generated Obj files only contain vertices and faces (additionally water vertices contain blue rgb so they are easy to identify).


## Getting Started

Project is written in Python 2.7 x64 and should be used under Windows.
Almost all required modules are inclued in basic Python, if something is missing use pip to install it. Modules that you may need to install:

```
jenkins-python

multiprocess

psutil

requests
```

### Installing

If you wish to compile basic program version you can do it by using pyinstaller module.

```
1. Install pyinstaller using pip
2. Navigate to destination folder in command line and execute command:
pyinstaller --onefile ParserProgram.py
3. Pyinstaller should generate exe file in dist folder in currect directory.

```

## Functions Overview

AdtToObjParser module is main parsing module that uses extracted adt, m2 and wmo files and converts them into obj format.

Main Functions from AdtToObjParser: parseallADTindirectory, parseTerrain, parseWater, parseAllWMO, parseAllM2, parseM2, parseWMO

```
parseallADTindirectory(mainfolderpath, outputfolderpath, startfolderindex=0, endfolderindex=9999,overwritefiles=True, highlevelofdetails=False)
```

```
parseTerrain(adtfilename, outputfolder=None, useCASCParser=False, cascfileinput=None)
```

```
parseWater(adtfilename, outputfolder=None, useCASCParser=False, cascfileinput=None)
```

```
parseAllWMO(filename, mapfolderlocation, outputfolderpath=None, highlevelofdetails=False, useCASCParser=False, cascfileinput=None)
```

```
parseAllM2(filename, mapfolderlocation, outputfolderpath=None, useCASCParser=False, cascfileinput=None)
```

```
parseM2(adtfilename, folderpath, filepath, posy, posz, posx, rotationy, rotationz, rotationx, scale, outputfolder=None, useCASCParser=False, cascfileinput=None)
```

```
parseWMO(adtfilename, folderpath, filepath, posy, posz, posx, rotationy, rotationz, rotationx, outputfolder=None, useCASCParser=False, cascfileinput=None)
```

Example:

```
parseallADTindirectory('E:\\MapsLegion\\', 'E:\\MapsObjParserOutput\\', 617, 700, True)
```

mainfolderpath should have structure of listfile (for example World\Maps\Kalimdor\Kalimdor_29_39.adt)





CASCParser module can parse files using their listfile names or generate list of adt, m2 and wmo files from given WoW folder.

Main Functions from CASCParser: parseAllNecessaryMapFile, parseWoWFile, getMapNames, getM2AndWMOUsingMaplistfile, readCASCData, encodeBLTEFile, Blizzhash, initializeNecessaryArrays, parseCDNConfig, getAllStringFromDB2Files, getDB2FileListFromWowClient

```
parseAllNecessaryMapFile(mainwowfolder, outputfolder, workernumber=4)
```

```
getM2AndWMOUsingMaplistfile(mainwowfolder, remakemaplistfile=False, workernumber=1)
```

```
getMapNames(wowfolderpath)
```

```
parseWoWFile(namefromlistfile, mainwowfolder, fixstring=True, returnparamsarray=False)
```

```
readCASCData(firstbyte, beuint32, sizeofdata, mainwowfolderpath)
```

```
initializeNecessaryArrays(encodingCDNHash, rootEncodedHash, mainwowfolder, specificlocale=None)
```

```
Blizzhash(string, fixstring=True)
```

```
parseCDNConfig(mainwowfolder, fixedregion='us', customcdnurl=None)
```

```
getDB2FileListFromWowClient(mainwowfolder, currentversion='7.3.5.26124', currentversionoffset=0x129D588, currentdb2offset=0x1815EB0)
```

```
getAllStringFromDB2Files(db2listfilepath, mainwowfolder)
```

Example:
parseAllNecessaryMapFile('C:\\World of Warcraft\\', 'E:\\Outputfolder\\', 3)




ObjFromCASCParser is connector module

Main Functions from ObjFromCASCParser: parseAllAdtFromMapListfile, parseADTUsingCASC

```
parseADTUsingCASC(adtfilenamefromlistfile, wowfolderpath, outputfolder=None)
```

```
parseAllAdtFromMapListfile(mainwowfolder, outputfolder=None, recreatemaplistfile=False, overwritefiles=False, startindex=0, stopindex=999999)
```

Example:
parseAllAdtFromMapListfile('C:\\World of Warcraft\\', 'E:\\Testfoldercascparser\\', False, False, 0, 55)


## Acknowledgments

* http://wowdev.wiki (Amazing info about WoW files and CASC archives)
* Ownedcore forum members
