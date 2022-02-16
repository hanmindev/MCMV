from main import MainConverter
from math_objects import Euler, Quaternion, Vector3

if __name__ == '__main__':
    converter = MainConverter('C:/Users/USER_NAME/AppData/Roaming/.minecraft/saves/WORLD_NAME/'
                              'datapacks/DATAPACK_NAME/data/animate/functions/FUNCTION_NAME')
    converter.load_file('data/CHARACTER1.bvh', scale=2.0, order='xyz', max_frames=None,
                        face_north=Quaternion().set_from_euler(Euler('xyz', 0.0, 0.0, 0.0)))

    # debug armature made up of blocks. Uncomment if it you would like.
    # converter.create_debug_armature('character_1', uuid=None, offset=Vector3(0.0, 0.0, 0.0),
    #                                 rotate=Quaternion(0.0, 0.0, 0.0, 1.0),
    #                                 show_names=False, scale=1.0)

    # actual armature. You will need to spawn in the marker entity.
    # command to summon marker: /summon marker ~ ~ ~ {UUID:[I;1424353081,-1843313156,-1603291854,1830243575]}
    # If you want to generate an NBT using a UUID, use this python function:

    # import utility
    # utility.uuid_str_to_uuid_nbt('54e5e739-9221-45fc-a06f-b5326d174cf7')
    converter.create_armature('character_1', scale=1.0, uuid='54e5e739-9221-45fc-a06f-b5326d174cf7',
                              offset=Vector3(0.0, -1.2, 0.0), rotate=Quaternion(0.0, 0.0, 0.0, 1.0),
                              base='Hip', show_names=False, fill_in=False, center=True,
                              allow_rotation=False,
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
                                       ),
                                      ('Right_Elbow',
                                       'Right_Wrist',
                                       'diamond_hoe{CustomModelData:104}',
                                       Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                       Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter()
                                       ),
                                      ('Left_Arm',
                                       'Left_Elbow',
                                       'diamond_hoe{CustomModelData:105}',
                                       Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                       Vector3(4.0, 0.0, 0.0).scaled_pixels_to_meter()
                                       ),
                                      ('Left_Elbow',
                                       'Left_Wrist',
                                       'diamond_hoe{CustomModelData:106}',
                                       Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                       Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter()
                                       ),
                                      ('Right_Thigh',
                                       'Right_Knee',
                                       'diamond_hoe{CustomModelData:107}',
                                       Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                       Vector3(-2.0, 0.0, 0.0).scaled_pixels_to_meter()
                                       ),
                                      ('Right_Knee',
                                       'Right_Ankle',
                                       'diamond_hoe{CustomModelData:108}',
                                       Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                       Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter()
                                       ),
                                      ('Left_Thigh',
                                       'Left_Knee',
                                       'diamond_hoe{CustomModelData:109}',
                                       Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                       Vector3(2.0, 0.0, 0.0).scaled_pixels_to_meter()
                                       ),
                                      ('Left_Knee',
                                       'Left_Ankle',
                                       'diamond_hoe{CustomModelData:110}',
                                       Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                       Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter()
                                       )
                                      ]
                              )
    converter.load_file('data/CHARACTER2.bvh', 2.0)
    converter.create_armature('character_2',
                              stands=[('Neck',
                                       'Head',
                                       'diamond_hoe{CustomModelData:111}',
                                       Vector3(0.0, 8.0, 0.0).scaled_pixels_to_meter(),
                                       Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter()
                                       ),
                                      ('Waist',
                                       'Spine',
                                       'diamond_hoe{CustomModelData:112}',
                                       Vector3(0.0, 12.0, 0.0).scaled_pixels_to_meter(),
                                       Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter()
                                       ),
                                      ('Right_Arm',
                                       'Right_Elbow',
                                       'diamond_hoe{CustomModelData:113}',
                                       Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                       Vector3(-4.0, 0.0, 0.0).scaled_pixels_to_meter()
                                       ),
                                      ('Right_Elbow',
                                       'Right_Wrist',
                                       'diamond_hoe{CustomModelData:114}',
                                       Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                       Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter()
                                       ),
                                      ('Left_Arm',
                                       'Left_Elbow',
                                       'diamond_hoe{CustomModelData:115}',
                                       Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                       Vector3(4.0, 0.0, 0.0).scaled_pixels_to_meter()
                                       ),
                                      ('Left_Elbow',
                                       'Left_Wrist',
                                       'diamond_hoe{CustomModelData:116}',
                                       Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                       Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter()
                                       ),
                                      ('Right_Thigh',
                                       'Right_Knee',
                                       'diamond_hoe{CustomModelData:117}',
                                       Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                       Vector3(-2.0, 0.0, 0.0).scaled_pixels_to_meter()
                                       ),
                                      ('Right_Knee',
                                       'Right_Ankle',
                                       'diamond_hoe{CustomModelData:118}',
                                       Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                       Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter()
                                       ),
                                      ('Left_Thigh',
                                       'Left_Knee',
                                       'diamond_hoe{CustomModelData:119}',
                                       Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                       Vector3(2.0, 0.0, 0.0).scaled_pixels_to_meter()
                                       ),
                                      ('Left_Knee',
                                       'Left_Ankle',
                                       'diamond_hoe{CustomModelData:120}',
                                       Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                       Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter()
                                       )
                                      ],
                              uuid='3888fe0d-41b5-46ad-9740-797228c6c3c3', base='Hip', offset=Vector3(0.0, -1.2, 0.0)
                              )
    converter.reset_function()
    converter.remove_function()
    converter.search_function('global animation_time')
