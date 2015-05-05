# RestbusSim-Converter
Converter for simulation scenarios of automotive control units.

This application converts a created restbus simulation in Vector CANoe to PROVEtech:TA. The main feature is the conversion from CAPL scripting language to WinWrap Basic. Other functionality supported: conversion of simple GUI from CANoe to PROVEtech:TA; automated settings of important tags for PROVEtech:TA-specific XML files. The feature of the conversion from CAPL to C for the Linux platform has been added. The translation of CAPL's on message events is introduced. Events are handled by using SocketCAN and libev.

The program is written in Python 3.4. The modules needed for compiling the program are:
- `io`, `string`, `mmap`, `os`, `tkinter`, `lex` and `yacc` (lex and yacc are included in Ply package available at: http://www.dabeaz.com/ply/ply-3.6.tar.gz)

For running the tool, tkinterApp.py file needs to be executed. Conversions are run by using the GUI. 

Steps for code conversion: <i> GUI & Code Conversion </b> -> <i> Convert CAPL -> WWB </i> / <i> Convert CAPL -> C </i>

Steps for GUI conversion: <i> GUI & Code Conversion </i> -> <i> Convert XVP -> AOF </i>


## Project files
<b> Note: </b> the files will be renamed

### Main Application

- ` tkinterApp.py `

  Window for setting of PROVEtech:TA-specific XML file
  
- ` panelsWindow.py`

  Window for GUI and CAPL conversion
  
- ` lexer.py `

  Lexer used during parsing
  
- ` parserPy.py `

  CAPL parser with subsequent translation to WinWrap Basic and/or C
  
### Reaction on received messages in C

For translating message events, the `msgEvents.c` file must be included in path `eventsHandler/msgEvents.c`.

- `socketCan.h`, `socketCan.c`

  Set up of the connection over CAN bus
  
- `reverse_gear/sent_rcv_libev.c`

  Example of shifting the reverse gear by using receiving and sending messages using libev
  
- `eventsHandler/msgEvents.c`
  
  Code for handling received messages - switch statements is automatically generated during translation from CAPL

  
## CAPL conversion - usage

<b> Example file for the translation can be found in ` working_example.txt `. </b>

- CAPL specific comments must be included during declaration
  
    ex.:
    
    ` /*@@var: */ `
    
    ` variables { ... } `
    
    ` /*@@end */ `
    
    ` /*@@caplFunc:speedTest(float speed, float clock): */ `
    
    ` float speedTest(float speed, float clock) { ... } `
    
    ` /*@@end */ `
    
    ` /*@@msg:message1: */ `
    
    ` on message message1 { ... } `
    
    ` /*@@end */ `
    
  
- max. binary expressions are supported for translation
  
    ex.:
    
    ` x = a + b `
    
    ` if (x != 0 && y > 0) { ... } `
    
    
- only simple FOR loops are currently supported for translation
   
    ex.: ` for(int i; i < 10; i++) { ... } `
    
- parsing of expressions in array indices is not supported
   
   ex.: ` arr[i++] `
   
    


  
  
