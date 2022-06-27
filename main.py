# this is for testing

from import_file import BvhFileLoader

file_loader = BvhFileLoader('data/nikkori/nene.bvh', 2.0, 'xyz')

model = file_loader.get_model()
animation = file_loader.get_animation()

