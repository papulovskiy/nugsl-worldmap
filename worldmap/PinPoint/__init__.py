'''
    Module
'''

pin_template = '''
  <path
     class="pinpoint @@class@@"
     id="@@name@@"
     d="M @@leftedge@@,@@y@@ 
        A @@radius@@ @@radius@@ 0 1 1 @@rightedge@@,@@y@@ 
        A @@radius@@ @@radius@@ 0 0 1 @@leftedge@@,@@y@@ 
        z"
     />
'''

class pinPoint:

    def longitude_to_pos(self, longitude):
        pos = self.greenwich + ( longitude * self.maxhalfwidth * 2 / 360 )
        if pos > self.centerpos + self.maxhalfwidth:
            pos = pos - ( self.maxhalfwidth * 2 )
        return pos
        
    def latitude_to_pos(self, latitude):
        return latitude * ( ( self.extend * ( self.maxy - self.miny ) ) / 180 ) + self.middleypos
        
    def get_pins(self, country=None):
        pins = ''
        for pin in self.pins:
            if country and pin['country'] != country:
                continue
            name = pin['name']
            cls = pin['class']
            pinwidth = pin['pinwidth']
            pins += self.define_pin( name, cls, pin['longitude'], pin['latitude'], pinwidth )
        return pins
        
    def define_pin(self, name, cls, longitude, latitude, pinwidth):
        x = self.longitude_to_pos( longitude )
        y = self.latitude_to_pos( latitude )
        if y > self.maxy:
            y = self.maxy
            x = self.centerpos
        if y < self.miny:
            y = self.miny
            x = self.centerpos
        if self.rendered_pinwidth:
            pinwidth = self.clobber_pinwidth()
        leftedge = x - (pinwidth/2)
        rightedge = x + (pinwidth/2)
        radius = pinwidth/2
        pin = pin_template.replace('@@x@@', '%0.4f' %x)
        pin = pin.replace('@@y@@', '%0.4f' %y)
        pin = pin.replace('@@leftedge@@', '%0.4f' %leftedge)
        pin = pin.replace('@@rightedge@@', '%0.4f' %rightedge)
        pin = pin.replace('@@name@@', name)
        pin = pin.replace('@@class@@', cls)
        pin = pin.replace('@@radius@@', '%0.4f' %radius)
        return pin

    def clobber_pinwidth(self):
        svg_width = self.viewport[2] - self.viewport[0]
        # Get the ratio of the requested pinwidth in
        # pixels to the pixel width of the output image
        factor = self.rendered_pinwidth / self.render_width
        # Get the pinwidth in SVG units that has the
        # same ratio to the SVG width of the image
        return svg_width * factor
        