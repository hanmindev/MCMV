from typing import Optional


def tuple_to_m_list(tup: tuple, c: str = '') -> str:
    """Return a string representation of a tuple to be used as an NBT list in Minecraft."""
    if type(tup[0]) is float:
        return '[' + ', '.join(tuple('{:f}'.format(i) + c for i in tup)) + ']'
    else:
        return '[' + ', '.join(tuple(str(i) + c for i in tup)) + ']'


def uuid_str_to_uuid_nbt(uuid: str) -> str:
    """Return a string representation of a integer list UUID-format converted from a normal UUID format."""
    split_uuid = uuid.split('-')
    a = split_uuid[0]
    b = split_uuid[1] + split_uuid[2]
    c = split_uuid[3] + split_uuid[4][0:4]
    d = split_uuid[4][4:16]
    uuids = tuple(str((int(i, 16) + 2147483648) % 4294967296 - 2147483648) for i in (a, b, c, d))
    return 'UUID:[I;' + ','.join(uuids) + ']'


def get_function_directory(directory: str, file: Optional[str]) -> str:
    """Return a function directory  from the directory and file that Minecraft uses to look up functions."""
    directory_list = directory.split('/')
    if directory_list[-1] == '':
        directory_list.pop()

    for i in range(len(directory_list)):
        if directory_list[i] == 'data':
            if directory_list[i - 2] == 'datapacks' and directory_list[i + 2] == 'functions':
                datapack_name = directory_list[i + 1]
                datapack_directory = directory_list[i + 3:len(directory_list)]
                datapack_directory.append('')
                return datapack_name + ':' + '/'.join(datapack_directory) + file
    print('This doesn\'t seem to be a valid path!')
    quit()
