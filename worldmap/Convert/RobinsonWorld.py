'''
    Module
'''

import re,sys
from nugsl.tagtool import tagFix

clip_template = '''        
<defs id="clip_defs">
  <clipPath
    clipPathUnits="userSpaceOnUse"
    id="ocean_clip">
@@ocean@@
  </clipPath>
</defs>
'''

clip_link_start = '''
<g
  id="two_planets"
  clip-path="url(#ocean_clip)">
'''

class robinsonWorld:
    
    def robinson(self):
        if self.flatness( self.filedata ) and not self.idata:
            print "Image appears to be flat, and there is no data file.  Aborting conversion."
            sys.exit()
        self.data = self.clone( data=self.filedata )
        self.offset_ocean( self.longitude_offset( self.meridian ) )
        self.data = self.apply_translations( self.data )
        self.data = self.viewport_set( self.data )
        self.write_imagemap( self.data )
        self.data = self.shrink_image( self.data )
        self.clip()
        return self.data

    def original(self):
        self.data = self.filedata
        if self.idata:
            self.data = self.apply_translations( self.data )
            self.data = self.shrink_image( self.data )
        self.isflat = False
        return self.data

    def shrink_image(self, data ):
        data = re.sub( self.r_coords, self.shrink_values, data )
        fixer = tagFix()
        ret = fixer.tagfix('path',data,
                            matchfunc=self.fix_pin,
                            regex=self.r_pin)
        return ret
                            
    def fix_pin(self, txt):
        # Get local max and min vals for X as strings
        # Adjust vals
        # Do replacement
        pin_data = self.get_pin_data( txt )
        self.fix_pin_minx = "100000"
        self.fix_pin_maxx = "-100000"
        re.sub(self.r_coords, self.get_fix_pin_vals, txt)
        pin_center = float(self.fix_pin_maxx) - ( ( float( self.fix_pin_maxx) - float( self.fix_pin_minx ) ) /2 )
        new_pin_minx = str( pin_center - ( pin_data['pinwidth'] / 2 ) )
        new_pin_maxx = str( pin_center + ( pin_data['pinwidth'] / 2 ) )
        txt = re.sub( self.fix_pin_minx, new_pin_minx, txt )
        txt = re.sub( self.fix_pin_maxx, new_pin_maxx, txt )
        return txt
    
    def get_fix_pin_vals(self, matchobj):
        x = matchobj.group(1)
        if float( x ) < float( self.fix_pin_minx ):
            self.fix_pin_minx = x
    
        if float( x ) > float( self.fix_pin_maxx ):
            self.fix_pin_maxx = x
        return ''
    
    def longitude_offset(self, meridian):
        factor = self.maxhalfwidth / 180.0
        if meridian < 0:
            meridian = 360 + meridian
        # Offset to center map on Greenwich
        offset = self.greenwich - self.centerpos
        offset = - ( meridian * factor ) - offset
        if - offset > self.centerpos - self.greenwich:
            offset = offset + ( self.maxhalfwidth * 2 )
        return offset
    
    def offset_ocean(self, offset):
        self.offset = offset
        self.centerpos += -offset
        fixer = tagFix()
        self.data = fixer.tagfix( 'path', 
                                 self.data, 
                                 matchfunc=self.fix_ocean, 
                                 regex='.*id="ocean".*' )

    def fix_ocean(self, txt):
        rex = re.compile('(<path.*?)(?:transform="translate\([^)]*\)")*(.*/>)', re.M|re.S )
        r = rex.match(txt)
        head = r.group(1)
        tail = r.group(2)
        body = '\ntransform="translate(%0.4f,0.0000)"\n' % (-self.offset,)
        return head + body + tail

    def shrink_values(self, matchobj):
        '''
            Internal function.
            
            Replace a single set of coordinates with "rounded"
            values.
        '''
        x = float( matchobj.group(1) )
        y = float( matchobj.group(2) )
        newx,newy = self.convert_values(x,y,flag='shrink')
        return '%0.4f,%0.4f' % (newx,newy)
    
    def clip(self):
        rex2 = '.*(<defs[^>]*/>).*(<path[^>]+id="ocean"[^>]*>).*(</svg>)'
        rex2 = re.compile( rex2, re.M|re.S )
        r2 = rex2.match( self.data )
        # Ocean object
        clip_path = r2.group(2).replace( 'id="ocean"', 'id="ocean_clip_path"' )
        # Index immediately before the defs tag opens
        #print r2.start(1)
        # Index immediately after the end of the defs tag
        #print r2.end(1)
        # Index immediately before the ocean object
        #print r2.start(2)
        # Index immediately before the end of the file
        #print r2.start(3)
        # Prepare the clip path
        clip_thing = clip_template.replace('@@ocean@@', clip_path )
        buffer = ''
        buffer += self.data[:r2.start(1)]
        buffer += clip_thing
        buffer += self.data[r2.end(1):r2.start(2)]
        buffer += clip_link_start
        buffer += self.data[r2.start(2):r2.start(3)]
        buffer += '\n</g>\n'
        buffer += self.data[r2.start(3):]
        self.data = buffer
   
