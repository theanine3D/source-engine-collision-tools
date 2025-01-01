# Source Engine Collision Tools
Blender (3.x+ / 4.x+) addon for generating and optimizing collision models for use in Source Engine games (ie. TF2, GMod, L4D2). Works best when combined with the [Blender Source Tools](http://steamreview.org/BlenderSourceTools/).

This addon can be useful for generating collision for other game engines too. However, only support for Source is specifically promised and tested.

Finding this addon useful? Please consider starring it ⭐, or donating 🙂<br>
[![image](https://user-images.githubusercontent.com/88953117/232652206-a5b7c5a1-d4cc-40ec-88d7-d3a5886d8f55.png)](https://www.paypal.com/donate/?hosted_button_id=K63REE7KJ3WUY)

Need help with the addon? You can join my Discord server and reach out for help there.
https://discord.gg/gdu5myxw

## Features
Some features are customizeable and can be tweaked via optional settings. There is also a "Recommended Settings" button that will automatically guess the best settings for you based on the currently selected, active object.
Note that all of the "Generate" features support the Decimate Ratio setting, to automatically reduce the complexity of the resulting collision model.
- **Generate Collision via Bisection** - Generate a Source Engine-compliant collision model for every currently selected object, by using Blender's own built-in Bisect tool to divide up the model into sections first.
- **Generate Collision from Faces** - Generate a Source Engine-compliant collision model for every currently selected object, based on the mesh's faces/polygons.
- **Generate Collision via UV Map** - Generates a collision mesh for the currently selected objects, based on each object's UV Map. Each UV island becomes a separate hull.
- **Generate Collision via Fracture** - This operator uses the Cell Fracture addon built into Blender to generate more accurate and performant collision meshes for Source Engine. However, unlike the above operator, it is intended to be used on individual props, not entire scenes at once. Works best on fully sealed objects with no holes or non-manifold geometry.
  - This collision method is unique in that it also creates a gap between collision hulls to prevent overlapping. The size of the gap is determined by the "Gap Width" setting
  - Attempts to generate only the amount of hulls specified by the "Fracture Target" setting. ie. A "Fracture Target" of 4 will try to split up the model into only 4 parts.
  - Note that the Cell Fracture addon needs to be enabled in your Blender preferences first!

- **Split Up Collision Mesh** - Splits up selected collision models into multiple separate objects, with every part having no more than 32 hulls.
- **Merge Adjacent Similars** - Merges convex hulls with similar adjacent hulls aggressively, lowering the final amount of hulls & producing a (potentially) less accurate, but more performant model. Similarity is based on the face count and volume of the hulls.
- **Remove Thin Hulls** - Removes any convex hulls that are significantly smaller than all other hulls.
- **Force Convex** - Forces all existing hulls in every selected collision model to be convex. Especially useful after using Blender's built-in Decimate modifier on an existing collision mesh, to ensure that any decimated hulls are still convex.
- **Remove Inside Hulls** - Removes any hulls that are completely or almost completely buried inside other hulls.
- **Convex Cut** - A combination of the Bisect and Convex Hull operators in Blender. This lets you cut up the model and at the same time convert the cut pieces into convex hulls. Can be found via the Mesh menu in Edit Mode. 
- **Generate Source Engine QC** - Automatically generate QC files for one or more collision model(s), allowing you to quickly compile them with batch compile tools out there (ie. [Crowbar](https://developer.valvesoftware.com/wiki/Crowbar))
  - Supports adding custom QC commands via a QC Override system. This allows you to, for example, add a custom "$scale" or "$surfaceprop" command to all generated QC files.
- **Update VMF** - Updates a selected VMF file by automatically adding any partitioned/split-up collision models that haven't already been added to the map.
- **Export Hulls to Hammer .VMF** - Converts hulls in the selected collision mesh(es) into Source Engine brush solids and exports them as a .VMF file that can be opened in Hammer.

## Installation
- If you are using Blender 4.2 or higher, you can install the addon via Blender's official [online extension repository](https://extensions.blender.org/add-ons/sourceenginecollisiontools/), which can also be accessed via Blender's Preferences.
- If you are using Blender 4.1 or lower, you can get the newest, bleeding edge version of the addon by pressing the big green "Code" button above, and choose "Download ZIP"
- If you want a more stable release, check the [Releases](https://github.com/theanine3D/source-engine-collision-tools/releases).
- After downloading either of the above, go into Blender's addon preferences (File → Preferences → Addons)
4. Click the "Install..." button and browse to the ZIP file you just downloaded, select it, and press "Install Add-on"

## Tips
- The UI for the addon is found in the "Object Properties" tab on the right-hand side of the Blender window.
- Decimation (by the Generate Collision Mesh operator) generally makes the Merge Adjacent Similars operator less effective, but Decimation is much faster at reducing the final complexity of the collision mesh. However, Decimation will reduce the complexity uniformly across the entire model, whereas Merge Adjacent Similars tries to reduce complexity only where similar hulls are found.
- Merge Adjacent Similars is less effective on overly large, complex models. For best results, split up a large complex model into several (3-5) separate pieces first, and then use Merge Adjacent Similars on each individual piece.
- For the "Update VMF" feature, the very first part of your split-up collision mesh, ending in 'part_000.mdl', must already be in the VMF somewhere (such as in a prop_static). The operator scans the VMF for any part_000, and any that are found are used as a template for all the other parts. So you'll need to add that first part manually in Hammer first.
- Source Engine has a limit of 32 hulls per collision mesh. Going beyond 32 hulls can lead to severe lag during gameplay. The "Split Up Collision Mesh" and "Update VMF" features are handy for this. By splitting up your collision mesh into 32-hull parts, you prevent lag, and the Update VMF feature can add numerous (even dozens or hundreds) of parts automatically for you to a VMF file.
- To utilize the QC override system, add a string-based Custom Property (in the bottom of the Object Properties panel) to one split-up collision object in your Blender scene, with the property name starting with "$". Enter the value/parameters for this property. Then press the Copy QC Overrides button to copy this override to all other selected collision parts. These will be included in the resulting generated QC files.
  - ![image](https://github.com/theanine3D/source-engine-collision-tools/assets/88953117/ca659755-e483-4866-871c-a9fc3848898d)

## Previews ##
### Interface ###
![image](https://github.com/user-attachments/assets/cc9d4aad-07d8-46cd-b445-739a42e1e504)
### Generate Collision by Bisection ###
![generate-by-bisection](https://github.com/user-attachments/assets/598a1280-7f10-4b24-ab31-533ad00c6d88)
### Generate Collision by Fracture ###
![Untitled](https://user-images.githubusercontent.com/88953117/231557347-ce472d26-0634-4db9-a18f-0d1e7891a019.gif)
### Generate Collision from Faces
![collision-gen-1](https://user-images.githubusercontent.com/88953117/212523161-07296101-d80f-4d7e-8cbe-5ccbc93425ba.gif)
### Merge Adjacent Similars ###
![merge-similars](https://user-images.githubusercontent.com/88953117/213289714-d13d5bb8-ef37-439e-8eac-1370b4716bab.gif)
### Remove Thin Hulls
![remove-thin-hulls](https://user-images.githubusercontent.com/88953117/216437113-22036e00-dcbe-4e74-a6c9-388fb96ac173.gif)

### Videos
Click the image below to watch a breakdown video of most of the features in the addon.

[![YouTube Video](https://user-images.githubusercontent.com/88953117/219478247-5763224f-5bb2-443d-81ee-b17532cbb7c4.png)](https://www.youtube.com/watch?v=ASLw-FMQUXM)

This video below shows some newer features that have been added since the previous video.

[![YouTube Video](https://github.com/user-attachments/assets/7244d17f-90cb-40fc-9117-e9aa341ea8d5)](https://youtu.be/yWF5ngntf5A)

### Gallery
The maps below were created using Source Engine Collision Tools. (If you're a mapper using my addon for your maps, send me a message if you want to list your map here!)

- #### Saturn Valley - TF2 map by Theanine3D

  - [![YouTube Video](https://github.com/user-attachments/assets/28a24da2-f792-4ab3-abb9-473d3a75bfc0)](https://www.youtube.com/watch?v=jbJhX8MaSDQ)
