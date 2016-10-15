'''
    Module to make a copy of the flattened version of
    the WikiMedia Robinson projection of the world, to
    the left of the existing image, with countries cloned
    individually and contained within the original country
    group, to save fuss and bother when doing colouring
    and whatnot.
'''

import re,sys
from nugsl.tagtool import tagFix

class cloneWorld:
    
    def clone(self, data=None ):
        
        if not data:
            data = self.filedata
        
        offset = '%0.4f' %(self.maxhalfwidth * 2)
        self.clone_offset = offset
        self.initialize_constants()
        self.template = self.template.replace('@@offset@@', offset)
        if not self.idata:
            data = self.flatten( data=data, internal=True )
        data = self.viewport_set( data )
        if self.pins:
            data = re.sub( '</svg>', self.get_pins() + '</svg>', data )
        fixer = tagFix()
        data = fixer.tagfix( 'g', 
                            data, 
                            matchfunc=self.fix_grouped_country, 
                            nonmatchfunc=self.fix_top_path, 
                            level=1 )
        #open('broken_file_before.svg', 'w+').write(data)
        data = self.apply_translations( data )
        #open('broken_file_after.svg', 'w+').write(data)
        return data

    def fix_top_path(self, data):
        fixer = tagFix(debug=True)
        return fixer.tagfix('path', data, matchfunc=self.fix_path)

    def fix_path(self, txt):
        r3 = self.rex3.match( txt )
        my_id = r3.group(1)
        if my_id == 'ocean':
            return txt
        rightobj = re.sub( 'id="([^"]*)"', "id=\"\\1_right\"", txt )
        leftobj = re.sub( 'id="([^"]*)"', "id=\"\\1_left\"", txt )
        leftobj = re.sub( 'transform="[^"]*"', '', leftobj )
        leftobj = re.sub( '<path', '<path transform="translate(-%s,0)"' %self.clone_offset, leftobj )
        return self.template_no_offset % ( my_id, rightobj + '\n' + leftobj )

    def fix_grouped_country(self, txt):
        r3 = self.rex3.match( txt )
        left_id = r3.group(1) + '_left'
        r2 = self.rex2.match( txt )
        try:
            head = r2.group(1)
        except:
            print txt
        body = r2.group(2)
        tail = r2.group(3)
        left_body = re.sub(self.rex1, 'id="\\1_left"', body)
        left_body = self.template % (left_id, left_body)
        return head + body + left_body + tail

    def initialize_constants(self):
        self.rex1 = re.compile('id="([^"]+)"', re.M|re.S)
        self.rex2 = re.compile( '(<g[^>]+>)(.*)(</g>)', re.M|re.S)
        self.rex3 = re.compile( '.*?id="([^"]+)"', re.M|re.S )
        
        self.template = '''
<g
    transform="translate(-@@offset@@,0)"
    id="%s"
>
%s
</g>
'''
        self.template_no_offset = '''
<g
    id="%s"
>
%s
</g>
'''
