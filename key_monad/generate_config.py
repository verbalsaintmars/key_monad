from .key_monad import key_monad
from .fmap_monad import aggregate_map


def generate_config(config, keys):
    if not isinstance(keys, tuple) and not isinstance(keys, list):
        raise Exception("generate_config's key isn't list/tuple container.")

    def create_monoid(keys, monad=None, root=''):
        for k in keys:
            k = root + k
            if monad:
                monad = aggregate_map(monad)(key_monad(k, config))
            else:
                monad = key_monad(k, config)
        return monad

    monad = create_monoid(keys)
    return monad
