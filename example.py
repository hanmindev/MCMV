from mcmv.armature_formatter import MinecraftModelCreator
from mcmv.armature_objects import DisplayVoxel
from mcmv.export_bedrock import BedrockModelExporter, BedrockGeoFileFormatter, BedrockAnimFileFormatter
from mcmv.export_java import JavaModelExporter
from mcmv.import_file import BvhFileLoader
from mcmv.math_objects import Vector3, Quaternion, Euler

file_loader = BvhFileLoader('data/dance.bvh', scale=0.1, order='xyz', face_north=Quaternion().set_from_euler(Euler('xyz', -90.0, 0.0, 0.0)))

model = file_loader.get_model()

animation = file_loader.get_animation()

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
 ('body',
  'elbow_r',
  Vector3(0.0, -5.0, 0.0),
  Vector3(4.0, -1.0, 0.0),
  DisplayVoxel(Vector3(0.0, -5.0, -2.0), Vector3(4.0, 6.0, 4.0), 'diamond_hoe{CustomModelData:102}')
  ),
 ('elbow_r',
  'wrist_r',
  Vector3(0.0, -4.0, 0.0),
  Vector3(2.0, 0.0, 0.0),
  DisplayVoxel(Vector3(-2.0, -6.0, -2.0), Vector3(4.0, 6.0, 4.0), 'diamond_hoe{CustomModelData:103}')
  # )
  ),
 ('body',
  'elbow_l',
  Vector3(0.0, -5.0, 0.0),
  Vector3(-4.0, -1.0, 0.0),
  DisplayVoxel(Vector3(-4.0, -5.0, -2.0), Vector3(4.0, 6.0, 4.0), 'diamond_hoe{CustomModelData:104}')
  ),
 ('elbow_l',
  'wrist_l',
  Vector3(0.0, -4.0, 0.0),
  Vector3(-2.0, 0.0, 0.0),
  DisplayVoxel(Vector3(-2.0, -6.0, -2.0), Vector3(4.0, 6.0, 4.0), 'diamond_hoe{CustomModelData:105}')
  # )
  ),
 ('body',
  'knee_r',
  Vector3(0.0, -6.0, 0.0),
  Vector3(2.0, -12.0, 0.0),
  DisplayVoxel(Vector3(-2.0, -6.0, -2.0), Vector3(4.0, 6.0, 4.0), 'diamond_hoe{CustomModelData:106}')
  ),
 ('knee_r',
  'ankle_r',
  Vector3(0.0, -6.0, 0.0),
  Vector3(0.0, 0.0, -2.0),
  DisplayVoxel(Vector3(-2.0, -6.0, 0.0), Vector3(4.0, 6.0, 4.0), 'diamond_hoe{CustomModelData:107}')
  ),
 ('body',
  'knee_l',
  Vector3(0.0, -6.0, 0.0),
  Vector3(-2.0, -12.0, 0.0),
  DisplayVoxel(Vector3(-2.0, -6.0, -2.0), Vector3(4.0, 6.0, 4.0), 'diamond_hoe{CustomModelData:108}')
  ),
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
]

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

m = MinecraftModelCreator()

# set bones

m.set_bones(bone_list)

# or, create bones from the animation model

# m.create_bones(model)

j = JavaModelExporter('C:/Users/USER/AppData/Roaming/.minecraft/saves/WORLD NAME/datapacks/armature/data/animate/functions/NAME')

# You can leave out translation if you're using created bones.
j.set_model_info(model, m.minecraft_model, translation)

# For this UUID, you can summon a marker using: /summon marker ~ ~ ~ {UUID:[I;-1154493750,-476361026,-1622016580,341842536]}
j.write_animation('ARMATURE_NAME', animation, 'bb2fd2ca-e39b-4ebe-9f51-fdbc14601a68', allow_rotation=True, offset=Vector3(0.0, 0.1, 0.0), rotate=Quaternion(0.0, 0.0, 0.0, 1.0))

j.write_reset_function()
j.write_remove_function()
j.write_search_function()

b = BedrockModelExporter()

b.set_model_info(model, m.minecraft_model, translation)
b.write_geo_model('C:/GEO_MODEL_PATH', 'MODEL_NAME', BedrockGeoFileFormatter('1.12.0', 'geometry.unknown', (64, 64)))

b.write_animation('C:/ANIMATION_MODEL_PATH', 'ANIMATION_NAME', BedrockAnimFileFormatter('1.8.0', 'animation.model.new'), animation)
