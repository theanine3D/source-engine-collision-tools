# Source Engine Collision Tools
Blender (3.0+) addon for generating and optimizing collision models for use in Source Engine games (ie. TF2, GMod, L4D2). Works best when combined with the [Blender Source Tools](http://steamreview.org/BlenderSourceTools/).

## Features
Some features are customizeable and can be tweaked via optional settings. There is also a "Recommended Settings" button that will automatically guess the best settings for you based on the currently selected, active object.
- **Generate Collision Mesh** - Generate a Source Engine-compliant collision model based on the current active object.
  - Supports (optional) decimation, to automatically reduce the complexity of the resulting collision model
- **Split Up Collision Mesh** - Splits up a selected collision model into multiple separate objects, with every part having no more than 32 hulls.
- **Merge Adjacent Similars** - Merges convex hulls with similar adjacent hulls aggressively, lowering the final amount of hulls & producing a (potentially) less accurate, but more performant model. Similarity is based on the face count and volume of the hulls.
- **Remove Thin Hulls** - Removes any convex hulls that are significantly smaller than all other hulls.
- **Force Convex** - Forces all existing hulls in a collision model to be convex. Especially useful when combined with Blender's built-in Decimate modifier on an existing collision mesh, to ensure that any decimated hulls are still convex.
- **Remove Inside Hulls** - Removes any hulls that are completely or almost completely buried inside other hulls.
- **Generate Source Engine QC** - Automatically generate QC files for one or more collision model(s), allowing you to quickly compile them with batch compile tools out there (ie. [Crowbar](https://developer.valvesoftware.com/wiki/Crowbar))
- **Update VMF** - Updates a selected VMF file by automatically adding any partitioned/split-up collision models that haven't already been added to the map. 

## Installation
1. For the newest, bleeding edge version, download [source_engine_collision_tools.py](https://github.com/theanine3D/source-engine-collision-tools/raw/main/source_engine_collision_tools.py) (right click this link and Save As...) If you want a more stable release, check the [Releases](https://github.com/theanine3D/source-engine-collision-tools/releases).
2. Go into Blender's addon preferences (File → Preferences → Addons)
3. Click the "Install..." button and browse to source_engine_collision_tools.py, select it, and press "Install Add-on"

(Note: The .PY file is installed directly, without a ZIP file)

## Tips
- Decimation (by the Generate Collision Mesh operator) generally makes the Merge Adjacent Similars operator less effective, but Decimation is much faster at reducing the final complexity of the collision mesh. However, Decimation will reduce the complexity uniformly across the entire model, whereas Merge Adjacent Similars tries to reduce complexity only where similar hulls are found.
- Merge Adjacent Similars is less effective on overly large, complex models. For best results, split up a large complex model into several (3-5) separate pieces first, and then use Merge Adjacent Similars on each individual piece.
- For the "Update VMF" feature, the very first part of your split-up collision mesh, ending in 'part_000.mdl', must already be in the VMF somewhere (such as in a prop-static). The operator scans the VMF for any part_000, and any that are found are used as a template for all the other parts.
- Source Engine has a limit of 32 hulls per collision mesh. Going beyond 32 hulls can lead to severe lag during gameplay. The "Split Up Collision Mesh" and "Update VMF" features are handy for this. By splitting up your collision mesh into 32-hull parts, you prevent lag, and the Update VMF feature can add numerous (even dozens or hundreds) of parts automatically for you to a VMF file.

## Previews ##
### Interface ###
![image](https://user-images.githubusercontent.com/88953117/216434606-367d0337-cbe9-4691-bc78-509acd481bf3.png)
### Automatic Collision Generation
![collision-gen-1](https://user-images.githubusercontent.com/88953117/212523161-07296101-d80f-4d7e-8cbe-5ccbc93425ba.gif)
### Merge Adjacent Similars ###
![merge-similars](https://user-images.githubusercontent.com/88953117/213289714-d13d5bb8-ef37-439e-8eac-1370b4716bab.gif)
### Remove Thin Hulls
![remove-thin-hulls](https://user-images.githubusercontent.com/88953117/216437113-22036e00-dcbe-4e74-a6c9-388fb96ac173.gif)
### Video
Click the image below to watch a breakdown video of all the features in the addon.

[![YouTube Video](https://i9.ytimg.com/vi/ASLw-FMQUXM/mqdefault.jpg?sqp=CIyLsJ8G-oaymwEmCMACELQB8quKqQMa8AEB-AH-CYAC0AWKAgwIABABGH8gFCh0MA8=&rs=AOn4CLC3wYz58u5FQpi5Uk8HwFpFSSPYWg)](https://www.youtube.com/watch?v=ASLw-FMQUXM)
