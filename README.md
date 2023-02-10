# MCMV

MCMV is a converter used for importing armature animations into Minecraft. Using this program, you can import virtually any armature animation into Minecraft.

Currently, it can import [.bvh files](https://research.cs.wisc.edu/graphics/Courses/cs-838-1999/Jeff/BVH.html) and export the armature animations directly to the Java version of Minecraft in .mcfunction format for datapacks, or as a Bedrock entity model and animation in .json format.   

Using programs such as blender, you can export a variety of animations into .bvh format, which can be imported into Minecraft using this converter.

Example video of it in action: https://www.youtube.com/watch?v=L2yVFUgoeBY

This converter was last developed in Python 3.10. If you are having problems with another Python version, consider switching to Python 3.10.

# Examples
Character dancing. Virtually any humanoid armature animation is able to be used to create an animation with the model on the right in Minecraft with a bit of tweaking. Custom model rigs aren't just limited to humanoid armatures.

["Characters  boxes  in dances"](https://skfb.ly/6VXqP) by Unity  (shehab house) is licensed under [Creative Commons Attribution](http://creativecommons.org/licenses/by/4.0/).

![dance](https://thumbs.gfycat.com/DescriptiveKeyEnglishpointer-size_restricted.gif)

For debugging/editing purposes, if you don't have models for each bone ready, you can have the program generate bones directly from the source model. (see below)

["Tyrannosaurus Rex"](https://skfb.ly/6X89s) by DailyArt is licensed under [Creative Commons Attribution-NonCommercial](http://creativecommons.org/licenses/by-nc/4.0/).

![dinosaur](https://thumbs.gfycat.com/SlowWeeAsiaticmouflon-size_restricted.gif?)

["phoenix bird"](https://skfb.ly/6vLBp) by NORBERTO-3D is licensed under [Creative Commons Attribution](http://creativecommons.org/licenses/by/4.0/).

![bird](https://thumbs.gfycat.com/FatalDopeyChinesecrocodilelizard-size_restricted.gif)

# Quickstart:

1. git clone or download the repository.
2. Create or pick an existing Minecraft world. Go to the save folder for that world, and put the ``armature`` folder inside ``java assets`` from the repository into ``datapacks``
3. Put the ``armature_template_rp`` folder inside the resourcepacks folder.
4. Open ``main.json`` inside the config folder in the repository.
   1. On line 63, 104, change the directory such that it matches your world's directory. Keep the last folder (dance and dinosaur) in the directory name.
   2. On line 139, 151, 172, 184, 203, 215, change the directory to where you want to save the Bedrock .geo.json and .animation.json files.

5. Open Command Prompt and navigate to the MCMV directory. Run the following and wait until completion.

```bat
python convert.py --config main.json
```

You can use different configs by changing ``main.json`` to another configuration file within the config folder.

**Java**:
1. Go into your Minecraft world that you saved the datapack into. If you were already in it, run /reload. Equip the resourcepack.
2. Run ```/scoreboard objectives add animation_time dummy```
3. Run ```/summon marker ~ ~ ~ {UUID:[I;-1154493750,-476361026,-1622016580,341842536]}``` where you want the armatures. (marker with UUID ``bb2fd2ca-e39b-4ebe-9f51-fdbc14601a68``)
4. Run ```/function animate:dance/reset``` and ```/function animate:dinosaur/reset``` to spawn the dancers and the dinosaur bones.
5. In two separate repeating command blocks, put ```/function animate:dance/main``` and ```/function animate:dinosaur/main```. Change ```Needs Redstone``` to ```Always Active```.
6. The animations should be running.

**Bedrock**:

There are guides on how to set up a resource/behavior pack for this. I will only be going into how to load the files into Blockbench.
1. Download Blockbench if you haven't already. Open Blockbench
2. Click ``Open Model`` and open a .geo file.
3. Go to the ``Animate`` tab on the top right, and click ``Import Animations`` on the left.
4. Select the correct .animation file.
5. The animations should be running.


# Usage
Following version 2.0, there are now two ways to convert the file.

The first option is writing all the conversion information in a .json file.

The second option is writing all the conversion information in a Python file.

I'd recommend going with the first option unless you want to learn more about the program.

## Option 1: json

**Note**:

Vectors are represented as a list of length 3:

``[1.0, 0.0, 0.0]`` is a vector pointing in the x direction.

Rotations can be represented in three ways:

1. ``["zyx", 10.0, 15.0, 5.0]`` is an Euler rotation with gimbal order zyx with a 10.0 degree rotation in the x axis, 15.0 degree rotation in the y axis, and a 5.0 degree rotation in the z axis.
2. ``[10.0, 15.0, 5.0]`` is the same as 1., but when an order is not specified it defaults to xyz.
3. ``[0.0, 1.0, 0.0, 0.0]`` is a unit [quaternion](https://en.wikipedia.org/wiki/Quaternion) which represents a 180 degree rotation on the y axis. If you don't know what this is, that's fine, just use one of the two other ones. If you do, great! In xyzw order.

There are three main json files required to use this converter. An example of each type of file can be found in their respective folders.

1. model
2. translation
3. config

### model

This is where information about how the armature is going to look inside Minecraft is stored.

``format_version``: The version of the generator this file should be used for.

``bones``: A list of all the bones for this armature.

#### There are two types of bones:

1. Visible Bones:
   1. Bone that is actually visible.
2. Positional Bone:
   1. A bone with no display, only used for offsets (e.g. displacement for a walking person)

Both bones have:

``parent_name``: Name of the parent bone this bone should be connected to.

``child_name``: Name of this bone.

Additionally, Visible Bones have:

``size``: Size of the bone as a three-dimensional Vector. This should point in the direction that the bone will appear when the model is in its default, non-animated pose. The magnitude determines where the next bone will be connected.

``offset``: Offset of the bone as a three-dimensional Vector. This is how much this bone should be offset from its parent's end position.

``display``: Information about the display.

Inside display, there are three parameters. The first two are for Bedrock, and the last one is for Java. You don't need all three parameters, you can fill in all the ones for Bedrock or Java.

**For Bedrock**:

``offset``: The offset of the cube relative to the bone.

``size``: The size of the cube.

**For Java**:

``item``: The item that will be used for display. (Note: You can put ``$+`` to replace it with a number later. e.g. setting the model number ``10`` in the configuration file (below) will set ``CustomModelData{$+2}`` to ``CustomModelData{102}``. This is useful if you want to reuse the same model with different textures)

### translation

This translates the bone names in model to the bone names in the .bvh file. By having a separate translate file, it makes it easy to swap out the animation file for a different one while still using the same model.

This is a simple key: item dictionary. The left is the bone name in the model, and the right is the bone name that appears in the .bvh file.

### config

This is where all the instructions are stored.

``format_version``: The version of the generator this file should be used for.

```animation_source```: A list of animations to import.
>
>Inside animation_source, you can specify details about the animation to better tailor it for your needs.
>
>``animation_name``: A unique name for this animation that is used within the config file.
>
>``type``: The type of animation this is. Currently ``bvh`` is the only option.
>
>``path``: The relative path to the animation file. They should all be in the ``data`` folder.
>
>``scale``: How much the animation should be scaled by. Default: 1.0
>
>``order``: The rotation order of the source animation file. You should be prompted with an option when exporting the .bvh file from blender. Default: xyz
>
>``face_north``: A rotation used to get the source armature facing north. This is important as all models should be facing north (you can get them to rotate after, but for the conversion they should all face north, or else there may be rotational ambiguity issues because .bvh represents bone sizes with Vectors, which have an unknown roll.) If you need help figuring this out, see below in ``model source``. Default: ["xyz", 0.0, 0.0, 0.0]
>
>``fps``: The frames per second to extract from this animation. Remember that for Java, the maximum frame rate is 20. Any higher will make the animation appear to move in slow motion. Default: 20
>
>``start_frame``: The frame to start at. Default: 0
>
>``max_frames``: The maximum number of frames this animation should contain. Negative values will make the animation contain all frames in the original file. Default: -1

``model_source``: A list of Minecraft models to import.

>There are currently two ways of creating models.
> 1. Load them from a pre-made .json file ``mcmv_json``
> 2. Create them from an animation ``create_from_animation``
>
> The second option can be used for prototyping, figuring out which direction the armature is facing so you can change the ``face_north`` parameter, or just to see the model inside Minecraft because it looks pretty cool.
>
> Both ways of creating models have the following parameters:
> 
> ``model_name``: A unique name for this model that is used within the config file.
> 
> ``type``: Whether to load or create the model (``mcmv_json`` vs ``create_from_animation``)
> 
> > For the first type of model, there is an extra parameter:
> >
> >``path``: The relative path of the model file. They should all be in the ``model`` folder.
> 
> > For the second type of model, there are three extra parameters:
> >
> >``animation_name``: Name of the animation you are going to create the model from.
> >
> > ``scale``: Scale of the model relative to the source animation (after it has been scaled from the import)
> >
> > ``base``: The "base" part of the model that moves. For a humanoid it is probably the hip/pelvis bone. Ancestor bones of the base will not be rendered.

``translation_source``: A list of translations.

> ``translation_name``: A unique name for this translation that is used within the config file.
>
> ``path``: The relative path of the model file. They should all be in the translation file.

``tasks``: A list of conversions or "tasks" the converter should perform.

> There are two possible outputs currently, which use the "java" and "bedrock" keywords in "type".
>  
> For exporting to the Java version of Minecraft in .mcfunction format for datapacks:
> 
> > ``type``: This should be set to ``java``
> >
> > ``function_path``: Path of the function folder within the datapack.
> >
> > **WARNING**: everything inside the folder will be deleted upon conversion. You should create a new folder for the animations.
> > 
> > For safety, this path must be inside an actual datapack inside a Minecraft world. Otherwise, it will fail.
> > 
> > ``reset_function``: Whether to generate a reset function to delete and re-spawn in the bones. Default: true
> > 
> > ``remove_function``: Whether to generate a removal function to delete all bones. Default: true
> > 
> > ``search_function``: Whether to generate a search tree to index each animation function with respect to a scoreboard value. Default: true
> > 
> > ``scoreboard counter``: The scoreboard player and objective to use to index the correct animation function.
> > 
> > ``auto``: Whether the main function (generated by ``search_function``) should increment the scoreboard value automatically.
> > 
> > ``loop``: Whether the main function (generated by ``search_function``) should reset the animation once it ends automatically.
> >
> > ``armatures``: A list of armatures to create.
> >
> > > Each armature can be configured using the following parameters:
> > >
> > > ``name``: Name of the armature. The folder containing the .mcfunction files for this armature will be named this. Must be unique per task.
> > > 
> > > ``model_name``: Name of the model that you are going to use that was previously imported.
> > > 
> > > ``model_no``: A string that will replace ``$+`` for the display item. Default: `` ``
> > > 
> > > ``animation_name``: Name of the animation you are going to use that was previously imported.
> > > 
> > > ``translation_name``: Name of the translation you are going to use that was previously imported. Optional if the model is one created from an animation. Default: ``null``
> > > 
> > > ``write_animation``: Information about how the animation should be imported into the game.
> > > 
> > > > ``root``: The selector / uuid of the root entity that the armature will be rooted on. Can be a vector as well to root the armature at a location. Default: ``[0.0, 0.0, 0.0]``
> > > > 
> > > > ``offset``: The offset of the armature from the root. Default: ``[0.0, 0.0, 0.0]``
> > > > 
> > > > ``rotation``: Rotation of the armature. Default: ``["xyz", 0.0, 0.0, 0.0]``
> > > > 
> > > > ``allow_rotation``: Whether the root entity should be allowed to rotate. Setting this to false will cause the armature to render incorrectly when the root entity is rotated. Default: ``true``
> 
> For exporting to the Bedrock version of Minecraft in .json format for Resource Packs:
>
> > ``type``: This should be set to ``bedrock``
> >
> > ``armatures``: A list of armatures to create.
> >
> > > ``name``: Name of the armature. Currently unused.
> > >
> > > ``model_name``: Name of the model that you are going to use that was previously imported.
> > > 
> > > ``model_no``: A string that will replace ``$+`` for the display item. Default: `` ``
> > > 
> > > ``animation_name``: Name of the animation you are going to use that was previously imported.
> > > 
> > > ``translation_name``: Name of the translation you are going to use that was previously imported. Optional if the model is one created from an animation. Default: ``null``
> > > 
> > > ``write_geo_model``: Information about how the model for the .geo.json file should be constructed. Optional if you already have a .geo.json model.
> > > 
> > > > ``geo_model_path``: Path where the .geo.json file should be saved.
> > > >
> > > > ``file_name``: Name that the .geo.json file should be saved as.
> > > > 
> > > > ``bedrock format``: Information required as the header of a Bedrock .geo.json file. If you have worked with Bedrock Resource Packs before you should know what this is.
> > > > 
> > > > > ``format_version``: Resource pack format version
> > > > >
> > > > > ``identifier``: Entity geometry name.
> > > > >
> > > > > ``texture_size``: Size of the textures.
> > > > 
> > > > ``offset``: Offset of the model from the origin. Default: ``[0.0, 0.0, 0.0]``
> > > > 
> > > > ``rotate``: How much the model's root should be rotated. Default: ``["xyz", 0.0, 0.0, 0.0]``
> > > 
> > > ``write_animation``: Informatino about how the animation for the .animation.json file should be constructed. Optional, but if you're not generating this what are you even using this tool for?
> 
> > > > ``animation_model_path``: Path where the .animation.json file should be saved.
> > > >
> > > > ``file_name``: Name that the .animation.json file should be saved as.
> > > > 
> > > > ``bedrock format``: Information required as the header of a Bedrock .animation.json file. If you have worked with Bedrock Resource Packs before you should know what this is.
> > > > 
> > > > > ``format_version``: Resource pack format version
> > > > >
> > > > > ``identifier``: Animation name.

## Option 2: Python

You should read how to import this using .json first to get an understanding of how this works. This can also be found in example.py

There may be parameters not shown here, look inside the code for more.

Load a .bvh file by creating a BvhFileLoader object:

```py
file_loader = BvhFileLoader('data/dance.bvh', scale=0.1, order='xyz', face_north=Quaternion().set_from_euler(Euler('xyz', -90.0, 0.0, 0.0)))
```

Save the model and animation.

```py
model = file_loader.get_model()

animation = file_loader.get_animation()
```

Create a list of bone information similar to the model json file. (Optional if you are going to create bones from the animation)

```py
bone_list = [
 ('body',
  'head',
  Vector3(0.0, 8.0, 0.0),
  Vector3(0.0, 0.0, 0.0),
  DisplayVoxel(Vector3(-4.0, 0.0, -4.0), Vector3(8.0, 8.0, 8.0), 'diamond_hoe{CustomModelData:100}')
  ),
 ('hip',
  'body',
  Vector3(0.0, 12.0, 0.0),
  Vector3(0.0, 0.0, 0.0),
  DisplayVoxel(Vector3(-4.0, 0.0, -2.0), Vector3(8.0, 12.0, 4.0), 'diamond_hoe{CustomModelData:101}')
  ),
...  
 ('knee_l',
  'ankle_l',
  Vector3(0.0, -6.0, 0.0),
  Vector3(0.0, 0.0, -2.0),
  DisplayVoxel(Vector3(-2.0, -6.0, 0.0), Vector3(4.0, 6.0, 4.0), 'diamond_hoe{CustomModelData:109}')
  ),
 (
  'root',
  'hip'
 )
```

Make a translation dictionary just like the translation json file. (Optional if you are going to create bones from the animation)

```py
translation = {
    'hip': 'Bip001 Pelvis_177',
    'body': 'Bip001 Spine_178',
    'head': 'Bip001 Head_195',

    'elbow_r': 'Bip001 R Forearm_205',
    'wrist_r': 'Bip001 R Hand_206',

    'knee_r': 'Bip001 R Calf_187',
    'ankle_r': 'Bip001 R Foot_188',

    'elbow_l': 'Bip001 L Forearm_199',
    'wrist_l': 'Bip001 L Hand_200',
    
    'knee_l': 'Bip001 L Calf_180',
    'ankle_l': 'Bip001 L Foot_181'
}
```

Create a MinecraftModelCreator object.

```py
m = MinecraftModelCreator()
```

Set or create bones.

```py
# set bones
m.set_bones(bone_list)

# or, create bones from the animation model
m.create_bones(model)
```

To export to Java:

```py
j = JavaModelExporter('C:/Users/USER/AppData/Roaming/.minecraft/saves/WORLD NAME/datapacks/armature/data/animate/functions/NAME')

# You can leave out translation if you're using created bones.
j.set_model_info(model, m.minecraft_model, translation)

# For this UUID, you can summon a marker using: /summon marker ~ ~ ~ {UUID:[I;-1154493750,-476361026,-1622016580,341842536]}
j.write_animation('ARMATURE_NAME', animation, 'bb2fd2ca-e39b-4ebe-9f51-fdbc14601a68', allow_rotation=True, offset=Vector3(0.0, 0.1, 0.0), rotate=Quaternion(0.0, 0.0, 0.0, 1.0))

j.write_reset_function()
j.write_remove_function()
j.write_search_function()
```

To export to Bedrock:

```py
b = BedrockModelExporter()

b.set_model_info(model, m.minecraft_model, translation)
b.write_geo_model('C:/GEO_MODEL_PATH', 'MODEL_NAME',BedrockGeoFileFormatter('1.12.0', 'geometry.unknown', (64, 64)))

b.write_animation('C:/ANIMATION_MODEL_PATH', 'ANIMATION_NAME', BedrockAnimFileFormatter('1.8.0', 'animation.model.new'), animation)
```


