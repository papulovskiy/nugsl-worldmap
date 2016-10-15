'''
    Module
'''

import sys, re, os
from ConfigParser import ConfigParser

class pinConfig(ConfigParser):
    
    def __init__(self, pin_file, pin_string, default_pin_width, super_pinwidth_default ):

        ConfigParser.__init__(self, defaults={'url': '', 'default_pinwidth': default_pin_width, 'country': 'none'})
        
        self.super_pinwidth_default = super_pinwidth_default
        
        self.pin_file_data = []
        self.pin_string_data = []
        
        for file in pin_file:
            if not os.path.exists( file ):
                print 'Error: unable to find pin file %s' %file
                sys.exit()
        
        self.read( pin_file )
        self.pin_string = pin_string
        
        self.parse_file()
        self.parse_string()

    def parse_file(self):

        for section in self.sections():
            m = {}
            for option in ['latitude','longitude']:
                if not self.has_option(section,option):
                    print 'Missing %s for %s, aborting.' % (option,section)
                    sys.exit()
            m['title'] = section
            m['url'] = self.get(section,'url')
            m['name'] = section.lower().replace(' ','-')
            m['name'] = re.sub('[^-a-z0-9]','', m['name'])
            m['country'] = self.get(section, 'country')
            latitude = self.get(section,'latitude')
            m['latitude'] = self.latitude_to_float( latitude )
            longitude = self.get(section,'longitude')
            m['longitude'] = self.longitude_to_float( longitude )
            dpw = self.get('DEFAULT','default_pinwidth').strip()
            if dpw.endswith('%'):
                dpw = self.super_pinwidth_default * float( dpw[:-1] ) / 100
            else:
                dpw = float( dpw )
            if self.has_option(section,'pinwidth'):
                p = self.get(section,'pinwidth')
                if p.endswith('%'):
                    m['pinwidth'] = dpw * float( p[:-1] ) / 100
                else:
                    m['pinwidth'] = dpw
            else:
                m['pinwidth'] = dpw

            if self.has_option(section,'class'):
                m['class'] = self.get(section,'class')
            else:
                m['class'] = m['name']
            self.pin_file_data.append(m)

    def pins(self):
        return self.pin_file_data + self.pin_string_data
    
    def latitude_to_float(self, s ):
        rx = re.match('^([-0-9]+(?:\.[0-9]+)*)$', s)
        if rx:
            return - float(rx.group(1))
        r = re.match( '([0-9]{1,2})([NSns])([0-9]{0,2})', s )
        if r:
            if r.group(2).upper() == 'N':
                direction = -1
            else:
                direction = 1
            latitude = float(r.group(1))
            if r.group(3) == '':
                minutes = 0
            else:
                minutes = float(r.group(3))
            latitude = ( latitude + ( minutes / 60 ) ) * direction
        else:
            latitude = None
        
        if latitude == None or latitude > 90 or latitude < -90:
            print "Error: invalid latitude value '%s'." % s
            sys.exit()
        else:
            return latitude
    
    def longitude_to_float(self, s ):
        rx = re.match('^([-0-9]+(?:\.[0-9]+)*)$', s)
        if rx:
            return float(rx.group(1))
        r = re.match( '([0-9]{1,3})([EWew])([0-9]{0,2})', s )
        if r:
            if r.group(2).upper() == 'W':
                direction = -1
            else:
                direction = 1
            longitude = float(r.group(1))
            if r.group(3) == '':
                minutes = 0
            else:
                minutes = float(r.group(3))

            meridian = ( longitude + ( minutes / 60 ) ) * direction
        else:
            meridian = None
        
        if meridian == None or meridian > 180 or meridian < -180:
            print "Error: invalid longitude value '%s'." % s
            sys.exit()
        else:
            return meridian

    def parse_string(self):
        if not self.pin_string:
            return []
        r1 = re.match('[a-zA-Z]+,.*',self.pin_string)
        if not r1:
            print "Error: A name is required as the first element in the -p option string."
            sys.exit()
        pins = self.pin_string.split(',')
        pin_name = pins[0]
        pins = [ x.split(':') for x in pins[1:] ]
        count = 1
        newpins = []
        for pin in pins:
            if len(pin) != 2:
                print "Error: Syntax error in -p option string, missing coordinate in item."
                print pin
                sys.exit()
            m = {}
            m['title'] = '%s%d' % (pin_name,count)
            m['name'] = '%s%d' % (pin_name,count)
            m['class'] = pin_name
            m['latitude'] = self.latitude_to_float( pin[0] )
            m['longitude'] = self.longitude_to_float( pin[1] )
            newpins.append(m)
            count += 1
        self.pin_string_data = newpins
