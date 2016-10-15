'''
    Module
'''

import unittest
import os
from worldmap import worldBase

class TestTranslation(unittest.TestCase):

    def setUp(self):
        self.wb = worldBase()
        self.wb.filedata = '''
<path id="ocean" class="ocean" d="0,0 0,100 100,0 100,100" />
<g transform="translate(1,1)" id="jp">
  <path transform="translate(2,2)" d="0,0" />
</g>
'''

    def testTranslation(self):
        res = self.wb.apply_translations( self.wb.filedata )
        expected = '''
<path id="ocean" class="ocean" d="0,0 0,100 100,0 100,100" />
<g id="jp">
  <path d="3.0000,3.0000" />
</g>
'''
        self.assertEqual(res,expected)
        
    
        
if __name__ == "__main__":
    unittest.main()
