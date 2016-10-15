'''
   Module
'''

import os,sys
from ConfigParser import ConfigParser

class countryConfig(ConfigParser):
    
    def __init__(self, country_file):
        ConfigParser.__init__(self, defaults={'url':"",'title':None,'fill':"",'stroke-width':"",'stroke-fill':""})
        
        self.country_data = []
        
        for file in country_file:
            if not os.path.exists( file ):
                print 'Error: unable to find requested data file for %s' %file
                sys.exit()
        
        self.read( country_file )
        self.parse_file()
        
    def parse_file(self):
        for section in self.sections():
            m = {}
            m['title'] = self.get(section,'title')
            m['code'] = section.lower()
            m['url'] = self.get(section,'url')
            m['fill'] = self.get(section,'fill')
            m['stroke-width'] = self.get(section,'stroke-width')
            m['stroke-fill'] = self.get(section,'stroke-fill')
            self.country_data.append( m )
            

    def countrydata(self):
        return self.country_data
    