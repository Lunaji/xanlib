# xanlib
[![Run tests](https://github.com/Lunaji/xanlib/actions/workflows/tests.yml/badge.svg)](https://github.com/Lunaji/xanlib/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/xanlib.svg)](https://pypi.org/project/xanlib/)

A Python library to handle the 3D data format XBF of the Xanadu engine, used in the game *Emperor: Battle for Dune*.  
It may be used to load and save all 1521 XBF files from the game.

## Installation
The library can be installed with pip:  
`pip install xanlib`

## Examples
### Console Usage
The following commands entered into a python console will edit the sidebar to move it to the left:
```python
from xanlib import load_xbf, save_xbf
scene = load_xbf('Data/UI0001/SIDEBAR/SIDEBAR1.XBF')
scene['~~0hide#'].transform = tuple(v - 100 if i == 12 else v for i, v in enumerate(scene['~~0hide#'].transform))
save_xbf(scene, 'Output/SIDEBAR1.XBF')
```
Explanation:
1. Import the load and save functions
2. Load the sidebar file
3. Subtract 100 from the x-coordinate of the translation component of the transformation matrix. It is a flat tuple in column-major order, thus need to modify the element at index 12. Because it is a tuple, it has to be entirely replaced.
4. Save to a new file.

Put the new file in a UI/SIDEBAR folder in the game's DATA folder to override the original and view the change in-game.

### blender_import.py
A script that can be run within Blender to import the meshes of a XBF file.
![missile_tank_blender](https://github.com/user-attachments/assets/47bdbe22-556e-4556-bca6-8b0d4c755497)

### extract_animations.py
A script that extracts animation info from the FX Data Header of an xbf file,
provided as a command line argument.  
Currently stand-alone, the code has yet to be integrated into the library.

Example usage:
```bash
python extract_anim_info.py Data/3DDATA0001/Buildings/AT_MGT_H0.xbf
```
will produce:
```
Stationary: 104-133, 0-50, 51-104, 133-163, 163-193
Idle 0: 200-240
Fire 0: 193-275
```

### xbf_viewer.py
A rudimentary vertex animation viewer made with `pygame`. It highlights the normals in these animations.  
(A more functional viewer is [under development](https://github.com/Lunaji/Xanadu-Animation-Viewer))
![pygame_viewer_animation](https://github.com/user-attachments/assets/b20e0c67-2c84-48ac-9d34-cf5c22e3478e)
