#!bin/python
#-*- coding: utf-8 -*-


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

##DONE
# + Plugin interface
# + Python plugin
# + Ruby plugin
# + Code Generator.


##TODOS:
# -Enable DTD
# -Use minidom instead of XML
# -Add static languages support (Keep track of class attribute <widget class=SOMECLASS id=SOMEID>
# -Add Doc-Strings.
# -Add support for Perl, Java, C/C++
# -Add a man page.



#Imports
import sys
from optparse import OptionParser
from xml import sax
from xml.sax import *

__PLUGINS=["Python", "Ruby"]

def getplugins():
    return globals()["__PLUGINS"]

def tabs2spaces(txt):
    return txt.replace("\t", "    ")
    
class SignalHandler(object): ##Keep track of the class (e.g class="GtkWindow") for static langugaes. next release.

    def __init__(self, signal, handler):

        self._signal=signal #signal name..
        self._handler=handler

    signal=lambda self: self._signal
    handler=lambda self: self._handler

    __str__=lambda self: "<WidgetModel (%s -> %s)>"%(self._signal, self._handler)

class Widget(object):

    def __init__(self, type_, id_):
        self._type=type_
        self._id=id_

    type_=lambda self: self._type
    id_  =lambda self: self._id

    __str__=lambda self: "<%s: %s>"%(self._type, self._id)



class GladeContentHandler(ContentHandler):

    def __init__(self):
        self._inwidget=False
        self._insignal=False
        self._curel=""
        self._widgets=[]
        self._store=[]


    def startElement(self, el, attrs):
        self._curel=el
        if el in ("widget","object"):
            self._inwidget=True
            _id=attrs["id"].replace("-", "_")
            _class=attrs["class"]
            self._widgets +=[Widget(_class, _id)] #<widget class="GtkWindow" id="window1">
        if el=="signal":
            self._insignal=True
            self._store += [SignalHandler(attrs["name"], attrs["handler"])]
            #convert it to a valid python name..


    def endElement(self, el):
        if el in ("widget", "object"):
            self._inwidget, self._insignal=False, False

    def characters(self, content): #should be used with properties
        pass

    widgets=lambda self: [w.id_() for w in self._widgets]
    fullwidgetsinfo=lambda self: self._widgets

    def store(self):
        return self._store

    def signals(self):
        return [x.signal() for x in self._store]

    def handlers(self):
        return [x.handler() for x in self._store]


    def get_root(self):
        return self._widgets[0]



class Plugin(object):

    def __init__(self, filename, widgetsinfo, store, outclass, testable=False, usinggtkbuilder=False):
        self._filename=filename
        self._widgets=[w.id_() for w in widgetsinfo]
        self._store=store
        self._gentest=testable
        self._outclass=outclass
        self._usinggtkbuilder=usinggtkbuilder
    
    def header_and_imports(self):
        pass

    def code_body(self):
        pass

    def callbacks(self):
        pass

    def test(self):
        pass

    def commonfooter(self):
        pass

    def generate_code(self):
        return tabs2spaces(self.header_and_imports()+self.code_body() + self.callbacks() + self.test()+ self.commonfooter())


class PythonPlugin(Plugin):

    def __init__(self, filename, widgetsinfo, store, testable, outclass="MainWindow",  usinggtkbuilder=True):

        super(PythonPlugin, self).__init__(filename,widgetsinfo, store, outclass, testable, usinggtkbuilder)
        


    def header_and_imports(self):
        
        fileheader="""
#!bin/python

##CODE GENERATED by gladizer 1.2
        

import pygtk
pygtk.require('2.0')

import gtk\n"""
        if not self._usinggtkbuilder:
            fileheader +="import gtk.glade\n"
        fileheader +="""

class %s(object):

\tdef __init__(self):
    """%self._outclass
       
        
        return fileheader

    def code_body(self):
        cbody="\n"
        if self._usinggtkbuilder:
            print "gtkbuilder..."
            cbody +="""\t\t# #builder
\t\tself.builder=gtk.Builder()
\t\tself.builder.add_from_file("%s")
            
\t\t #connect signals and handlers.
\t\tself.builder.connect_signals(self)
            
"""%(self._filename)
            
            for w in self._widgets:
                cbody +="\t\tself._%s=self.builder.get_object('%s')\n"%(w, w)
            print cbody
            cbody +="\t\tself._%s.show()"%self._widgets[0]
                
        else:
  
            cbody +="""
\t\t#Widget tree..
\t\tself.wTree=gtk.glade.XML('%s')

\t\t#connect signals and handlers.
\t\tself.wTree.signal_autoconnect(self)

"""%(self._filename)
            for w in self._widgets:
                cbody +="\t\tself._%s=self.wTree.get_widget('%s')\n"%(w, w)

            cbody +="\t\tself._%s.show()"%self._widgets[0]
            
        return cbody

    def callbacks(self):
        handlers=""
        for x in self._store:
            handler=x.handler()
            signal=x.signal()
            #if signal=="delete_event": #do it by hand!
            #    handlers +="\n\tdef %s(self,widget, *args):\n\t\t\tgtk.main_quit(); return False\n\n"%handler # widget, object
            #    continue #dobuled if not.
            handlers +="""\n\tdef %s(self, widget, *args):\n\t\tpass\n"""%handler #widget, event

        return handlers


    def test(self):
        return "\n"

    def commonfooter(self):
        footer="""# run main loop\n
def main():
\t%s = %s()
\t#%s.%s.show()
\tgtk.main()

if __name__ == "__main__":
\tmain()
"""%(self._outclass.lower(), self._outclass, self._outclass.lower(), self._widgets[0])
        return footer

class RubyPlugin(Plugin):

    def __init__(self, filename, widgetsinfo, store, testable, outclass="MainWindow", usinggtkbuilder=False):
        super(RubyPlugin, self).__init__(filename,widgetsinfo, store, outclass, testable, usinggtkbuilder)


    def header_and_imports(self):
        header="""#!bin/ruby

##This file is generated by Gladizer 1.2
#
#
##

require 'libglade2'

class %s
\tinclude GetText
\tattr :glade

\tdef initialize(path_or_data, root = nil, domain = nil, localedir = nil, flag = GladeXML::FILE)
\t\tbindtextdomain(domain, localedir, nil, "UTF-8")
\t\t@glade = GladeXML.new(path_or_data, root, domain, localedir, flag) {|handler| method(handler)}

"""% self._outclass
        return header

    def code_body(self):
        widgets=""
        for w in self._widgets:
            widgets +="\t\t@%s=@glade.get_widget('%s')\n\n"%(w, w)

        #call the main window show method..
        widgets +="\t\t@%s.show"%(self._widgets[0])
        return widgets +"\n\tend\n"


    def callbacks(self):
        handlers=""
        for x in self._store:
            handler=x.handler()
            signal=x.signal()
            if signal=="delete_event":
                handlers +="\n\tdef %s(widget, arg0)\n\t\t\tGtk.main_quit()\n\n\tend\n"%handler # widget, object
                continue #dobuled if not.
            handlers +="""\n\tdef %s(widget)\n\t\tputs "Not implemented yet"\n\tend\n"""%handler #widget, event
        handlers +="\n\tend"
        return handlers

    def commonfooter(self):
        footer="""# Main program
if __FILE__ == $0
  # Set values as your own application.
  PROG_PATH = "%s"
  PROG_NAME = "%s"
  %s.new(PROG_PATH, nil, PROG_NAME)
  Gtk.main
end"""%(self._filename, self._outclass, self._outclass)
        return footer

    def test(self):
        return "\n"

class PerlPlugin(Plugin):

    def __init__(self, filename, widgets, store, testable, outclass="MainWindow"):
        raise NotImplementedError

#for static languages use widgets info to keep track of the type.

class JavaPlugin(Plugin):

    def __init__(self, filename, widgetsinfo, store, testable, outclass="MainWindow"):
        super(JavaPlugin, self).__init__(filename,widgetsinfo, store, outclass, testable)

    def header_and_imports(self):
        header="""


        """
        return header

    def cody_body(self):
        cbody="""
final XML wTree;
final Window %s;

        """

        return cbody

    def callbacks(self):
        pass

    def test(self):
        pass

    def commonfooter(self):
        pass



class CodeGenerator(object):

    def __init__(self, gladefile="tst.glade", plugin="python"):
        self._gladefile=gladefile
        self._gh=GladeContentHandler()
        self._parser=make_parser()

        self._parser.setDTDHandler(0)
        self._parser.setContentHandler(self._gh)

        #--glade2py
        self._parser.setFeature(sax.handler.feature_validation,0)
        self._parser.setFeature(sax.handler.feature_external_ges,0)
        self._parser.setFeature(sax.handler.feature_external_pes,0)
        #--
        self._parser.parse(open(self._gladefile))

        #for w in self._gh.fullwidgetsinfo():
        #    print w

        self._plugin=plugin.lower()

        gladefile=lambda self:self._gladefile
        plugin=lambda self: self._plugin


    def generate(self):
        p=None
        if self._plugin=="python":
            p=PythonPlugin(self._gladefile, self._gh.fullwidgetsinfo(), self._gh.store(), False)
            return p.generate_code()
        elif self._plugin=="ruby":
            p=RubyPlugin(self._gladefile, self._gh.fullwidgetsinfo(), self._gh.store(), False)
            return p.generate_code()
        else:
            raise NotImplemented, plugin



#obsolete.
def usage():
    return """gladizer <gladefile> <to>
gladefile => a valid .glade file.
to        => [python, ruby, perl]
"""


def main():
    optsparser=OptionParser()
    optsparser.add_option("-f", "--file", dest="filename", help="Valid glade file.")
    optsparser.add_option("-p", "--plugin", dest="plugin", help="Language plugin (Python, Ruby, Perl)")
    options, args=optsparser.parse_args() #defaulted to sys.argv[1:]
    gladefile=optsparser.values.filename
    plugin=optsparser.values.plugin

    cg=CodeGenerator(gladefile, plugin)

    print cg.generate()



if __name__=="__main__":
    main()
