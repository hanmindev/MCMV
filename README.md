# bvh-to-mcf
.bvh file to .mcfunction converter  

Example video of it in action: https://www.youtube.com/watch?v=L2yVFUgoeBY

Quick setup for beginners tutorial: https://www.youtube.com/watch?v=uLdCslxuUDs [outdated, but if you follow the tutorial below you should be able to follow through]. I will post an updated tutorial as soon as I have some time free from school.

This program lets you import pretty much any armature animations into Minecraft by converting .bvh files into .mcfunction.

Using programs like blender, you can export animations to .bvh which can be converted by this program into .mcfunction.

# Examples
Character dancing. Virtually any humanoid armature animation is able to be used to create an animation with the model on the right with a bit of tweaking.

!["Characters  boxes  in dances"](https://skfb.ly/6VXqP) by Unity  (shehab house) is licensed under ![Creative Commons Attribution](http://creativecommons.org/licenses/by/4.0/).

![dance](https://thumbs.gfycat.com/DescriptiveKeyEnglishpointer-size_restricted.gif)

For debugging/editing purposes, if you don't have models for each bone ready, you can have the program generate temporary bones using the "fill_in" parameter. (see below)

!["Tyrannosaurus Rex"](https://skfb.ly/6X89s) by DailyArt is licensed under ![Creative Commons Attribution-NonCommercial](http://creativecommons.org/licenses/by-nc/4.0/).

![dinosaur](https://thumbs.gfycat.com/SlowWeeAsiaticmouflon-size_restricted.gif)

!["phoenix bird"](https://skfb.ly/6vLBp) by NORBERTO-3D is licensed under ![Creative Commons Attribution](http://creativecommons.org/licenses/by/4.0/).

![bird](https://thumbs.gfycat.com/FatalDopeyChinesecrocodilelizard-size_restricted.gif)

# Usage
Following version 2.0, there are now two ways to convert the file.

The first option is writing all the conversion information in a .json file.

The second option is writing all the conversion information in a Python file.

I'd recommend going with the first option unless you want to learn more about the program. 


## Option 1: .json

We will be using example.json.

1. Create a folder named 'data' in the same directory as main.py. This is where your .bvh files should be.
2. (line 7) Replace the path in "function_path" to your datapack directory.
3. (line 15) Write the name of your .bvh file.
4. (line 16) Scale your .bvh model if you know it is the wrong size. If you don't know, I'd recommend putting 0.01 and later increasing it.
5. (line 17) If you know the euler angle order for your model, put it down. If you don't, it's probably xyz. You should have been prompted when exporting your .bvh file on blender.
6. (line 19) If your armature doesn't spawn in game facing north (-z), you will have to tweak these values so it faces north. The values are in degrees.
7. (line 22) Give your character a name. The name must be lowercase alphanumeric and underscores, no spaces.
8. (line 26) Provide an entity UUID for where the armature should be positioned at. If you're going to leave it as default, you're going to have to do: ``/summon marker ~ ~ ~ {UUID:[I;1424353081,-1843313156,-1603291854,1830243575]}`` later in game.
9. (line 30) Provide the name of the bone where the armature's body starts. It is probably the pelvis / hip / spine. Check the .bvh file for the exact name.
10. (lines 36-103) All the information has been filled out for a humanoid model. However, your model likely does not have the exact same names as the one I used. Open the .bvh file and find the names of all the bones and fill them in accordinly. The start_bone must be a parent of end_bone. If you don't have a humanoid model, you can define your own bones to be displayed. Size is the size of your item model (e.g. player body is 12 pixels tall), and offset is the offset that your item model will have (right arm is 4 pixels to the right of the body). If you want to debug / just want to import your model into Minecraft, delete everythign inside stands: \[\] and set "fill_in" to true (line 106).
11. You can remove lines 110-195. Don't forget to remove the comma on line 109. If you want to add additional armatures, add it back after.

With that, you should be ready to go!

Open command prompt, navigate to the directory, and run

```python json_example.py```

## Option 2. Python (skip if you want to skip the hassle):

example.py has an example that you can use to follow along. It should need minor changes to get it working.

1. Create a folder named 'data' in the same directory as main.py. This is where your .bvh files should be.
2. Create an instance of a MainConverter class with a path to where the functions should be written to. WARNING: THIS WILL DELETE THE FOLDER AND ALL IT'S CONTENTS  
```py
converter = MainConverter('C:/Users/USER/AppData/Roaming/.minecraft/saves/WORLD_NAME/datapacks/DATAPACK_NAME/data/animate/functions/FOLDER')
```  
3. Load the .bvh file into the converter. A full list of parameters can be found in example.py.
```py
converter.load_file('data/ANIMATION_FILE.bvh', 2.0, 'xyz', face_north=Quaternion().set_from_euler(Euler('xyz', 0.0, 0.0, 0.0)))
```

It's important that your armature starts off facing north (-z) in Minecraft. Leave face_north as is for now, and after the armature is imported in the game, change the angles to make it face north. The values are in degrees.


4. Create an armature by defining it's name, root entity UUID, and in-game bones. Example:
```py
converter.create_armature('character_1', scale=1.0, uuid='54e5e739-9221-45fc-a06f-b5326d174cf7',
                              offset=Vector3(0.0, -1.2, 0.0), rotate=Quaternion(0.0, 0.0, 0.0, 1.0),
                              base='Hip',
                              stands=[('Neck',
                                       'Head',
                                       'diamond_hoe{CustomModelData:101}',
                                       Vector3(0.0, 8.0, 0.0).scaled_pixels_to_meter(),
                                       Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter()
                                       ),
                                      ('Waist',
                                       'Spine',
                                       'diamond_hoe{CustomModelData:102}',
                                       Vector3(0.0, 12.0, 0.0).scaled_pixels_to_meter(),
                                       Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter()
                                       ),
                                      ('Right_Arm',
                                       'Right_Elbow',
                                       'diamond_hoe{CustomModelData:103}',
                                       Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                       Vector3(-4.0, 0.0, 0.0).scaled_pixels_to_meter()
                                       ) # ... more bones
                                      ]
                              )
```
The armature name should be alphanumeric + dash/underscores, no spaces.  

The root entity UUID should be the UUID of the entity you want the armature to be centered at. The function will not spawn the root entity in, so you should spawn a marker entity and get it's UUID first. If you're using the default one, use this command to spawn it in: ``/summon marker ~ ~ ~ {UUID:[I;1424353081,-1843313156,-1603291854,1830243575]}``  

Each bone is represented as a tuple. The items in the tuple are, in order:  
* Name of the parent bone. This should match the name of the bones in the .bvh file.  
* Name of the child bone. This should match the name of the bones in the .bvh file. Alternatively, an initial pose vector may be used.  
Initial-Pose vector: Define the T-pose direction of the bone. Check which direction the bone is facing while poseless in the .bvh model. e.g. A model doing a T-pose may have the left-arm pointing in the x-direction. Then, the vector would be (1.0, 0.0, 0.0). Magnitude does not matter.  
* Name of the item that will be displayed between the parent bone and the child bone. For example, if the parent bone is "Right_Arm" and the child bone is "Right_Elbow", the item should be a model of the bone that connects the right arm and the right elbow (bicep area)
* Size Vector: Define the size of the bone in Minecraft. e.g. 'Head' has a size vector of Vector3(0.0, 8.0, 0.0).scaled_pixels_to_meter() because it is 8 pixels tall. So if Head had a child, for example a hat, it will be placed visually on top of the head. This vector should correspond to the block model. e.g. If the 'Arm' model is pointing down, the vector should be (0.0, -8.0, 0.0). If it is pointing in the x-direction, the vector should be (8.0, 0.0, 0.0).  
* Offset Vector: Define the offset of the bone in Minecraft relative to it's parent. e.g. 'Head' with an offset vector of (0.0, 0.0, 0.0) is too low and overlaps with the body. Thus an offset vector of Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter() is used. This offset vector is rotated by the parent's rotation, it is not a global offset.  


5. Repeat steps 3 and 4 if you have more armatures to export to the same folder.
6. Generate a reset function for the armatures.
```py
converter.reset_function()
```
7. Generate a search function for the armatures.
```py
converter.search_function()
```

With that, you should be ready to go! Just run the file.

## Minecraft
1. You should have spawned in entities as described previously.
2. Add scoreboard.
```
/scoreboard objectives add animation_time dummy
```
3. Reset entities. The function should be in the folder where you saved your functions.  
e.g. if your path is ```C:/Users/USER/AppData/Roaming/.minecraft/saves/WORLD_NAME/datapacks/DATAPACK_NAME/data/animate/functions/FOLDER```, you should be able to run your function using:  
```/function animate:FOLDER/reset```
4. Play animation: In the same folder as the reset function in step 3, there should be a 'main' function.  
e.g. if your reset function was ```/function animate:FOLDER/reset```, your main function should be ```/function animate:FOLDER/main```.
Running this function in Minecraft will display a single frame, with the frame number being the value of global's animation_time score. Set a clock with the 'main' function command and ```scoreboard players add global animation_time 1```.
e.g. In a loop:
```
scoreboard players add global animation_time 1
function animate:FOLDER/main
```

That should be it! If I missed anything please let me know!

I'll try and find a way to put up a proper documentation somewhere because this program can do quite a bit of stuff and I'm constantly adding more features to it, but I haven't had the time to note it all down.
