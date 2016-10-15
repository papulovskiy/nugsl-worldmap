'''
    Module
'''

import re
from nugsl.tagtool import tagFix

class countryImage:

    def isolate_country(self, country):
        self.country = country
        data = self.flatten( internal=True )
        fixer = tagFix()
        data = fixer.tagfix('g', data, 
                      matchfunc=self.delete_tag,
                      nonmatchfunc=self.isolate_contiguous_country,
                      level=1,
                      invert=True,
                      regex='(?m)(?s).*id="%s".*' % (country,))
        if country == 'us':
            data = self.repair_us_country_view( data )
        data = self.viewport_set( data )
        if self.pins:
            data = re.sub( '</svg>', self.get_pins( country=country ) + '</svg>', data )
        self.write_imagemap( data, flat_output=True )
        return data
    
    def isolate_contiguous_country(self, txt):
        fixer = tagFix()
        txt = fixer.tagfix('path', txt,
                            matchfunc=self.delete_tag,
                            invert=True,
                            regex='(?m)(?s).*(id="%s").*' % (self.country,))
        return txt
    
    def delete_tag(self, txt):
        return ''

    def repair_us_country_view(self, data):
        return re.sub(self.r_coords, self.repair_us_coords, data )

    def repair_us_coords(self, matchobj):
        x = float( matchobj.group(1) )
        y = float( matchobj.group(2) )
        if x > self.centerpos:
            x = x - ( self.maxx - self.minx )
        return '%0.4f,%0.4f' % (x,y)
