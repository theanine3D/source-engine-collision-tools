# Source Engine Collision Tools
Blender (3.0+) addon for generating and optimizing collision models for use in Source Engine games (ie. TF2, GMod, L4D2). Works best when combined with the [Blender Source Tools](http://steamreview.org/BlenderSourceTools/).

## Features
All features are customizeable and can be tweaked via optional settings. There is also a "Recommended Settings" button that will automatically guess the best settings for you based on the currently selected, active object.
- **Generate Collision Mesh** - Generate a Source Engine-compliant collision model based on the current active object.
  - Supports (optional) decimation, to automatically reduce the complexity of the resulting collision model
- **Split Up Collision Mesh** - Splits up a selected collision model into multiple separate objects, with every part having no more than 32 hulls.
- **Merge Adjacent Similars** - Merges convex hulls with similar adjacent hulls aggressively, lowering the final amount of hulls & producing a (potentially) less accurate, but more performant model.
- **Remove Thin Faces** - Removes any polygons that are significantly smaller than the average face area in the model.
- **Generate Source Engine QC** - Automatically generate QC files for one or more collision model(s), allowing you to quickly compile them with batch compile tools out there (ie. [Crowbar](https://developer.valvesoftware.com/wiki/Crowbar))
- **Force Convex** - Forces all existing hulls in a collision model to be convex. 

## Installation
1. For the newest, bleeding edge version, download [source_engine_collision_tools.py](https://github.com/theanine3D/source-engine-collision-tools/raw/main/source_engine_collision_tools.py) (right click this link and Save As...) If you want a more stable release, check the [Releases](https://github.com/theanine3D/source-engine-collision-tools/releases).
2. Go into Blender's addon preferences (File → Preferences → Addons)
3. Click the "Install..." button and browse to source_engine_collision_tools.py, select it, and press "Install Add-on"

(Note: The .PY file is installed directly, without a ZIP file)

## Tips
- Decimation (by the Generate Collision Mesh operator) generally makes the Merge Adjacent Similars operator less effective, but Decimation is generally much faster at reducing the final complexity of the collision mesh.
- Merge Adjacent Similars is less effective on overly large, complex models. For best results, split up a large complex model into separate pieces first, and then use Merge Adjacent Similars on each individual piece.
- If you don't get good results after running one of the operators, try increasing the Scale Modifier and Distance Modifier settings. Larger models can require higher or lower values for those settings.

## Previews ##
### Interface ###
![image](https://user-images.githubusercontent.com/88953117/213289952-681acd91-0bd2-4684-96c6-c51c4eaa15bd.png)
### Automatic Collision Generation
![collision-gen-1](https://user-images.githubusercontent.com/88953117/212523161-07296101-d80f-4d7e-8cbe-5ccbc93425ba.gif)
### Merge Adjacent Similars ###
![merge-similars](https://user-images.githubusercontent.com/88953117/213289714-d13d5bb8-ef37-439e-8eac-1370b4716bab.gif)
### Remove Thin Faces
![remove-thin-faces](https://user-images.githubusercontent.com/88953117/212523166-9b911cbc-649d-43b5-918b-ecd9aa41acd9.gif)
