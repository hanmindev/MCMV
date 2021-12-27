# bvh-to-mcf
.bvh file to .mcfunction converter
Example video of it in action: https://www.youtube.com/watch?v=L2yVFUgoeBY

This program lets you import armature animations into Minecraft by converting .bvh files into .mcfunction.

Using programs like blender, you can export animations to .bvh which can be converted by this program into .mcfunction.

# Usage
See leo_need_roki.py for an example. There is a lot to write so it is recommended that you make a separate file to run the program.

## Python:
1. Create a folder named 'data' in the same directory as main.py.
2. Create an instance of a MainConverter class with a path to where the functions should be written to.  
```py
converter = MainConverter('C:/Users/USER/AppData/Roaming/.minecraft/saves/WORLD_NAME/datapacks/DATAPACK_NAME/data/animate/functions/FOLDER')
```  
3. Load the .bvh file into the converter with a scale value and Euler rotation order (optional, default 'xyz')
```py
converter.load_file('data/ANIMATION_FILE.bvh', 2.0, 'xyz')
```
4. Create an armature by defining it's name, root entity UUID, and in-game bones. Example:
```py
converter.globalize_armature('character_1', '54e5e739-9221-45fc-a06f-b5326d174cf7',
                                 [('Head',
                                   '2f9d6e9a-aaca-4964-9059-ec43f2016499',
                                   '19c4830d-8714-4e62-b041-0cde12b6de96',
                                   Vector3(0.0, 8.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0),
                                   'diamond_hoe{CustomModelData:101}'
                                   ),
                                  ('Body',
                                   '41451f74-0acb-4406-a42f-cc90a4a04c9b',
                                   '530b439d-1760-4652-93a7-3320f269358a',
                                   Vector3(0.0, 12.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0),
                                   'diamond_hoe{CustomModelData:102}'
                                   ),
                                   # ... more bones
                                 ]
                               )
```
The armature name should be alphanumeric + dash/underscores, no spaces.  

The root entity UUID should be the UUID of the entity you want the armature to be centered at. The function will not spawn the root entity in, so you should spawn a marker entity and get it's UUID first.  

Each bone is represented as a tuple. The items in the tuple are, in order:  
* Name of the bone. This should match the name of the bones in the .bvh file.  
* UUID of the AEC (will be spawned in, pick an arbitrary UUID).  
* UUID of the Armor Stand (will be spawned in, pick an arbitrary UUID).  
* Size Vector: Define the size of the bone in Minecraft. e.g. 'Head' has a size vector of Vector3(0.0, 8.0, 0.0).scaled_pixels_to_meter() because it is 8 pixels tall. So if Head had a child, for example a hat, it will be placed visually on top of the head. This vector should correspond to the block model. e.g. If the 'Arm' model is pointing down, the vector should be (0.0, -8.0, 0.0). If it is pointing in the x-direction, the vector should be (8.0, 0.0, 0.0).  
* Offset Vector: Define the offset of the bone in Minecraft relative to it's parent. e.g. 'Head' with an offset vector of (0.0, 0.0, 0.0) is too low and overlaps with the body. Thus an offset vector of Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter() is used. This offset vector is rotated by the parent's rotation, it is not a global offset.  
* Initial-Pose vector: Define the T-pose direction of the bone. Check which direction the bone is facing while poseless in the .bvh model. e.g. A model doing a T-pose may have the left-arm pointing in the x-direction. Then, the vector would be (1.0, 0.0, 0.0). Magnitude does not matter.  

5. Repeat steps 3 and 4 if you have more armatures to export to the same folder.
6. Generate a reset function for each of the armatures.
```py
converter.reset_function('character_1')
```
7. Generate a search function for each of the armatures.
```py
converter.search_function('character_1')
```

## Minecraft
1. You should have spawned in entities as described in step 4 in instructions for Python.
2. Add scoreboard.
```
/scoreboard objectives add animation_time dummy
```
3. Reset entities. The function should be in the folder defined in step 2 in instructions for Python  
e.g. if your path is ```C:/Users/USER/AppData/Roaming/.minecraft/saves/WORLD_NAME/datapacks/DATAPACK_NAME/data/animate/functions/FOLDER```, you should be able to run your function using:  
```/function animate:FOLDER/reset```
4. Play animation: In the same folder as the reset function in step 3, there should be a 'main' function.  
e.g. if your reset function was ```/function animate:FOLDER/reset```, your main function should be ```/function animate:FOLDER/main```.
Running this function in Minecraft will display a single frame, with the frame number being the value of global's animation_time score. Set a clock with the 'main' function command and ```scoreboard players add global animation_time 1```.
e.g. In a loop:
```
scoreboard players add global animation_time 1
function animate:FOLDER/reset
```
