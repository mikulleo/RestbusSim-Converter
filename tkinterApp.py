# -*- coding: iso-8859-1 -*-

# main for GUI
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
from panelsWindow import PanelsWindow

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
        Label(master, text=u"P:RE config").grid(row=0,column=0)
        Label(master, text=u"dbc/arxml file").grid(row=1,column=0)
        Label(master, text=u"xml RBS file").grid(row=2,column=0)
        Label(master, text=u"Port Name").grid(row=3,column=0)
        Label(master, text=u"Bit Rate").grid(row=4,column=0)

        pre_path = StringVar()
        pre_path.set("E:\Documents\CVUT Praha\Ing\Diplomova prace\PROVEtech\generatedTest.xml")
        dbcArxml_path = StringVar()
        dbcArxml_path.set("E:\Documents\CVUT Praha\Ing\Diplomova prace\PROVEtech\HeadUnit_NTG55\HeadUnit_NTG55_2014\Converted_205_217_222_253_HEADUNIT_CAN_2014_29a_dSPACE.dbc")
        xmlRbs_path = StringVar()
        xmlRbs_path.set("E:\Documents\CVUT Praha\Ing\Diplomova prace\PROVEtech\HeadUnit_NTG55\HeadUnit_NTG55_2014\205_217_222_253_HEADUNIT_CAN_2014_29a_dSPACE.xml")
        port_name_init = StringVar()
        port_name_init.set("HU_CAN")


        e_pre = Entry(master,textvariable = pre_path,width = 125)
        e_pre.grid(row=0,column=1)
        e_dbcArxml = Entry(master,textvariable = dbcArxml_path,width = 125)
        e_dbcArxml.grid(row=1,column=1)
        e_xmlRbs = Entry(master,textvariable = xmlRbs_path,width = 125)
        e_xmlRbs.grid(row=2,column=1)
        e_port = Entry(master,textvariable = port_name_init)          # grid must be introduced later; otherwise NoneType error
        e_port.grid(row=3,column=1)
        e_bitRate = Entry(master)
        e_bitRate.grid(row=4,column=1)
        
        select_preconf_btn = Button(master, text=u"SELECT", command = lambda: self.select_pre_callback(e_pre))
        #select_preconf_btn.config(width = 16, height = 3, font = ("Helvetica", "10", "bold"))
        select_preconf_btn.grid(row=0,column=2)
        select_dbc_btn = Button(master, text=u"SELECT", command = lambda: self.select_dbc_callback(e_dbcArxml))
        #select_dbc_btn.config(width = 16, height = 3, font = ("Helvetica", "10", "bold"))
        select_dbc_btn.grid(row=1,column=2)
        select_xmlrbs_btn = Button(master, text=u"SELECT", command = lambda: self.select_xmlRbs_callback(e_xmlRbs))
        #select_xmlrbs_btn.config(width = 16, height = 3, font = ("Helvetica", "10", "bold"))
        select_xmlrbs_btn.grid(row=2,column=2)
        next_btn = Button(master, text=u"NEXT", command = lambda: self.next_btn_callback(e_pre,e_port,e_bitRate,e_dbcArxml,e_xmlRbs))
        #next_btn.config(width = 16, height = 3, font = ("Helvetica", "10", "bold"))
        next_btn.grid(row=5,column=2)
        panels_conv_btn = Button(master, text=u"PANELS", command = lambda: PanelsWindow(master))
        panels_conv_btn.grid(row=6,column=2)

    def __init__(self,master):
        frame = Frame(master)
        #frame.pack()
        self.layout_scheme(master)

        self.file_opt = options = {}
        options['defaultextension'] = '.xml'
        options['filetypes'] = [('all files', '.*'), ('XML files', '.xml'),('DBC files','.dbc'),('AUTOSAR files','.arxml')]
        options['initialdir'] = 'C:\\'
        options['parent'] = root 
        options['title'] = 'Select file'
    
if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    
    root.mainloop()
