from key_monad import key_monad
from fmap_monad import aggregate_map


def generate_config(config, keys):
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
