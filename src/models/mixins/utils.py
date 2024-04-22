def type_checker(item: dict, keys: list):
    for (key, data_type) in keys:
        if not key in item:
            raise AttributeError
        if not type(item[key]) is data_type:
            raise AttributeError