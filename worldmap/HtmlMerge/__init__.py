'''
    Module
'''

import os

def html_merge( htmlcode, filename, imagetype, imagemap, title=None ):
    if not title:
        title = 'The World'
    htmlname = os.path.splitext( filename )[0] + '.html'
    graphicname = os.path.splitext( filename)[0] + '.' + imagetype
    htmlcode = htmlcode.replace('@@image-type@@', imagetype)
    htmlcode = htmlcode.replace('@@image-map@@', imagemap )
    htmlcode = htmlcode.replace('@@image-file@@', graphicname )
    htmlcode = htmlcode.replace('@@title@@', title )
    open( htmlname, 'w+').write( htmlcode )
