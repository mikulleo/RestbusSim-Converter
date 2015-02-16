# -*- coding: iso-8859-1 -*-

# panels for GUI
#
# Author: Leos Mikulka (mikulkal@hotmail.com)
# Date:

__author__ = "Leos Mikulka"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "mikulkal@hotmail.com"

import tkinter as tk
from tkinter import *
from tkinter import filedialog
from lxml import etree
import os.path
import io
from enum import Enum

from parserPy import Parser

class Ctrl(Enum):
    CheckBoxControl = 1
    ButtonControl = 2
    SwitchControl = 3
    RadioButtonControl = 4
    ComboBoxControl = 5
    MeterControl = 6
    AnalogGaugeControl = 7
    LCDControl = 8

class PanelsWindow:

    # Pythonic way of switch-case stmt
    def checkbox():
        return Ctrl.CheckBoxControl

    def button():
        return Ctrl.ButtonControl

    def switch():
        return Ctrl.SwitchControl

    def radio_button():
        return Ctrl.RadioButtonControl

    def combo_box():
        return Ctrl.ComboBoxControl

    def meter():
        return Ctrl.MeterControl

    def analog_gauge():
        return Ctrl.AnalogGaugeControl

    def lcd():
        return Ctrl.LCDControl

    objects_options = { 'CheckBoxControl' : checkbox,
                       'ButtonControl' : button,
                       'SwitchControl' : switch,
                       'RadioButtonControl' : radio_button,
                       'ComboBoxControl' : combo_box,
                       'MeterControl' : meter,
                       'AnalogGaugeControl' : analog_gauge,
                       'LCDControl' : lcd,
                    }           

    def convert_xvp_callback(self,xvpFiles):
        xvpFiles_list = (xvpFiles.get()).split(",")
        
        panel_id = 1
        for xvpFile in xvpFiles_list:

            tree = etree.parse(xvpFile)           # parse xvp file
            root = tree.getroot()                       # get root of an xml tree
 
            controls_list = []
            design_list = []

            #objects = tree.xpath("Object/Object/@Type")      # select attribute Type of all tags Object inside Panels.Runtime.Panel
            objects = tree.xpath("Object/Object")  

            for num in range(1,len(objects)+1):              # iterate through objects      
                # from an attribute Type of tag Object select an actual type of an object (e.g. CheckBoxControl)
                object = tree.xpath("/Panel/Object/Object[%s]/@Type" % num)
                object_typeAttr = object[0]
                object_typeAttr_list = object_typeAttr.split(",")    # split all entries of type (i.e. attributes to list)
                object_vectorType_list = (object_typeAttr_list[0]).split(".")   # select the first entry and split so we can get type of an object
                object_type = object_vectorType_list.pop()            # actual type (e.g. CheckBoxControl) is located as the last element 

                object_type = self.objects_options[object_type]()    # convert to ENUM type

                # select text inside tags <Property Name='SymbolConfiguration'>
                prop_config = tree.xpath("/Panel/Object/Object[%s]/Property[@Name='SymbolConfiguration']/text()" % num)
                object_config_entry = prop_config[0]
                object_config_list = object_config_entry.split(";")     # put all properties from SymbolConfiguration into a list

                node = object_config_list[3]
                message = object_config_list[4]
                signal = object_config_list[5]
                dbc_file = object_config_list[7]

                prop_position = tree.xpath("/Panel/Object/Object[%s]/Property[@Name='Location']/text()" % num)
                object_position = prop_position[0]
                object_position = object_position.split(", ")
                prop_size = tree.xpath("/Panel/Object/Object[%s]/Property[@Name='Size']/text()" % num) 
                object_size = prop_size[0]
                object_size = object_size.split(", ")
                prop_label = tree.xpath("/Panel/Object/Object[%s]/Property[@Name='Text']/text()" % num) 
                object_label = prop_label[0]

                controls_list.append([('ID',num),(object_type),('Node',node),('Message',message),('Signal',signal),('DBC',dbc_file)])
                design_list.append([('Position',object_position),('Size',object_size),('Label',object_label)])
          
            self.generate_code_aof(panel_id,controls_list, design_list)
            panel_id += 1

    def generate_code_aof(self,panel_id,controls,design):
        string = ""
        if (panel_id == 1):
            f = open('text.txt','w')
            string += "[Allgemein]\n"+"Version=3\n"+"LeftSide=0\n"+"[ErfassSignale]\n"+"SignalschlüsselListe=\n"
            string += "[Page%s]\n" % str(panel_id)
            string += "SCROLLPOS=0|0\n"
        else:
            f = open('text.txt','a')
            string += "[Page%s]\n" % str(panel_id)
            string += "SCROLLPOS=0|0\n"

        # example: output[0][0][1] = 1st object, 1st tuple ('ID',num), value (num)
        for i in range(0,len(controls)):
            object_type = controls[i][1]

            if (object_type == Ctrl.ButtonControl) or (object_type == Ctrl.CheckBoxControl):
                if not (str(controls[i][2][1])=="" and str(controls[i][3][1])==""):     # empty message and signal ---> i.e. variable
                    string += "BOOLCONTROL=Signalschlüssel:TX."
                    for j in range (2,5):   # positions in control_list
                        if (j < 4):
                            string += str(controls[i][j][1])+'.'
                        else:
                            string += str(controls[i][j][1])+';'

                    x_pos = design[i][0][1][0]      # i-th tuple, 1st tuple, value, x-position
                    y_pos = design[i][0][1][1]
                    width = design[i][1][1][0]
                    height = design[i][1][1][1]

                    # TODO!! XSize YSize are probably not aof specific!!
                    specific_aof_attributes_1 = "XSize:7;YSize:1;Shortname:1;ColorOn:255;ColorOff:8421504;ButtonStyle:7;TextAlignment:0;ButtonAlignment:2;"
                    specific_aof_attributes_2 = "ButtonMode:1;IsHiActive:1;\n"

                    string += "XPos:%s;YPos:%s;" % (x_pos,y_pos)
                    string += specific_aof_attributes_1
                    string += "ButtonHeight:%s;ButtonWidth:%s;" % (height,width)
                    string += specific_aof_attributes_2
                else:
                    pass

            

        f.write(string)
        print("Transfer to AOF file successful.")

    def select_xvp_callback(self,xvp):
        files = tk.filedialog.askopenfilenames(**self.file_opt)

        xvp.delete(0,END)
        last = len(files)-1

        for i,file in enumerate(files):
            file = os.path.normpath(file)       # normalize path, i.e. backslashes on Win, fwd-slashes on Unix and Mac
            if (i == last):
                xvp.insert(END,file)
            else:
                xvp.insert(END,file+",")

    def convert_capl_callback(self,caplFile):
        parser_init = Parser(caplFile)

    def select_capl_callback(self,capl):
        file = tk.filedialog.askopenfilename(**self.file_opt)
        file = os.path.normpath(file)       # normalize path, i.e. backslashes on Win, fwd-slashes on Unix and Mac
        capl.delete(0,END)
        capl.insert(0,file)


    def layout_scheme(self,master):
        xvp_path = StringVar()
        xvp_path.set("E:\Documents\CVUT Praha\Ing\Diplomova prace\CANoe_milan\Panels\Panel1.xvp")
        capl_path = StringVar()
        capl_path.set("E:\Documents\CVUT Praha\Ing\Diplomova prace\code\compiler\compiler\ex.txt")

        e_xvp = Entry(master,textvariable = xvp_path,width = 125)
        e_xvp.grid(row = 0)
        e_capl = Entry(master,textvariable = capl_path,width = 125)
        e_capl.grid(row = 1)

        convert_xvp_btn = Button(master, text=u"CONVERT XVP", command = lambda: self.convert_xvp_callback(e_xvp))
        convert_xvp_btn.grid(row=2,column = 1)
        select_xvp_btn = Button(master, text=u"SELECT", command = lambda: self.select_xvp_callback(e_xvp))
        select_xvp_btn.grid(row=0, column=1)
        convert_capl_btn = Button(master, text=u"CONVERT CAPL", command = lambda: self.convert_capl_callback(e_capl))
        convert_capl_btn.grid(row=3,column = 1)
        select_capl_btn = Button(master, text=u"SELECT", command = lambda: self.select_capl_callback(e_capl))
        select_capl_btn.grid(row=1, column=1)

    def __init__(self,master):
        top = tk.Toplevel(master)
        l = tk.Label(top, text="Panels Conversion")
        top.title(u"Panels Conversion")
        self.layout_scheme(top)         # put top as a master

        self.file_opt = options = {}
        options['defaultextension'] = '.xvp'
        options['filetypes'] = [('all files', '.*'), ('XVP files', '.xvp'),('AOF files', '.aof')]
        options['initialdir'] = 'C:\\'
        options['parent'] = top
        options['title'] = 'Select file'