# Source Engine Collision Tools
Blender addon for generating and optimizing collision models for use in Source Engine

## Features
- **Generate Collision Mesh** - Generate a Source Engine-compliant collision model based on the current active object. The original object will be temporarily hidden, but not modified otherwise.
- **Split Up Collision Mesh** - Splits up a selected collision model into multiple separate objects, with every part having no more than 32 hulls.
- **Merge Adjacent Similars** - Merges convex hulls with similar adjacent hulls aggressively, lowering the final amount of hulls & producing a less accurate, but more performant model.
- **Remove Thin Faces** - Removes any polygons that are smaller than the average face area in the model.

## Planned Features ##
- ** Generate Source Engine QC ** - Automatically generate QC files for one or more collision model(s), allowing you to quickly compile them with batch compile tools out there (ie. Crowbar)
