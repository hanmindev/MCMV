def tuple_to_m_list(tup, chr):
    return '[' + ', '.join(tuple(i + chr for i in map(str, tup))) + ']'
