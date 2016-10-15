'''
    Module

    Performs output operations and handles layering of multi-styled images.    
'''

import os

class outPut:
    
    def output(self, mode):
        
        if mode == 'orig':
            data = self.original()
        elif mode == 'rotated':
            data = self.robinson()
        elif mode == 'flat':
            print "Saving Robinson projection data file for this output image."
            self.pickle_values()
            data = self.flatten()
        else:
            data = self.isolate_country( mode )
        
        self.output_and_render( self.styles[0], data )
        
        count = 1
        for style in self.styles[1:]:
            self.output_and_render( style, data, count=count )
            count += 1

    def output_and_render(self, style, data, count=None ):
        basename = os.path.splitext( self.ofile )[0]
        if count:
            basename = basename + '-%d' %count

        data = self.insert_style( style, data )
            
        open( basename + '.svg', 'w+' ).write( data )
        if self.render_width:
            self.rsvg_output( basename )
            
        if self.cleanup and self.render_width:
            os.unlink( basename + '.svg' )

    def rsvg_output(self, basename ):
        pngfile = basename + '.png'
        svgfile = basename + '.svg'
        cmd = 'rsvg -w %d %s %s' % (self.render_width, svgfile, pngfile )
        fh = os.popen(cmd)
        fh.close()
        if self.render_type == 'jpg':
            jpgfile = basename + '.jpg'
            cmd = 'pngtopnm -mix -background "#ffffff" | pnmtojpeg --quality=75 --progressive --optimize'
            ifh,ofh,efh = os.popen3(cmd)
            ifh.write( open(pngfile).read() )
            ifh.close()
            open( jpgfile, 'w+').write( ofh.read() )
            os.unlink( pngfile )

