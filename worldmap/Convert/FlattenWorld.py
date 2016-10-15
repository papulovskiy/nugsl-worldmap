'''
    Module for flattening the WikiMedia Robinson projection
    of the world.
'''

import re,sys,os.path
import math

from nugsl.tagtool import tagFix
from nugsl.worldmap import worldBase

class flattenWorld(worldBase):

    def flatten(self, data=None, internal=False):
        '''
            Convert image to a cylindrical projection and return
            the converted data.
        '''
        
        if not data:
            data = self.filedata
        

        if not self.idata:
            data = re.sub( self.r_coords, self.expand_values, data )
            fixer = tagFix()
            data = fixer.tagfix('p',
                               data,
                               matchfunc=self.fix_pin,
                               regex=self.r_pin)
        else:
            print "  Skipping flatten step as unnecessary."

        if not internal:
            data = self.viewport_set( data )
            if self.pins:
                data = re.sub( '</svg>', self.get_pins() + '</svg>', data )
            self.write_imagemap( data, flat_output=True )
        return data

    def expand_values(self, matchobj):
        '''
            Internal function.
            
            Replace a single set of coordinates with "flattened"
            values.
        '''
        x = float( matchobj.group(1) )
        y = float( matchobj.group(2) )
        newx,newy = self.convert_values(x,y,flag='expand')
        return '%0.4f,%0.4f' % (newx,newy)

