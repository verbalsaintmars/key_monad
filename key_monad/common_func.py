import copy
import json
import os


def get_dict_obj(config, key, create=False, separator='/'):
    current = config

    for next in key.split(separator):
        if not next:
            continue
        elif next[0] != "_" and hasattr(current, next):
            current = getattr(current, next)
        elif isinstance(current, dict) and \
                dict.__contains__(current, next):
            current = current[next]
        elif create:
            newdict = {}
            current[next] = newdict
            current = newdict
        else:
            root_key_inspect = key.split(separator)[-1]
            if root_key_inspect in config:
                return config[root_key_inspect]
            return None
    return current


def createJsonFile(contents_dict, contents_file, read_only=True, pretty=False):
    try:
        if os.path.exists(contents_file):
            os.chmod(contents_file, 0777)

        out_file = open(contents_file, 'w')

        if pretty:
            str_json = json.dumps(contents_dict, indent=4, sort_keys=True)
        else:
            str_json = json.dumps(contents_dict)

        out_file.write(str_json)
        out_file.close()
        if read_only:
            os.chmod(contents_file, 0400)

    except Exception:
        raise

    return contents_file


def modify_dict_result(result, keys, regex_c, replace_value):
    """
    copy-on-write(COW): if there're keys match, deep copy the dict and modify.
    :return: modified result or src result
    """
    cow_result = {}
    key_path_queue = []

    def find_replace(value):
        if value is None:
            value = ""
        if not isinstance(value, basestring):
            return
        if regex_c.search(value):
            return regex_c.sub(replace_value, value)

    def extract_value(result):
        def extract(key):
            return find_replace(result[key])
        return extract

    def assign(c_result):
        def act_assign(t):
            c_result[t[0]] = t[1]
        return act_assign

    def current_layer_check(current_result):
        key_list = filter(lambda k: k in keys, current_result)
        modified_value_key = \
            zip(key_list, map(extract_value(current_result), key_list))

        if filter(lambda t: t[1], modified_value_key):
            if not cow_result:
                cow_result.update(copy.copy(result))

            key_path_index = 0
            c_result = cow_result

            while key_path_index < len(key_path_queue):
                c_result = c_result[key_path_queue[key_path_index]]
                key_path_index += 1

            map(assign(c_result), modified_value_key)

    def loop_dict(inner_result):
        current_layer_check(inner_result)

        for k, v in inner_result.iteritems():
            if isinstance(inner_result[k], dict):
                key_path_queue.append(k)
                loop_dict(inner_result[k])
                key_path_queue.pop()

    loop_dict(result)
    return cow_result if cow_result else result


def check_dict_result(result, regex_c, sep=r"/"):
    """
    :return: list of keys not valid.
    """
    def find_value(value):
        if value is None:
            value = ""
        if not isinstance(value, basestring):
            return
        if regex_c.match(value):
            return True
        return False

    def extract_value(result):
        def extract(key):
            return find_value(result[key])
        return extract

    def current_layer_check(current_result, keypath):
        key_list = current_result.keys()

        checked_value_key = \
            zip(key_list, map(extract_value(current_result), key_list))

        value_match_key_value = filter(lambda t: t[1], checked_value_key)
        match_key_path_list = []

        for k, _ in value_match_key_value:
            match_key_path = (sep).join((keypath, k))
            match_key_path_list.append(
                match_key_path[1:] if match_key_path[0] == sep else
                match_key_path)

        return match_key_path_list

    def loop_dict(inner_result, keypath, match_key_path_list):
        match_key_path_list.extend(
            current_layer_check(inner_result, keypath))
        for k, v in inner_result.iteritems():
            if isinstance(inner_result[k], dict):
                loop_dict(
                    inner_result[k],
                    (sep).join((keypath, k)),
                    match_key_path_list)

    match_key_path_list = []
    loop_dict(result, "", match_key_path_list)
    return match_key_path_list