#!bin/python
#-*- coding: utf-8 -*-
#
###############################################
# Author: Ahmed Youssef
# Program: GladizerGUI v1
# Website: http://www.programming-fr34ks.net
###############################################

# Copyright (C) 2008, Ahmed Youssef <guru.python@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from Tkinter import *
import tkFileDialog as tfd
import tkMessageBox as tmd
from gladizer import getplugins, CodeGenerator
import os
import os.path as op
import traceback

class GladizerWindow(Frame):

    def __init__(self, master=None):

         Frame.__init__(self, master)

         self.title="GladizerGUI"

         self._inputfile=StringVar()
         self._outputfile=StringVar()
         self._usedplugin=None

         self._init_comps()


    def _init_comps(self):


        inp=Button(self, text="Input", command=self._getinputfile)
        inp.grid(row=0, sticky=W+N)

        self.inpentry=Entry(self, textvariable=self._inputfile)
        self.inpentry.grid(row=0, column=1, sticky=E)

        out=Button(self, text="Output", command=self._getoutputfile)
        out.grid(row=1, sticky=W+N)


        self.outentry=Entry(self, textvariable=self._outputfile)
        self.outentry.grid(row=1, column=1, sticky=E)

        Label(self, text="Plugins:").grid(row=2, column=0, sticky=N+W)
        #plugins list.
        self.lbplugins=Listbox(self, height=5, selectmode=BROWSE, relief=SUNKEN)
        self.lbplugins.grid(row=2, column=1, columnspan=3, sticky=E+S)
        if len(getplugins())>=1:
            for plugin in getplugins():
                self.lbplugins.insert(0, plugin)

        self.lbplugins.select_set(0)

        start=Button(self, text="Gladize!", command=self._gladize).grid(row=3, columnspan=2, sticky=E+S)
        self.grid()

    def _getinputfile(self, *args):

        self._inputfile.set(tfd.askopenfilename())
        #self.inpentry.delete(0, END)
        #self.inpentry.insert(0, self._inputfile)


    def _getoutputfile(self, *args):

        self._outputfile.set(tfd.asksaveasfilename())
        #self.outentry.delete(0, END)
        #self.outentry.insert(0, self._outputfile)

    def showerror(self, msg):
        tmd.showerror("Error", msg)
    def _gladize(self):
        if self._inputfile.get() and self._outputfile.get():
            if not op.exists(self._inputfile.get()):
                self.showerror("Specify a valid .glade file.")

            if not len(self.lbplugins.curselection())>=1:
                self.showerror("Specify a plugin.")
                self.lbplugins.select_set(0)
                return

            self._usedplugin=self.lbplugins.get(self.lbplugins.curselection()[0])
            #print "Going on with %s => %s with %s plugin"%(self._inputfile, self._outputfile, self._usedplugin)

            try:
                f=file(self._outputfile.get(), "w")
                f.write(CodeGenerator(self._inputfile.get(), self._usedplugin).generate())
                tmd.showinfo("Gladized", "%s gladized successfully!"%self._outputfile.get())
            except Exception, e:
                pass
                #traceback.print_exc(file=sys.stdout)
            finally:
                f.close()

        else:
            self.showerror("Specify valid data.")
            return



def main():

    root=Tk()               #Master
    gw=GladizerWindow(root) #GladizerWindow
    root.mainloop()         #Entering the mainloop

if __name__=="__main__":
    main()


