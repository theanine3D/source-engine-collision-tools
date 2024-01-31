# Source Engine Collision Tools
Blender (3.x+ / 4.x+) addon for generating and optimizing collision models for use in Source Engine games (ie. TF2, GMod, L4D2). Works best when combined with the [Blender Source Tools](http://steamreview.org/BlenderSourceTools/).

Finding this addon useful? Please consider starring it ⭐, or donating 🙂<br>
[![image](https://user-images.githubusercontent.com/88953117/232652206-a5b7c5a1-d4cc-40ec-88d7-d3a5886d8f55.png)](https://www.paypal.com/donate/?hosted_button_id=K63REE7KJ3WUY)

## Features
Some features are customizeable and can be tweaked via optional settings. There is also a "Recommended Settings" button that will automatically guess the best settings for you based on the currently selected, active object.
- **Generate Collision Mesh** - Generate a Source Engine-compliant collision model based on the current active object.
  - Supports (optional) decimation, to automatically reduce the complexity of the resulting collision model
- **Generate Fractured Collision** - This operator uses the Cell Fracture addon built into Blender to generate more accurate and performant collision meshes for Source Engine. However, unlike the above operator, it is intended to be used on individual props, not entire scenes at once. Works best on fully sealed objects with no holes or non-manifold geometry.
  - Automatically creates a gap between collision hulls to prevent overlapping. The size of the gap is determined by the "Gap Width" setting
  - Attempts to generate only the amount of hulls specified by the "Fracture Target" setting. ie. A "Fracture Target" of 4 will try to split up the model into only 4 parts.
  - Note that the Cell Fracture addon needs to be enabled in your Blender preferences first!
  - _**NOTE**: This specific feature is currently broken in Blender 4.x due to a [bug](https://projects.blender.org/blender/blender-addons/issues/105012#issuecomment-1070774) in the Cell Fracture addon_

- **Split Up Collision Mesh** - Splits up a selected collision model into multiple separate objects, with every part having no more than 32 hulls.
- **Merge Adjacent Similars** - Merges convex hulls with similar adjacent hulls aggressively, lowering the final amount of hulls & producing a (potentially) less accurate, but more performant model. Similarity is based on the face count and volume of the hulls.
- **Remove Thin Hulls** - Removes any convex hulls that are significantly smaller than all other hulls.
- **Force Convex** - Forces all existing hulls in a collision model to be convex. Especially useful after using Blender's built-in Decimate modifier on an existing collision mesh, to ensure that any decimated hulls are still convex.
- **Remove Inside Hulls** - Removes any hulls that are completely or almost completely buried inside other hulls.
- **Generate Source Engine QC** - Automatically generate QC files for one or more collision model(s), allowing you to quickly compile them with batch compile tools out there (ie. [Crowbar](https://developer.valvesoftware.com/wiki/Crowbar))
- **Update VMF** - Updates a selected VMF file by automatically adding any partitioned/split-up collision models that haven't already been added to the map.
- **Export Hulls to Hammer .VMF** - Converts hulls in the selected collision mesh into Source Engine brush solids and exports them as a .VMF file that can be opened in Hammer.

## Installation
- For the newest, bleeding edge version, press the big green "Code" button above, and choose "Download ZIP"
- If you want a more stable release, check the [Releases](https://github.com/theanine3D/source-engine-collision-tools/releases).
- After downloading either of the above, go into Blender's addon preferences (File → Preferences → Addons)
4. Click the "Install..." button and browse to the ZIP file you just downloaded, select it, and press "Install Add-on"

## Tips
- The UI for the addon is found in the "Object Properties" tab on the right-hand side of the Blender window. The UI's features are greyed out if you have no object selected, so select an object first in the 3D VIewport.
- Decimation (by the Generate Collision Mesh operator) generally makes the Merge Adjacent Similars operator less effective, but Decimation is much faster at reducing the final complexity of the collision mesh. However, Decimation will reduce the complexity uniformly across the entire model, whereas Merge Adjacent Similars tries to reduce complexity only where similar hulls are found.
- Merge Adjacent Similars is less effective on overly large, complex models. For best results, split up a large complex model into several (3-5) separate pieces first, and then use Merge Adjacent Similars on each individual piece.
- For the "Update VMF" feature, the very first part of your split-up collision mesh, ending in 'part_000.mdl', must already be in the VMF somewhere (such as in a prop_static). The operator scans the VMF for any part_000, and any that are found are used as a template for all the other parts. So you'll need to add that first part manually in Hammer first.
- Source Engine has a limit of 32 hulls per collision mesh. Going beyond 32 hulls can lead to severe lag during gameplay. The "Split Up Collision Mesh" and "Update VMF" features are handy for this. By splitting up your collision mesh into 32-hull parts, you prevent lag, and the Update VMF feature can add numerous (even dozens or hundreds) of parts automatically for you to a VMF file.

## Previews ##
### Interface ###
![image](https://github.com/theanine3D/source-engine-collision-tools/assets/88953117/ab0452ea-0949-4419-83e8-2820d7e1fba0)
### Generate Fractured Collision ###
![Untitled](https://user-images.githubusercontent.com/88953117/231557347-ce472d26-0634-4db9-a18f-0d1e7891a019.gif)
### Generate Collision Mesh
![collision-gen-1](https://user-images.githubusercontent.com/88953117/212523161-07296101-d80f-4d7e-8cbe-5ccbc93425ba.gif)
### Merge Adjacent Similars ###
![merge-similars](https://user-images.githubusercontent.com/88953117/213289714-d13d5bb8-ef37-439e-8eac-1370b4716bab.gif)
### Remove Thin Hulls
![remove-thin-hulls](https://user-images.githubusercontent.com/88953117/216437113-22036e00-dcbe-4e74-a6c9-388fb96ac173.gif)
### Video
Click the image below to watch a breakdown video of all the features in the addon.

[![YouTube Video](https://user-images.githubusercontent.com/88953117/219478247-5763224f-5bb2-443d-81ee-b17532cbb7c4.png)](https://www.youtube.com/watch?v=ASLw-FMQUXM)
