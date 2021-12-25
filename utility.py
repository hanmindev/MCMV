def tuple_to_m_list(tup: tuple, c: str = '') -> str:
    if type(tup[0]) is float:
        return '[' + ', '.join(tuple('{:f}'.format(i) + c for i in tup)) + ']'
    else:
        return '[' + ', '.join(tuple(str(i) + c for i in tup)) + ']'


def uuid_str_to_uuid_nbt(uuid: str) -> str:
    split_uuid = uuid.split('-')
    a = split_uuid[0]
    b = split_uuid[1] + split_uuid[2]
    c = split_uuid[3] + split_uuid[4][0:4]
    d = split_uuid[4][4:16]
    uuids = tuple(str((int(i, 16) + 2147483648) % 4294967296 - 2147483648) for i in (a, b, c, d))
    return 'UUID:[I;'+','.join(uuids)+']'
