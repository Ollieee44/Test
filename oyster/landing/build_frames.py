"""Build frames.html (SELFTAC in 3D style frames) from frames_template.html and data/meshes.json."""
import os
D = os.path.dirname(os.path.abspath(__file__)) + '/'
html = open(D + 'frames_template.html').read().replace('/*MESHES*/', open(D + 'data/meshes.json').read())
open(D + 'frames.html', 'w').write(html)
print('frames.html', len(html) // 1024, 'KB')
