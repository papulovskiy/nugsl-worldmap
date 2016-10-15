'''
    Module
'''

import sys, os
from WorldBase import worldBase
from Convert import flattenWorld
from Convert import cloneWorld
from Convert import robinsonWorld
from Convert import countryImage
from Config import pinConfig
from Config import countryConfig
from ViewPort import viewPort
from ImageMap import imageMap
from PinPoint import pinPoint
from nugsl.tagtool import tagFix

from HtmlMerge import html_merge
from OutPut import outPut
from StyleSheet import styleSheet

class worldMap(worldBase,flattenWorld,cloneWorld,robinsonWorld, countryImage, viewPort, imageMap, pinPoint, outPut, styleSheet):
    def __init__(self, filename, ofile,
                 suppress_country_imagemap=False,
                 suppress_pinpoint_imagemap=False,
                 meridian=0,
                 render_width=None,
                 render_height=None,
                 rendered_pinwidth=None,
                 render_type='png',
                 cleanup=None,
                 idata=None, odata=None, pins=None, countrydata=None, style_files=None, extend=1, pin_width=5.0 ):


        self.ofile=ofile             
        self.render_width=float( render_width )
        self.render_height=float( render_height )

        self.rendered_pinwidth=rendered_pinwidth
        
        self.render_type = render_type
        self.cleanup=cleanup
        self.style_files=style_files
        self.meridian = meridian
        
        self.suppress_country_imagemap=suppress_country_imagemap
        self.suppress_pinpoint_imagemap=suppress_pinpoint_imagemap

        self.country = None
        
        self.idata = idata
        self.odata = odata
        
        self.filename = filename
        self.filedata = open(filename).read()
        
        self.debug = False
        self.extend=float(extend)
        self.countrydata = countrydata
        self.pins = pins
        self.pin_width = pin_width

        if os.path.basename( sys.argv[0] ) == 'nugsl-worldmap.py':
            print "ERROR: The nugsl-worldmap.py script is obsolete."
            print "  Please delete it from your system and use nugsl-worldmap"
            print "  (with no .py extension) instead."
            sys.exit()
        worldBase.__init__(self)
        self.load()
