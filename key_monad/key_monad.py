import collections
import uuid

from common_func import get_dict_obj


class key_monad(object):
    """
    Context is immutable.
    No side-effect.
    """

    """
    CACHE supports multiple config dict.
    """
    CACHE = {"dummy": ({1: None}, {})}

    def __init__(self, key, config, separator=r"/"):
        """
        :key: config key string tuple or single key string
        :config: json config
        """
        def check_config_existence():
            for k, v in self.CACHE.iteritems():
                if v[0] == config:
                    return k

            r_key = uuid.uuid4()
            self.CACHE[r_key] = (config, {})
            return r_key

        _cache_key = check_config_existence()

        if isinstance(key, collections.Iterable) and \
                not isinstance(key, basestring):
            self.__absolute_key = key
        else:
            self.__absolute_key = [key]

        self.__config = self.CACHE[_cache_key][0]
        self.__result = {}
        self.__key_separator = separator

        def assign(k):
            key = k.split(self.key_separator)[-1]
            if key == "":
                self.__result = self.__config
            else:
                self.__result[key] = self.CACHE[_cache_key][1].get(
                    k, self.__get_dict_obj(k, self.key_separator))
                self.CACHE[_cache_key][1][k] = self.__result[key]

        for k in iter(self.__absolute_key):
            assign(k)

    def __get_dict_obj(self, key, separator):
        return get_dict_obj(self.__config, key, separator=separator)

    @property
    def key_separator(self):
        return self.__key_separator

    @property
    def absolute_key(self):
        return self.__absolute_key

    @property
    def key(self):
        return self.result.keys()

    @property
    def result(self):
        return self.__result
