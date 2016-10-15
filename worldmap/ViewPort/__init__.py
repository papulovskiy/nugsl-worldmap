'''
    Module
'''

import re
from nugsl.tagtool import tagFix

class viewPort:
    '''
        Adjust the viewport of the current document incarnation.
        
        This should be a simple point-and-shoot thing that just
        always works, so we can forget about this irritating problem.
        Should check for the presence of an ocean object.  If found,
        set the viewport from it.  If no ocean object is found,
        set the viewport from all path objects contained in the file.
    '''

    def viewport_set(self, data):
        if not self.render_width and not self.render_height:
            return data
        r = re.match('(?m)(?s).*<path[^>]*id="ocean".*', data)
        if r:
            self.viewport_invert = False
            self.viewport_regex = '(?m)(?s).*id="ocean".*'
        else:
            self.viewport_invert = True
            self.viewport_regex = '(?m)(?s).*class="pinpoint.*'
        fixer = tagFix()
        return self.viewport_from_paths( data )
        
    def viewport_from_paths(self, data):
        self.viewport = [10000,10000,-10000,-10000]
        fixer = tagFix()
        fixer.tagfix('path', data, matchfunc=self.get_viewport, invert=self.viewport_invert, regex=self.viewport_regex)
        self.viewport[0] += -1
        self.viewport[1] += -1
        maxpinradius = self.get_max_pin_radius()
        self.viewport[0] += - maxpinradius
        self.viewport[1] += - maxpinradius
        self.viewport[2] += maxpinradius
        self.viewport[3] += maxpinradius
        self.viewport_width = self.viewport[2] - self.viewport[0]
        self.viewport_height = self.viewport[3] - self.viewport[1]
        
        # Adjust output dimensions, for reference when rendering bitmaps
        if not self.render_height:
            self.render_height = self.get_render_height()
        elif not self.render_width:
            self.render_width = self.get_render_width()
        if self.render_height > self.get_render_height:
            self.render_height = self.get_render_height()
        elif self.render_width > self.get_render_width():
            self.render_width = self.get_render_width()
        return self.adjust_viewport( data )
    
    def get_render_width(self):
        return self.render_height * self.viewport_width / self.viewport_height
    
    def get_render_height(self):
        return self.render_width * self.viewport_height / self.viewport_width

    def adjust_viewport(self, data):
        viewbox = 'viewBox="%f %f %f %f"' % (self.viewport[0], self.viewport[1], self.viewport_width, self.viewport_height)
        width = 'width="%f"' % (self.viewport_width,)
        height = 'height="%f"' % (self.viewport_height,)
        data = re.sub('(?m)(?s)viewBox="[^"]*"', viewbox, data)
        data = re.sub('(?m)(?s)height="[^"]*"', height, data)
        data = re.sub('(?m)(?s)width="[^"]*"', width, data)
        return data
        
    def get_viewport(self, txt):
        re.sub(self.r_coords, self.get_viewport_coords, txt)
        return txt
        
    def get_viewport_coords(self, matchobj):
        x = float( matchobj.group(1) )
        y = float( matchobj.group(2) )
        if x < self.viewport[0]:
            self.viewport[0] = x
        if y < self.viewport[1]:
            self.viewport[1] = y
        if x > self.viewport[2]:
            self.viewport[2] = x
        if y > self.viewport[3]:
            self.viewport[3] = y

