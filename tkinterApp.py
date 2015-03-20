# -*- coding: iso-8859-1 -*-

#
# Copyright 2015 Leos Mikulka
#
# This file is part of RestbusSim-Converter.

# RestbusSim-Converter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# RestbusSim-Converter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with RestbusSim-Converter.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Leos Mikulka"
__copyright__ = "Copyright 2015, Leos Mikulka"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "mikulkal@hotmail.com"


import tkinter as tk
from tkinter import *
from tkinter import filedialog
from lxml import etree
import os.path
import io
from panelsWindow import PanelsWindow
from parserPy import Parser

class App:
    
    def next_btn_callback(self,preConf,portName,bitRate,dbc,xmlr):
        tree = etree.parse(preConf.get())           # parse Provetech:RE config file
        root = tree.getroot()                       # get root of an xml tree
 

        find_portName = etree.XPath("/RCConfiguration/Device/Config/Port/Name/text()")
        port_name_xml = find_portName(tree)[0]      # get a port name from the xml-file
        print(port_name_xml)

        port_name_app = portName.get()              # get a port name from the text field
        if (port_name_xml == port_name_app):
            print("Port found...")
            bit_rate = tree.xpath('//RCConfiguration/Device/Config/Port/Config/BitRate')        # xml-path of bit rate
            bit_rate[0].text = bitRate.get()
            bit_rate_text = bit_rate[0].text
            dbc_arxml = tree.xpath('//RCConfiguration/Device/Config/Port/Config/NWDescriptor')  # xml-path of DBC/ARXML file
            dbc_arxml[0].text = dbc.get()
            dbc_arxml_text = dbc_arxml[0].text
            xml_rbs = tree.xpath('//RCConfiguration/Device/Config/Port/Config/RBSDescriptor')    # xml-path of xml for Rest-bus sim. file
            xml_rbs[0].text = xmlr.get()
            xml_rbs_text = xml_rbs[0].text

            # check whether all text fields are not empty and write to an output
            if (not bit_rate_text or not dbc_arxml_text or not xml_rbs_text):
                print("ERROR! Empty field.") 
            else:
                etree.ElementTree(root).write(preConf.get(), pretty_print=True)
                print("Values in the output XML file set.")

        else:
            print("ERROR! Port not found.")

    def select_pre_callback(self,preConf):
        file = tk.filedialog.askopenfilename(**self.file_opt)
        file = os.path.normpath(file)       # normalize path, i.e. backslashes on Win, fwd-slashes on Unix and Mac
        preConf.delete(0,END)
        preConf.insert(0,file)

    def select_dbc_callback(self,dbcarxml):
        file = tk.filedialog.askopenfilename(**self.file_opt)
        file = os.path.normpath(file)       # normalize path, i.e. backslashes on Win, fwd-slashes on Unix and Mac
        dbcarxml.delete(0,END)
        dbcarxml.insert(0,file)

    def select_xmlRbs_callback(self,xmlrbs):
        file = tk.filedialog.askopenfilename(**self.file_opt)
        file = os.path.normpath(file)       # normalize path, i.e. backslashes on Win, fwd-slashes on Unix and Mac
        xmlrbs.delete(0,END)
        xmlrbs.insert(0,file)

    def layout_scheme(self,master):         # basic layout

        pre_label = LabelFrame(master, text=u"P:RE config")
        pre_label.grid(row=0,column=0)
        pre_label.config(font="Cambria 14", padx=10,pady=7,bd=4,relief="groove",width=13)
        dbcArxml_label = LabelFrame(master, text=u"dbc/arxml file")
        dbcArxml_label.grid(row=1,column=0)
        dbcArxml_label.config(font="Cambria 14", padx=10,pady=7,bd=4,relief="groove",width=13)
        xmlRbs_label = LabelFrame(master, text=u"xml RBS file")
        xmlRbs_label.grid(row=2,column=0)
        xmlRbs_label.config(font="Cambria 14", padx=10,pady=7,bd=4,relief="groove",width=13)
        port_label = LabelFrame(master, text=u"Port Name")
        port_label.grid(row=3,column=0)
        port_label.config(font="Cambria 14", padx=10,pady=7,bd=4,relief="groove",width=13)
        bitRate_label = LabelFrame(master, text=u"Bit Rate")
        bitRate_label.grid(row=4,column=0)
        bitRate_label.config(font="Cambria 14", padx=10,pady=7,bd=4,relief="groove",width=13)

        pre_path = StringVar()
        pre_path.set("E:\Documents\CVUT Praha\Ing\Diplomova prace\PROVEtech\generatedTest.xml")
        dbcArxml_path = StringVar()
        dbcArxml_path.set("E:\Documents\CVUT Praha\Ing\Diplomova prace\PROVEtech\HeadUnit_NTG55\HeadUnit_NTG55_2014\Converted_205_217_222_253_HEADUNIT_CAN_2014_29a_dSPACE.dbc")
        xmlRbs_path = StringVar()
        xmlRbs_path.set("E:\Documents\CVUT Praha\Ing\Diplomova prace\PROVEtech\HeadUnit_NTG55\HeadUnit_NTG55_2014\205_217_222_253_HEADUNIT_CAN_2014_29a_dSPACE.xml")
        port_name_init = StringVar()
        port_name_init.set("HU_CAN")


        e_pre = Entry(pre_label,textvariable = pre_path)
        e_pre.grid(row=0,column=1)
        e_pre.config(font="Cambria 12",bd=2,relief="groove",width=75)
        e_dbcArxml = Entry(dbcArxml_label,textvariable = dbcArxml_path)
        e_dbcArxml.grid(row=1,column=1)
        e_dbcArxml.config(font="Cambria 12",bd=2,relief="groove",width=75)
        e_xmlRbs = Entry(xmlRbs_label,textvariable = xmlRbs_path)
        e_xmlRbs.grid(row=2,column=1)
        e_xmlRbs.config(font="Cambria 12",bd=2,relief="groove",width=75)
        e_port = Entry(port_label,textvariable = port_name_init)          # grid must be introduced later; otherwise NoneType error
        e_port.grid(row=3,column=1)
        e_port.config(font="Cambria 12",bd=2,relief="groove",width=75)
        e_bitRate = Entry(bitRate_label)
        e_bitRate.grid(row=4,column=1)
        e_bitRate.config(font="Cambria 12",bd=2,relief="groove",width=75)
        
        select_preconf_btn = Button(master, text=u"SELECT", command = lambda: self.select_pre_callback(e_pre))
        select_preconf_btn.config(width=10,padx=10,pady=10,bd=2,font="Cambria 12")
        select_preconf_btn.grid(row=0,column=1)
        select_dbc_btn = Button(master, text=u"SELECT", command = lambda: self.select_dbc_callback(e_dbcArxml))
        select_dbc_btn.config(width=10,padx=10,pady=10,bd=3,font="Cambria 12")
        select_dbc_btn.grid(row=1,column=1)
        select_xmlrbs_btn = Button(master, text=u"SELECT", command = lambda: self.select_xmlRbs_callback(e_xmlRbs))
        select_xmlrbs_btn.config(width=10,padx=10,pady=10,bd=3,font="Cambria 12")
        select_xmlrbs_btn.grid(row=2,column=1)
        next_btn = Button(master, text=u"GENERATE XML", command = lambda: self.next_btn_callback(e_pre,e_port,e_bitRate,e_dbcArxml,e_xmlRbs))
        next_btn.grid(row=4,column=1)
        next_btn.config(width=10,padx=10,pady=5,bd=3,font="Cambria 14",wraplength=100)


    def layout_scheme_bottom(self,master):
        
        panels_conv_btn = Button(master, text=u"GUI & CODE CONVERSION", command = lambda: PanelsWindow(master))
        panels_conv_btn.grid(row=5,column=1)
        panels_conv_btn.config(width=50,padx=20,pady=5,bd=3,font="Cambria 12")

    def __init__(self,master):
        frame_top = Frame(master)
        frame_top.grid(row = 0, column = 0, rowspan = 5, columnspan = 2, sticky = W+E+N+S,padx=5,pady=(5,1)) 
        frame_bottom = Frame(master)
        frame_bottom.grid(row = 5, column = 0, rowspan = 1, columnspan = 2, sticky = W+E+N+S,padx=(70,50),pady=(0,2))
        self.layout_scheme(frame_top)
        self.layout_scheme_bottom(frame_bottom)
        #frame.pack()

        self.file_opt = options = {}
        options['defaultextension'] = '.xml'
        options['filetypes'] = [('all files', '.*'), ('XML files', '.xml'),('DBC files','.dbc'),('AUTOSAR files','.arxml')]
        options['initialdir'] = 'C:\\'
        options['parent'] = root 
        options['title'] = 'Select file'
    
if __name__ == '__main__':
    #root = tk.Tk()

    #app = App(root)

  

    parser_init = Parser("E:\Documents\CVUT Praha\Ing\Diplomova prace\code\compiler\compiler\ex.txt")
        
    #root.mainloop()
