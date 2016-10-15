'''
    Module
'''

import re
from nugsl.tagtool import tagFix

class imageMap:
    '''
        Generate image maps for countries or pinpoints.
    '''

    def write_imagemap(self, data, flat_output=False ):
        if self.render_width:
            self.imagemap_countries( data )
            self.imagemap_pinpoints( data )
            self.imagemap_translate( flat_output=flat_output )
            self.imagemap_get_map()

    ## Command to extract the imagemap as a string
    def imagemap_get_map(self):
        anchors = ''
        for anchor in self.imagemap_anchor_buffer:
            coords = []
            for coordpair in anchor[1]:
                coords.append( '%d' %coordpair[0] )
                coords.append( '%d' %coordpair[1] )
            anchors += self.imagemap_anchor( anchor[0], coords )
        for pinanchor in self.imagemap_pinanchor_buffer:
            anchors += self.imagemap_pinanchor( pinanchor )
        self.imagemap = self.imagemap_imagemap( anchors )
            
    ## Command to gather data on known countries
    def imagemap_countries(self, data):
        self.imagemap_anchor_buffer = []
        if self.suppress_country_imagemap:
            return
        for country in self.countrydata:
            if country['url']:
                self.imagemap_country( data, country )

    ## Command to gather data on known pinpoints
    def imagemap_pinpoints(self, data):
        self.imagemap_pinanchor_buffer = []
        if self.suppress_pinpoint_imagemap:
            return
        for pinpoint in self.pins:
            if pinpoint['url']:
                self.imagemap_pinpoint( data, pinpoint )

    ## Templates
    def imagemap_imagemap(self, anchors):
        ret = "<map name='nugslmap'>\n<p>@@anchors@@\n</map>"
        ret = ret.replace('@@anchors@@', anchors)
        return ret

    def imagemap_anchor(self, url, coords):
        ret = "<a href='@@url@@' shape='poly' coords='@@coords@@'></a>\n"
        ret = ret.replace('@@url@@', url)
        coords = ','.join(coords)
        ret = ret.replace('@@coords@@', coords)
        return ret
    
    def imagemap_pinanchor(self, pinanchor):
        ret = "<a href='@@url@@' shape='circle' coords='@@coords@@'></a>\n"
        coords = ','.join( ['%d'%x for x in  pinanchor[1]] )
        ret = ret.replace('@@url@@', pinanchor[0] )
        return ret.replace('@@coords@@', coords )
        
    ## Internal functions for countries
    def imagemap_country(self, data, country):
        '''
            Store the HTML anchor(s) for the specified country on a string variable.
        '''
        self.imagemap_countrydata = country
        fixer = tagFix()
        fixer.tagfix('g', data, 
                     nonmatchfunc=self.imagemap_contiguous_country,
                     matchfunc=self.imagemap_noncontiguous_country,
                     level=1,
                     regex='(?m)(?s).*id="%s".*' % (country['code'],))

    def imagemap_contiguous_country(self, txt):
        fixer = tagFix()
        fixer.tagfix('path', txt,
                     matchfunc=self.imagemap_process_anchor,
                     regex='(?m)(?s).*id="%s".*' % (self.imagemap_countrydata['code'],))
        return ''

    def imagemap_noncontiguous_country(self, txt):
        fixer = tagFix()
        fixer.tagfix('path', txt,
                     matchfunc=self.imagemap_process_anchor)
        return ''
    
    def imagemap_process_anchor(self, txt):
        self.imagemap_coords = []
        # Validate: if no points are inside the viewport,
        # ignore
        self.imagemap_valid = False
        re.sub(self.r_coords_nohandles, self.imagemap_validate_anchor, txt)
        if not self.imagemap_valid:
            return ''
        # Fetch
        self.imagemap_coordinate_buffer = []
        re.sub(self.r_coords_nohandles, self.imagemap_fetch_anchor_data, txt)
        self.imagemap_anchor_buffer.append( [self.imagemap_countrydata['url'],self.imagemap_coordinate_buffer] )
        #anchor = self.imagemap_anchor()
        #self.imagemap_anchors += anchor
        return ''

    def imagemap_validate_anchor(self, matchobj):
        if matchobj.group(1):
            x = float( matchobj.group(1) )
        else:
            x = float( matchobj.group(5) )
        if self.viewport[0] < x < self.viewport[2]:
            self.imagemap_valid = True
    
    def imagemap_fetch_anchor_data(self, matchobj):
        if matchobj.group(1):
            x = float( matchobj.group(1) )
            y = float( matchobj.group(2) )
        else:
            x = float( matchobj.group(3) )
            y = float( matchobj.group(4) )
        self.imagemap_gather(x, y)
        return ''

    def imagemap_gather(self, x, y):
        # This is invoked on the map when it is flat
        if x < self.viewport[0]:
            x = self.viewport[0]
        if x > self.viewport[2]:
            x = self.viewport[2]
        self.imagemap_coordinate_buffer.append( [x,y] )
        
    def imagemap_translate(self, flat_output=False):
        for apos in range(0,len(self.imagemap_anchor_buffer),1):
            anchor_coords = self.imagemap_anchor_buffer[apos][1]
            for cpos in range(0,len(anchor_coords),1):
                coords = anchor_coords[cpos]
                x,y = self.imagemap_translate_coords( coords[0], coords[1], flat_output=flat_output)
                self.imagemap_anchor_buffer[apos][1][cpos][0] = x
                self.imagemap_anchor_buffer[apos][1][cpos][1] = y
    
    def imagemap_translate_coords(self, x, y, flat_output=False):
        if not flat_output:
            x,y = self.convert_values( x, y, flag='shrink' )
        # Viewport vars do NOT have the same meaning as the values
        # in viewBox!  Viewport is x1,y1,x2,y2.  ViewBox is x1,y1,w,h.
        factor = self.render_width / ( self.viewport[2] - self.viewport[0] )
        x = ( x - self.viewport[0] ) * factor
        y = ( y - self.viewport[1] ) * factor
        return (x, y)

    ## Internal functions for pinpoints
    def imagemap_pinpoint(self, data, pinpoint):
        '''
            Store the HTML anchor(s) for the specified pinpoint on a string variable.
        '''
        self.imagemap_pinpointdata = pinpoint
        fixer = tagFix()
        fixer.tagfix('path', data, 
                     matchfunc=self.imagemap_process_pinpoint,
                     regex='(?m)(?s).*id="%s[_"].*' % (pinpoint['name'],))

    def imagemap_process_pinpoint(self, txt):
        r = re.match('(?m)(?s).*M([^,]*),([-.0-9]*).*A *([-.0-9]*).*', txt)
        x = float( r.group(1) )
        y = float( r.group(2) )
        # Omit pinpoints that are outside the viewport
        if self.viewport[0] > x > self.viewport[2]:
            return ''
        # If exporting a country image, omit points that are not associated with it
        if self.country:
            if not self.imagemap_pinpointdata['country'] == self.country:
                return ''
        radius = float( r.group(3) )
        x = x + radius
        factor = self.render_width / ( self.viewport[2] - self.viewport[0] )
        x = ( x - self.viewport[0] ) * factor
        y = ( y - self.viewport[1] ) * factor
        radius = radius * factor
        
        self.imagemap_pinanchor_buffer.append( [self.imagemap_pinpointdata['url'], [x,y,radius]] )
        return ''
    