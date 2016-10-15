#!/usr/bin/env python

from distutils.core import setup

long_description="""

This program can be used to refactor a Robinson projection world map,
offered through the WikiMedia project, in several useful ways.  A
flattened version of the map can be produced, or the map can be
rotated to an arbitrary line of longitude.  Pinpoint marks can be
added at specific coordinates, and the stylesheet of the map can be
rewritten, giving full control over colours and other aspects of
the map's appearance.
""".strip()

data = []
data.append('data/BlankMap-World6.svg')

setup(name='nugsl-worldmap',
      version='1.16',
      description='WikiMedia world map tool',
      author='Frank Bennett',
      author_email='biercenator@gmail.com',
      maintainer='Frank Bennett',
      maintainer_email='biercenator@gmail.com',
      url='http://gsl-nagoya-u.net/',
      packages=['nugsl','nugsl.worldmap', 'nugsl.worldmap.StyleSheet', 'nugsl.worldmap.OutPut', 'nugsl.worldmap.PinPoint', 'nugsl.worldmap.HtmlMerge', 'nugsl.worldmap.ImageMap', 'nugsl.worldmap.ViewPort','nugsl.worldmap.Convert','nugsl.worldmap.Config'],
      provides=['nugsl.worldmap'],
      scripts=['scripts/nugsl-worldmap'],
      requires=['nugsl.tagtool'],
      package_dir={'nugsl':''},
      data_files=[('share/nugsl-worldmap/data',data)],
      long_description=long_description,
      platforms=['any'],
      license='http://www.gnu.org/copyleft/gpl.html'
      )
