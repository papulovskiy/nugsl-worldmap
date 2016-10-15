'''
    Make a module of me
'''

import re,sys,os.path
from cPickle import Pickler, Unpickler
from nugsl.tagtool import tagFix
import math

class worldBase:

    def __init__(self):

        self.greenwich = 1269.7627342
        self.offset = 0.0

        self.r_id = re.compile('.*id="([^"]+)".*', re.S|re.M)
        self.r_pin = re.compile('<path.*class="pinpoint.*/>', re.M|re.S)
        r_coord = '([-0-9]+(?:\.[0-9]+)*)'
        r_coords = r_coord + ',' + r_coord
        self.r_coords = re.compile( r_coords, re.M|re.S )
        
        r_coords_nohandles = '(?:M +%s|C +%s +%s)' % (r_coords, r_coords, r_coords)
        self.r_coords_nohandles = re.compile( r_coords_nohandles, re.M|re.S )
        
        self.r_coords_ex = re.compile('.*[^-0-9.]' + r_coords + '.*', re.M|re.S )
        self.r_coords_no_trans = '()' + r_coords
        self.r_ocean = re.compile('.*<path[^>]+class="ocean"[^>]*\sd="([^"]+).*',re.M|re.S)
        r_group_head = '(<g[^a-z0-9])([^>]*)transform="translate\(' + r_coords + '\)"\s+'
        self.r_group_head = re.compile(r_group_head, re.M|re.S)
        self.r_gtrans = re.compile(r_group_head + '(.*)(</g>)',re.M|re.S)
        self.r_ptrans = re.compile('(<path[^a-z0-9])([^>]*)transform="translate\(' + r_coords + '\)"\s+(.*)(/>)',re.M|re.S)

        
    def load(self):
        
        self.init_styles( self.filedata )
        
        # Begone, Jiggery Pokery!  Off with ye!
        self.filedata = self.apply_translations( self.filedata )
            
        self.get_extremes()

        self.find_centerpos()
        self.find_maxhalfwidth()

        self.find_leftmost()
        self.delete_cruft( 'left' )
        self.build_conv_left()
        
        self.find_rightmost()
        self.delete_cruft( 'right' )
        self.build_conv_right()
        
        if self.idata:
            if os.path.exists(self.idata):
                print "Robinson projection data exists for this input file."
                if not self.flatness( self.filedata ):
                    self.idata = None
                    print "  Input image appears to be curved, calculating curve from image."
                else:
                    print "  Input image appears to be flat, using external data file."
                    self.unpickle_values()
            else:
                self.idata = None

    def get_max_pin_radius(self):
        maxpinwidth = 0
        for width in [x['pinwidth'] for x in self.pins]:
            if width > maxpinwidth:
                maxpinwidth = width
        radius =  maxpinwidth / 2
        return radius
    
    def get_pin_data(self, txt):
        r = re.match('(?m)(?s).*id="([^"]*)".*', txt)
        name = r.group(1).split('_')[0]
        try:
            pinpos = [x['name'] for x in self.pins].index( name )
        except:
            pinpos = -1
        if pinpos > -1:
            return self.pins[pinpos]
        else:
            return None

    def flatness(self, data):
        self.isflat = True
        fixer = tagFix()
        fixer.tagfix('path', data,
                     regex='(?m)(?s).*id="ocean".*',
                     matchfunc=self.flatness_check1)
        return self.isflat
    
    def flatness_check1(self, txt):
        re.sub( self.r_coords, self.flatness_check2, txt )
        return ''

    def flatness_check2(self, matchobj):
        x = float( matchobj.group(1) )
        y = float( matchobj.group(2) )
        if y > self.maxy - 0.01:
            return ''
        if y < self.miny + 0.01:
            return ''
        if x > self.centerpos and x < self.maxx - 10:
                self.isflat = False
            
    def pickle_values(self):
        if not os.path.exists( self.odata ):
            po = Pickler( open( self.odata, 'w+' ) )
            po.dump( self.centerpos )
            po.dump( self.maxhalfwidth )
            po.dump( self.leftmost )
            po.dump( self.rightmost )
            po.dump( self.conv_left )
            po.dump( self.conv_right )
            po.dump( self.middleypos )
            po.dump( self.radius )
            po.dump( self.miny )
            po.dump( self.maxy )
            po.dump( self.extend )

    def unpickle_values(self):
        pi = Unpickler( open( self.idata ) )
        self.centerpos = pi.load()
        self.maxhalfwidth = pi.load()
        self.leftmost = pi.load()
        self.rightmost = pi.load()
        self.conv_left = pi.load()
        self.conv_right = pi.load()
        self.middleypos = pi.load()
        self.radius = pi.load()
        self.miny = pi.load()
        self.maxy = pi.load()
        self.extend = pi.load()

    def apply_translations(self, data ):
        '''
            Internal function.
        
            For all groups containing a translation transform attribute,
            invoke tagfix to apply the translation values to all 
            coordinates within the scope of the group.
        '''
        fixer = tagFix()
        data = fixer.tagfix( 'path',
                            data,
                            matchfunc=self.perform_translation, 
                            regex=self.r_ptrans )
        return fixer.tagfix( 'g',
                            data, 
                            matchfunc=self.perform_translation, 
                            regex=self.r_group_head )

    def perform_translation(self, txt):
        '''
            Internal function.
            
            For an individual group known to contain a translation
            transform attribute, refactor its content using the
            group_parts function.
        '''
        if txt[1] == 'g':
            ret = re.sub( self.r_gtrans, self.group_parts, txt )
        else:
            ret = re.sub( self.r_ptrans, self.group_parts, txt)
        return ret

    def group_parts(self, groupobj):
        '''
            Internal function.
            
            Extract the translation values and start, middle
            and end portions from a group match object.  For
            the middle portion of the match, apply the
            translation values to all coordinate pairs it
            contains.  The translation transform attribute
            is omitted from the returned string.
        '''
        start = groupobj.group(1)
        middle1 = groupobj.group(2)
        self.x_trans = float( groupobj.group(3) )
        self.y_trans = float( groupobj.group(4) )
        middle2 = groupobj.group(5)
        end = groupobj.group(6)
        middle1 = re.sub( self.r_coords_no_trans, self.translate, middle1)
        middle2 = re.sub( self.r_coords_no_trans, self.translate, middle2)
        return start + middle1 + middle2 + end
    
    def translate(self, coordobj):
        '''
            Internal function.
            
            Apply a set of translation values to a coordinate pair.
        '''
        x = float( coordobj.group(2) )
        y = float( coordobj.group(3) )
        x = x + self.x_trans
        y = y + self.y_trans
        return '%0.4f,%0.4f' % (x,y)

    def get_coordinates(self, data):
        '''
            Internal function.
            
            Extract a list of coordinate tuples from arbitrary
            file data.
        '''
        data = re.findall(self.r_coords, data)
        for pos in range(len(data)-1,-1,-1):
            data[pos] = (float(data[pos][0]), float(data[pos][1]))
        return data

    def get_extremes(self):
        '''
            Internal function.
            
            Extract the coordinate values from the ocean object,
            and identify its maximum and minimum values for X and Y.
        '''
        r = re.match(self.r_ocean, self.filedata)
        if r:
            endpoints = r.group(1)
        else:
            print 'Oops, unable to find the ocean.  Giving up.'
            sys.exit()
        
        self.endpoints = self.get_coordinates(endpoints)
        self.endpoints.sort( self.sortfunc )
        array = {}
        maxy = None
        maxx = None
        miny = None
        minx = None
        for item in self.endpoints:
            if maxy == None:
                maxy = item[1]
            if maxx == None:
                maxx = item[1]
            if minx == None:
                minx = item[1]
            if miny == None:
                miny = item[1]
            if item[1] < miny:
                miny = item[1]
            if item[1] > maxy:
                maxy = item[1]
                
            if item[0] < minx:
                minx = item[0]
            if item[0] > maxx:
                maxx = item[0]
        self.maxy = maxy
        self.maxx = maxx
        self.miny = miny
        self.minx = minx
        
        self.radius = ( self.maxy - self.miny ) / 2
        self.middleypos = self.radius + self.miny
        
    def sortfunc(self,a,b):
        '''
            Internal function.
            
            Spaceship function used to sort a list of
            x-y tuples by their value in y.
        '''
        if a[1] > b[1]:
            return -1
        elif a[1] == b[1]:
            return 0
        else:
            return 1

    def find_centerpos(self):
        '''
            Internal function.
            
            Identify the center of the ocean on the horizontal
            axis.
        '''
        self.centerpos = (self.maxx - self.minx)/2 + self.minx

    def find_maxhalfwidth(self):
        '''
            Internal function.
            
            Set the width from the center of the ocean to
            either extreme, for internal reference.
        '''
        self.maxhalfwidth = (self.maxx - self.minx)/2

    def find_leftmost(self):
        '''
            Internal function.
            
            Make a list of all left-side coordinates
            in the ocean arc.
        '''
        self.leftmost = self.endpoints[:]
        for pos in range(len( self.leftmost )-1,-1,-1):
            if self.leftmost[pos][0] > self.centerpos:
                self.leftmost.pop(pos)
    
    def find_rightmost(self):
        '''
            Internal function.
            
            Make a list of all right-side coordinates
            in the ocean arc.
        '''
        self.rightmost = self.endpoints[:]
        for pos in range(len( self.rightmost )-1,-1,-1):
            if self.rightmost[pos][0] < self.centerpos:
                self.rightmost.pop(pos)
    
    def delete_cruft(self, hemisphere):
        '''
            Internal function.
            
            The ocean arc is a flat line at the top and
            the bottom.  This function deletes all but the
            outer extreme value pairs, for the left- and
            the right-side arc coordinate sets.            
        '''
        exec 'arc = self.%smost[:]' %hemisphere
        array = {}
        for t in arc:
            if not array.has_key( t[1] ):
                array[ t[1] ] = t[0]
            elif hemisphere == 'right' and t[0] > array[ t[1] ]:
                array[ t[1] ] = t[0]
            elif t[0] < array[ t[1] ]:
                array[ t[1] ] = t[0]
        arc = []
        keys = array.keys()
        keys.sort()
        keys.reverse()
        for key in keys:
            arc.append( (array[key], key) )
        exec 'self.%smost = arc' %hemisphere

    def build_conv_left(self):
        '''
            Internal function.
            
            For each value in the leftside arc, calculate
            the multiplier needed to move it to the maximum
            width position.  Save this and the Y value to
            which it applies to a left-side conversion
            list.
        '''
        
        self.conv_left = []
        for d in self.leftmost:
            cur_length = self.centerpos - d[0]
            factor = self.maxhalfwidth / cur_length
            self.conv_left.append( (d[1], factor) )
        
    def build_conv_right(self):
        '''
            Internal function.
            
            For each value in the rightside arc, calculate
            the multiplier needed to move it to the maximum
            width position.  Save this and the Y value to
            which it applies to a right-side conversion
            list.
        '''
        
        self.conv_right = []
        for d in self.rightmost:
            cur_length = d[0] - self.centerpos
            factor = self.maxhalfwidth / cur_length
            self.conv_right.append( (d[1], factor) )

    def convert_values(self,x,y,flag='expand'):
        '''
            Internal function.
            
            This is where we bring all the groundwork together.
            Take X and Y values as arguments, and step through 
            the appropriate list of conversion tuples to identify 
            the range within which the given Y value falls.  Interpolate
            the conversion factor, apply it to the given X value, and
            return the converted tuple.
        '''
        if x < self.centerpos:
            factor = None
            for pos in range(len(self.conv_left)-1, -1, -1):
                if y - 0.00006 < self.conv_left[pos][0] < y + 0.00006:
                    factor = self.conv_left[pos][1]
                    break
                elif y + 0.00006 < self.conv_left[pos][0]:
                    y1 = self.conv_left[pos][0]
                    try:
                        y2 = self.conv_left[pos+1][0]
                    except:
                        print 'Ran out of choices in WorldBase.py'
                        print 'y: %f' %y
                        print 'conv_left: %f' % self.conv_left[pos][0]
                    c1 = self.conv_left[pos][1]
                    c2 = self.conv_left[pos+1][1]

                    m = (y1-y2)/(c1-c2)
                    factor = ((y-y2)/m) + c2
                    break
        elif x > self.centerpos:
            factor = None
            for pos in range(len(self.conv_right)-1, -1, -1):
                if y - 0.00006 < self.conv_right[pos][0] < y + 0.00006:
                    factor = self.conv_right[pos][1]
                    break
                elif y + 0.00006 < self.conv_right[pos][0]:
                    y1 = self.conv_right[pos][0]
                    try:
                        y2 = self.conv_right[pos+1][0]
                    except:
                        print 'Ran out of choices in WorldBase.py'
                        print 'y: %f' %y
                        print 'conv_right: %f' % self.conv_right[pos][0]
                    c1 = self.conv_right[pos][1]
                    c2 = self.conv_right[pos+1][1]
                    m = (y1-y2)/(c1-c2)
                    factor = ((y-y2)/m) + c2
                    break
        if factor == None:
            print 'Failure in WorldBase.py'
            print '         x: %f' %x
            print ' centerpos: %f' %self.centerpos
            print ' table min: %f' %self.conv_left[-1][0]
            print ' table max: %f' %self.conv_left[0][0]
            print '         y: %f' %y
            print 'table max expanded: %f ' %self.conv_left[0][0]
            sys.exit()
        if flag == 'shrink':
            x = self.shrink_x( x, factor )
        if flag == 'expand':
            x = self.expand_x( x, factor )
        return (x,y)
    
    def expand_x(self, x, factor ):
        x = ( (x - self.centerpos) * factor ) + self.centerpos
        return x

    def shrink_x(self, x, factor ):
        x = ( (x - self.centerpos) / factor ) + self.centerpos
        return x


    def get_country_title(self, country_code):
        for country in self.countrydata:
            if country['code'] == country_code:
                return country['title']
        return None
