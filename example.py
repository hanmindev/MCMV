from main import MainConverter
from math_objects import Vector3

if __name__ == '__main__':
    converter = MainConverter('C:/Users/USER/AppData/Roaming/.minecraft/saves/WORLD_NAME/'
                              'datapacks/DATAPACK_NAME/data/animate/functions/FOLDER_NAME')
    converter.load_file('data/CHARACTER_1.bvh', 2.0)

    converter.globalize_armature('CHARACTER_1', '54e5e739-9221-45fc-a06f-b5326d174cf7',
                                 [('Neck',
                                   '2f9d6e9a-aaca-4964-9059-ec43f2016499',
                                   '19c4830d-8714-4e62-b041-0cde12b6de96',
                                   Vector3(0.0, 8.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0),
                                   'diamond_hoe{CustomModelData:101}'
                                   ),
                                  ('Waist',
                                   '41451f74-0acb-4406-a42f-cc90a4a04c9b',
                                   '530b439d-1760-4652-93a7-3320f269358a',
                                   Vector3(0.0, 12.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0),
                                   'diamond_hoe{CustomModelData:102}'
                                   ),
                                  ('Right_Arm',
                                   '11dc3ca9-72b0-41e5-a25e-732749eb5370',
                                   'ad9573a4-361e-417c-8494-bf93c1cf44ef',
                                   Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-4.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-1.0, 0.0, 0.0),
                                   'diamond_hoe{CustomModelData:103}'
                                   ),
                                  ('Right_Elbow',
                                   '2ab7eb3a-be71-4ac8-9c7d-dd2923646c9a',
                                   '1d6e6d29-8aeb-9678-8321-594123d6d035',
                                   Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-1.0, 0.0, 0.0),
                                   'diamond_hoe{CustomModelData:104}'
                                   ),
                                  ('Left_Arm',
                                   'd931c78e-ef11-4f37-92f6-d10a7c595f9c',
                                   'fe0ebeb5-9553-4455-8a78-1759237a1ae1',
                                   Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(4.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0),
                                   'diamond_hoe{CustomModelData:105}'
                                   ),
                                  ('Left_Elbow',
                                   '2ab7eb3a-be71-4ac8-9c7d-dd29d5646c9a',
                                   '1d6e6d29-8aeb-9678-8321-594151d6d035',
                                   Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0),
                                   'diamond_hoe{CustomModelData:106}'
                                   ),
                                  ('Right_Thigh',
                                   '1f4134e3-2608-4d8d-8f10-d687549cb46d',
                                   '2ea57372-4206-428f-9b4c-7c946d247270',
                                   Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-2.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0),
                                   'diamond_hoe{CustomModelData:107}'
                                   ),
                                  ('Right_Knee',
                                   '1f4134e3-2608-4d8d-8f10-d6875123b46d',
                                   '2ea57372-4206-428f-9b4c-7c9461237270',
                                   Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0),
                                   'diamond_hoe{CustomModelData:108}'
                                   ),
                                  ('Left_Thigh',
                                   'dada4315-783e-45d9-990d-418a3284db9a',
                                   '3c49fedd-ad2d-46dc-a3fd-fed469eb6d02',
                                   Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                   Vector3(2.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0),
                                   'diamond_hoe{CustomModelData:109}'
                                   ),
                                  ('Left_Knee',
                                   'dada1235-783e-45d9-990d-418a3284db9a',
                                   '3c49123d-ad2d-46dc-a3fd-fed469eb6d02',
                                   Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0),
                                   'diamond_hoe{CustomModelData:110}'
                                   )
                                  ]
                                 )
    converter.load_file('data/CHARACTER_2.bvh', 2.0)
    converter.globalize_armature('CHARACTER_2', '3888fe0d-41b5-46ad-9740-797228c6c3c3',
                                 [('Neck',
                                   '2f9d6e9a-aaca-1234-9059-ec43f2016499',
                                   '19c4830d-8714-1234-b041-0cde12b6de96',
                                   Vector3(0.0, 8.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0),
                                   'diamond_hoe{CustomModelData:111}'
                                   ),
                                  ('Waist',
                                   '41451f74-0acb-1234-a42f-cc90a4a04c9b',
                                   '530b439d-1760-1234-93a7-3320f269358a',
                                   Vector3(0.0, 12.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0),
                                   'diamond_hoe{CustomModelData:112}'
                                   ),
                                  ('Right_Arm',
                                   '11dc3ca9-72b0-1234-a25e-732749eb5370',
                                   'ad9573a4-361e-1234-8494-bf93c1cf44ef',
                                   Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-4.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-1.0, 0.0, 0.0),
                                   'diamond_hoe{CustomModelData:113}'
                                   ),
                                  ('Right_Elbow',
                                   '2ab7eb3a-be71-1234-9c7d-dd2923646c9a',
                                   '1d6e6d29-8aeb-1234-8321-594123d6d035',
                                   Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-1.0, 0.0, 0.0),
                                   'diamond_hoe{CustomModelData:114}'
                                   ),
                                  ('Left_Arm',
                                   'd931c78e-ef11-1234-92f6-d10a7c595f9c',
                                   'fe0ebeb5-9553-1234-8a78-1759237a1ae1',
                                   Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(4.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0),
                                   'diamond_hoe{CustomModelData:115}'
                                   ),
                                  ('Left_Elbow',
                                   '2ab7eb3a-be71-1234-9c7d-dd29d5646c9a',
                                   '1d6e6d29-8aeb-1234-8321-594151d6d035',
                                   Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0),
                                   'diamond_hoe{CustomModelData:116}'
                                   ),
                                  ('Right_Thigh',
                                   '1f4134e3-2608-1234-8f10-d687549cb46d',
                                   '2ea57372-4206-1234-9b4c-7c946d247270',
                                   Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-2.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0),
                                   'diamond_hoe{CustomModelData:117}'
                                   ),
                                  ('Right_Knee',
                                   '1f4134e3-2608-1234-8f10-d6875123b46d',
                                   '2ea57372-4206-1234-9b4c-7c9461237270',
                                   Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0),
                                   'diamond_hoe{CustomModelData:118}'
                                   ),
                                  ('Left_Thigh',
                                   'dada4315-783e-1234-990d-418a3284db9a',
                                   '3c49fedd-ad2d-1234-a3fd-fed469eb6d02',
                                   Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                   Vector3(2.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0),
                                   'diamond_hoe{CustomModelData:119}'
                                   ),
                                  ('Left_Knee',
                                   'dada1235-783e-1234-990d-418a3284db9a',
                                   '3c49123d-ad2d-1234-a3fd-fed469eb6d02',
                                   Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0),
                                   'diamond_hoe{CustomModelData:120}'
                                   )
                                  ]
                                 )
    converter.reset_function()
    converter.search_function()

    converter = MainConverter('C:/Users/USER/AppData/Roaming/.minecraft/saves/WORLD_NAME'
                              '/datapacks/DATAPACK_NAME/data/animate/functions/FOLDER_NAME2')
    converter.load_file('data/CHARACTER_1_GUITAR.bvh', 0.0)
    converter.globalize_armature('CHARACTER_1_GUITAR', '41451f74-0acb-1234-a42f-cc90a4a04c9b',
                                 [('Guitar',
                                   '2f9d6e9a-7428-4964-9059-ec43f2016499',
                                   '19c4830d-2954-4e62-b041-0cde12b6de96',
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 24.0, 5.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0),
                                   'diamond_hoe{CustomModelData:152}'
                                   )
                                  ]
                                 )

    converter.load_file('data/CHARACTER_2_GUITAR.bvh', 0.0)
    converter.globalize_armature('CHARACTER_2_GUITAR', '41451f74-0acb-4406-a42f-cc90a4a04c9b',
                                 [('Guitar',
                                   '2f9d6e9a-7428-4964-2347-ec43f2016499',
                                   '19c4830d-2954-4e62-2463-0cde12b6de96',
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 24.0, 5.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0),
                                   'diamond_hoe{CustomModelData:151}'
                                   )
                                  ]
                                 )
    converter.reset_function()

    converter.search_function()
