import re


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split('(\d+)', text)]


def merge_dicts(dict1: dict, dict2: dict):
    assert set(dict1.keys()) == set(dict2.keys())
    for key in dict1.keys():
        assert isinstance(dict1[key], list)
        assert isinstance(dict2[key], list)
        dict1[key] += dict2[key]
    return dict1


def flat_nested_dict(dict_to_flat: dict):
    d = {}
    for k, v in dict_to_flat.items():
        if not isinstance(v, dict):
            d[k] = v
        else:
            d.update(flat_nested_dict(v))
    return d


def make_lists_values(d: dict):
    for k, v in d.items():
        if not isinstance(v, list):
            d[k] = [v]
    return d


def init_dict(labels, length):
    return {x: [None] * length for x in labels}
