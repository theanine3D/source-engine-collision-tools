# Source Engine Collision Tools
Blender addon for generating and optimizing collision models for use in Source Engine

## Features
All features are customizeable and can be tweaked via optional settings. However, in most cases, you can leave the settings at default.
- **Generate Collision Mesh** - Generate a Source Engine-compliant collision model based on the current active object.
  - Supports (optional) decimation, to automatically reduce the complexity of the resulting collision model
- **Split Up Collision Mesh** - Splits up a selected collision model into multiple separate objects, with every part having no more than 32 hulls.
- **Merge Adjacent Similars** - Merges convex hulls with similar adjacent hulls aggressively, lowering the final amount of hulls & producing a less accurate, but more performant model.
- **Remove Thin Faces** - Removes any polygons that are smaller than the average face area in the model.

## Planned Features ##
- ** Generate Source Engine QC ** - Automatically generate QC files for one or more collision model(s), allowing you to quickly compile them with batch compile tools out there (ie. Crowbar)

## Previews ##
![collision-gen-1](https://user-images.githubusercontent.com/88953117/212523161-07296101-d80f-4d7e-8cbe-5ccbc93425ba.gif)
![merge similars](https://user-images.githubusercontent.com/88953117/212523164-0a4c54df-5f35-42b5-9131-57e4ed92a899.png)
![remove-thin-faces](https://user-images.githubusercontent.com/88953117/212523166-9b911cbc-649d-43b5-918b-ecd9aa41acd9.gif)
