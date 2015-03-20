# RestbusSim-Converter
Converter for simulation scenarios of automotive control units.

This application converts a created restbus simulation in Vector CANoe to PROVEtech:TA. The main feature is the conversion from CAPL scripting language to WinWrap Basic. Other functionality supported: conversion of simple GUI from CANoe to PROVEtech:TA; automated settings of important tags for PROVEtech:TA-specific XML files.

The application is written in Python.

## Project files
<b> Note: </b> the files will be renamed

- ` tkinterApp.py `

  Window for setting of PROVEtech:TA-specific XML file
  
- ` panelsWindow.py`

  Window for GUI and CAPL conversion
  
- ` lexer.py `

  Lexer used during parsing
  
- ` parserPy.py `

  CAPL parser with subsequent translation to WinWrap Basic
  
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
   
    


  
  
