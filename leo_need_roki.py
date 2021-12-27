from main import MainConverter
from math_objects import Vector3

if __name__ == '__main__':
    converter = MainConverter('C:/Users/Hanmin/AppData/Roaming/.minecraft/saves/Project '
                              'Sekai/datapacks/prsk/data/animate/functions/armor_stand')
    converter.load_file('data/ichika.bvh', 2.0)
    # size, offset, t-pose
    converter.globalize_armature('ichika', '54e5e739-9221-45fc-a06f-b5326d174cf7',
                                 [('Neck',
                                   '2f9d6e9a-aaca-4964-9059-ec43f2016499',
                                   '19c4830d-8714-4e62-b041-0cde12b6de96',
                                   Vector3(0.0, 8.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:101}'
                                   ),
                                  ('Waist',
                                   '41451f74-0acb-4406-a42f-cc90a4a04c9b',
                                   '530b439d-1760-4652-93a7-3320f269358a',
                                   Vector3(0.0, 12.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:102}'
                                   ),
                                  ('Right_Arm',
                                   '11dc3ca9-72b0-41e5-a25e-732749eb5370',
                                   'ad9573a4-361e-417c-8494-bf93c1cf44ef',
                                   Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-4.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:103}'
                                   ),
                                  ('Right_Elbow',
                                   '2ab7eb3a-be71-4ac8-9c7d-dd2923646c9a',
                                   '1d6e6d29-8aeb-9678-8321-594123d6d035',
                                   Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:104}'
                                   ),
                                  ('Left_Arm',
                                   'd931c78e-ef11-4f37-92f6-d10a7c595f9c',
                                   'fe0ebeb5-9553-4455-8a78-1759237a1ae1',
                                   Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(4.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:105}'
                                   ),
                                  ('Left_Elbow',
                                   '2ab7eb3a-be71-4ac8-9c7d-dd29d5646c9a',
                                   '1d6e6d29-8aeb-9678-8321-594151d6d035',
                                   Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:106}'
                                   ),
                                  ('Right_Thigh',
                                   '1f4134e3-2608-4d8d-8f10-d687549cb46d',
                                   '2ea57372-4206-428f-9b4c-7c946d247270',
                                   Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-2.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:107}'
                                   ),
                                  ('Right_Knee',
                                   '1f4134e3-2608-4d8d-8f10-d6875123b46d',
                                   '2ea57372-4206-428f-9b4c-7c9461237270',
                                   Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:108}'
                                   ),
                                  ('Left_Thigh',
                                   'dada4315-783e-45d9-990d-418a3284db9a',
                                   '3c49fedd-ad2d-46dc-a3fd-fed469eb6d02',
                                   Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                   Vector3(2.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:109}'
                                   ),
                                  ('Left_Knee',
                                   'dada1235-783e-45d9-990d-418a3284db9a',
                                   '3c49123d-ad2d-46dc-a3fd-fed469eb6d02',
                                   Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:110}'
                                   )
                                  ]
                                 )
    converter.load_file('data/shiho.bvh', 2.0)
    converter.globalize_armature('shiho', '3888fe0d-41b5-46ad-9740-797228c6c3c3',
                                 [('Neck',
                                   '2f9d6e9a-aaca-1234-9059-ec43f2016499',
                                   '19c4830d-8714-1234-b041-0cde12b6de96',
                                   Vector3(0.0, 8.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:111}'
                                   ),
                                  ('Waist',
                                   '41451f74-0acb-1234-a42f-cc90a4a04c9b',
                                   '530b439d-1760-1234-93a7-3320f269358a',
                                   Vector3(0.0, 12.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:112}'
                                   ),
                                  ('Right_Arm',
                                   '11dc3ca9-72b0-1234-a25e-732749eb5370',
                                   'ad9573a4-361e-1234-8494-bf93c1cf44ef',
                                   Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-4.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:113}'
                                   ),
                                  ('Right_Elbow',
                                   '2ab7eb3a-be71-1234-9c7d-dd2923646c9a',
                                   '1d6e6d29-8aeb-1234-8321-594123d6d035',
                                   Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:114}'
                                   ),
                                  ('Left_Arm',
                                   'd931c78e-ef11-1234-92f6-d10a7c595f9c',
                                   'fe0ebeb5-9553-1234-8a78-1759237a1ae1',
                                   Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(4.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:115}'
                                   ),
                                  ('Left_Elbow',
                                   '2ab7eb3a-be71-1234-9c7d-dd29d5646c9a',
                                   '1d6e6d29-8aeb-1234-8321-594151d6d035',
                                   Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:116}'
                                   ),
                                  ('Right_Thigh',
                                   '1f4134e3-2608-1234-8f10-d687549cb46d',
                                   '2ea57372-4206-1234-9b4c-7c946d247270',
                                   Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-2.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:117}'
                                   ),
                                  ('Right_Knee',
                                   '1f4134e3-2608-1234-8f10-d6875123b46d',
                                   '2ea57372-4206-1234-9b4c-7c9461237270',
                                   Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:118}'
                                   ),
                                  ('Left_Thigh',
                                   'dada4315-783e-1234-990d-418a3284db9a',
                                   '3c49fedd-ad2d-1234-a3fd-fed469eb6d02',
                                   Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                   Vector3(2.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:119}'
                                   ),
                                  ('Left_Knee',
                                   'dada1235-783e-1234-990d-418a3284db9a',
                                   '3c49123d-ad2d-1234-a3fd-fed469eb6d02',
                                   Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:120}'
                                   )
                                  ]
                                 )
    converter.load_file('data/honami.bvh', 2.0)
    converter.globalize_armature('honami', 'b5f2ae0c-ee4a-49c1-a16a-335883c5eb2f',
                                 [('Neck',
                                   '2f9d6e9a-aaca-3456-9059-ec43f2016499',
                                   '19c4830d-8714-3456-b041-0cde12b6de96',
                                   Vector3(0.0, 8.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:121}'
                                   ),
                                  ('Waist',
                                   '41451f74-0acb-3456-a42f-cc90a4a04c9b',
                                   '530b439d-1760-3456-93a7-3320f269358a',
                                   Vector3(0.0, 12.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:122}'
                                   ),
                                  ('Right_Arm',
                                   '11dc3ca9-72b0-3456-a25e-732749eb5370',
                                   'ad9573a4-361e-3456-8494-bf93c1cf44ef',
                                   Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-4.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:123}'
                                   ),
                                  ('Right_Elbow',
                                   '2ab7eb3a-be71-3456-9c7d-dd2923646c9a',
                                   '1d6e6d29-8aeb-3456-8321-594123d6d035',
                                   Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:124}'
                                   ),
                                  ('Right_Wrist',
                                   '2ab7eb3a-be71-8258-9c7d-dd2923646c9a',
                                   '1d6e6d29-8aeb-4394-8321-594123d6d035',
                                   Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:154}'
                                   ),
                                  ('Left_Arm',
                                   'd931c78e-ef11-3456-92f6-d10a7c595f9c',
                                   'fe0ebeb5-9553-3456-8a78-1759237a1ae1',
                                   Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(4.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:125}'
                                   ),
                                  ('Left_Elbow',
                                   '2ab7eb3a-be71-3456-9c7d-dd29d5646c9a',
                                   '1d6e6d29-8aeb-3456-8321-594151d6d035',
                                   Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:126}'
                                   ),
                                  ('Left_Wrist',
                                   '2ab7eb3a-be71-5430-9c7d-dd29d5646c9a',
                                   '1d6e6d29-8aeb-3754-8321-594151d6d035',
                                   Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:154}'
                                   ),
                                  ('Right_Thigh',
                                   '1f4134e3-2608-3456-8f10-d687549cb46d',
                                   '2ea57372-4206-3456-9b4c-7c946d247270',
                                   Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-2.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:127}'
                                   ),
                                  ('Right_Knee',
                                   '1f4134e3-2608-3456-8f10-d6875123b46d',
                                   '2ea57372-4206-3456-9b4c-7c9461237270',
                                   Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:128}'
                                   ),
                                  ('Left_Thigh',
                                   'dada4315-783e-3456-990d-418a3284db9a',
                                   '3c49fedd-ad2d-3456-a3fd-fed469eb6d02',
                                   Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                   Vector3(2.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:129}'
                                   ),
                                  ('Left_Knee',
                                   'dada1235-783e-3456-990d-418a3284db9a',
                                   '3c49123d-ad2d-3456-a3fd-fed469eb6d02',
                                   Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:130}'
                                   )
                                  ]
                                 )
    converter.load_file('data/saki.bvh', 2.0)
    converter.globalize_armature('saki', 'f3560c07-b59e-40ac-a4f6-4e5b868c5839',
                                 [('Neck',
                                   '2f9d6e9a-aaca-4567-9059-ec43f2016499',
                                   '19c4830d-8714-4567-b041-0cde12b6de96',
                                   Vector3(0.0, 8.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:131}'
                                   ),
                                  ('Waist',
                                   '41451f74-0acb-4567-a42f-cc90a4a04c9b',
                                   '530b439d-1760-4567-93a7-3320f269358a',
                                   Vector3(0.0, 12.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:132}'
                                   ),
                                  ('Right_Arm',
                                   '11dc3ca9-72b0-4567-a25e-732749eb5370',
                                   'ad9573a4-361e-4567-8494-bf93c1cf44ef',
                                   Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-4.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:133}'
                                   ),
                                  ('Right_Elbow',
                                   '2ab7eb3a-be71-4567-9c7d-dd2923646c9a',
                                   '1d6e6d29-8aeb-4567-8321-594123d6d035',
                                   Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:134}'
                                   ),
                                  ('Left_Arm',
                                   'd931c78e-ef11-4567-92f6-d10a7c595f9c',
                                   'fe0ebeb5-9553-4567-8a78-1759237a1ae1',
                                   Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(4.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:135}'
                                   ),
                                  ('Left_Elbow',
                                   '2ab7eb3a-be71-4567-9c7d-dd29d5646c9a',
                                   '1d6e6d29-8aeb-4567-8321-594151d6d035',
                                   Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:136}'
                                   ),
                                  ('Right_Thigh',
                                   '1f4134e3-2608-4567-8f10-d687549cb46d',
                                   '2ea57372-4206-4567-9b4c-7c946d247270',
                                   Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-2.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:137}'
                                   ),
                                  ('Right_Knee',
                                   '1f4134e3-2608-4567-8f10-d6875123b46d',
                                   '2ea57372-4206-4567-9b4c-7c9461237270',
                                   Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:138}'
                                   ),
                                  ('Left_Thigh',
                                   'dada4315-783e-4567-990d-418a3284db9a',
                                   '3c49fedd-ad2d-4567-a3fd-fed469eb6d02',
                                   Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                   Vector3(2.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:139}'
                                   ),
                                  ('Left_Knee',
                                   'dada1235-783e-4567-990d-418a3284db9a',
                                   '3c49123d-ad2d-4567-a3fd-fed469eb6d02',
                                   Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:140}'
                                   )
                                  ]
                                 )
    converter.load_file('data/miku.bvh', 2.0)
    converter.globalize_armature('miku', '58eee451-d736-4207-affc-e730d75872fe',
                                 [('Neck',
                                   '2f9d6e9a-7654-4567-9059-ec43f2016499',
                                   '19c4830d-7654-4567-b041-0cde12b6de96',
                                   Vector3(0.0, 8.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:141}'
                                   ),
                                  ('Waist',
                                   '41451f74-7654-4567-a42f-cc90a4a04c9b',
                                   '530b439d-7645-4567-93a7-3320f269358a',
                                   Vector3(0.0, 12.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:142}'
                                   ),
                                  ('Right_Arm',
                                   '11dc3ca9-7645-4567-a25e-732749eb5370',
                                   'ad9573a4-7654-4567-8494-bf93c1cf44ef',
                                   Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-4.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:143}'
                                   ),
                                  ('Right_Elbow',
                                   '2ab7eb3a-7645-4567-9c7d-dd2923646c9a',
                                   '1d6e6d29-7645-4567-8321-594123d6d035',
                                   Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:144}'
                                   ),
                                  ('Left_Arm',
                                   'd931c78e-7645-4567-92f6-d10a7c595f9c',
                                   'fe0ebeb5-7645-4567-8a78-1759237a1ae1',
                                   Vector3(0.0, -5.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(4.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:145}'
                                   ),
                                  ('Left_Elbow',
                                   '2ab7eb3a-7654-4567-9c7d-dd29d5646c9a',
                                   '1d6e6d29-7654-4567-8321-594151d6d035',
                                   Vector3(0.0, -4.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:146}'
                                   ),
                                  ('Right_Thigh',
                                   '1f4134e3-7654-4567-8f10-d687549cb46d',
                                   '2ea57372-7654-4567-9b4c-7c946d247270',
                                   Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                   Vector3(-2.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:147}'
                                   ),
                                  ('Right_Knee',
                                   '1f4134e3-7645-4567-8f10-d6875123b46d',
                                   '2ea57372-7645-4567-9b4c-7c9461237270',
                                   Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:148}'
                                   ),
                                  ('Left_Thigh',
                                   'dada4315-7654-4567-990d-418a3284db9a',
                                   '3c49fedd-7645-4567-a3fd-fed469eb6d02',
                                   Vector3(0.0, -6.5, 0.0).scaled_pixels_to_meter(),
                                   Vector3(2.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:149}'
                                   ),
                                  ('Left_Knee',
                                   'dada1235-7645-4567-990d-418a3284db9a',
                                   '3c49123d-7654-4567-a3fd-fed469eb6d02',
                                   Vector3(0.0, -6.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 0.0, 2.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, -1.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:150}'
                                   )
                                  ]
                                 )
    converter.reset_function('ichika')
    converter.reset_function('shiho')
    converter.reset_function('honami')
    converter.reset_function('saki')
    converter.reset_function('miku')

    converter.search_function('ichika')
    converter.search_function('shiho')
    converter.search_function('honami')
    converter.search_function('saki')
    converter.search_function('miku')

    converter = MainConverter('C:/Users/Hanmin/AppData/Roaming/.minecraft/saves/Project '
                              'Sekai/datapacks/prsk/data/animate/functions/guitar')
    converter.load_file('data/shiho_guitar.bvh', 0.0)
    # size, offset, t-pose
    converter.globalize_armature('shiho_guitar', '41451f74-0acb-1234-a42f-cc90a4a04c9b',
                                 [('Guitar',
                                   '2f9d6e9a-7428-4964-9059-ec43f2016499',
                                   '19c4830d-2954-4e62-b041-0cde12b6de96',
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 24.0, 5.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:152}'
                                   )
                                  ]
                                 )

    converter.load_file('data/ichika_guitar.bvh', 0.0)
    # size, offset, t-pose
    converter.globalize_armature('ichika_guitar', '41451f74-0acb-4406-a42f-cc90a4a04c9b',
                                 [('Guitar',
                                   '2f9d6e9a-7428-4964-2347-ec43f2016499',
                                   '19c4830d-2954-4e62-2463-0cde12b6de96',
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(0.0, 24.0, 5.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:151}'
                                   )
                                  ]
                                 )

    converter.load_file('data/miku_guitar.bvh', 0.0)
    # size, offset, t-pose
    converter.globalize_armature('miku_guitar', '41451f74-7654-4567-a42f-cc90a4a04c9b',
                                 [('Guitar',
                                   '2f9d6e9a-7428-7424-2347-ec43f2016499',
                                   '19c4830d-2954-8543-2463-0cde12b6de96',
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   Vector3(24.0, 5.0, -5.0).scaled_pixels_to_meter(),
                                   Vector3(1.0, 0.0, 0.0).scaled_pixels_to_meter(),
                                   'diamond_hoe{CustomModelData:153}'
                                   )
                                  ]
                                 )
    converter.reset_function('shiho_guitar')
    converter.reset_function('ichika_guitar')
    converter.reset_function('miku_guitar')

    converter.search_function('shiho_guitar')
    converter.search_function('ichika_guitar')
    converter.search_function('miku_guitar')
