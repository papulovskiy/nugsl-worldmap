'''
    Module
'''

import re,os,sys

style_rex = re.compile("(.*<style[^>]*>)(.*)(</style>.*)",re.M|re.S)

class styleSheet:

    def init_styles(self, data):
        self.styles = []
        if not self.style_files:
            self.styles.append( self.get_style( data ) )
        else:
            for style_file in self.style_files:
                if not os.path.exists( style_file ):
                    print 'ERROR: Unable to find style file %s' %style_file
                    sys.exit()
                self.styles.append( open( style_file ).read() )

    def insert_style(self, style, data):
        ret = re.sub(style_rex, "\\1" + style +"\\3", data)
        return ret


    def get_style(self, data):
        r = re.match(style_rex, data)
        if r:
            return r.group(2)
        else:
            return ''
