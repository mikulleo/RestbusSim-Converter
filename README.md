# RestbusSim-Converter
Converter for simulation scenarios of automotive control units.

This application converts a created restbus simulation in Vector CANoe to PROVEtech:TA. The main feature is the conversion from CAPL scripting language to WinWrap Basic. Other functionality supported: conversion of simple GUI from CANoe to PROVEtech:TA; automated settings of important tags for PROVEtech:TA-specific XML files.

The application is written in Python.

Edit 4/2014:
Added the feature of the conversion from CAPL to C. The translation of CAPL's on message events is introduced. Events are handled by using SocketCAN and libev.

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
   
    


  
  
