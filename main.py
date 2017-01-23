#! /usr/bin/env python
import argparse
import json
import sys

from key_monad.key_monad import key_monad
from key_monad.generate_config import generate_config
from key_monad.fmap_monad import aggregate_map
from key_monad.fmap_monad import default_root_user_value_map
from key_monad.fmap_monad import remove_nfs_protocol_map
from key_monad.validator_monad import validate_for_none_map

INSTALL_JSON_FILE_1 = "install_json_1.json"
INSTALL_JSON_FILE_2 = "install_json_2.json"

SAMPLE_KEYS = (
    'node_type',
    'install_json/admin_email',
    'install_json/controlplane_ilom',
    'install_json/rootuser')


EXTRA_KEYS = (
    "install_json/seed_ilom",
    "nfs_location")


NONE_KEYS = ("TEST_NONE",)


def get_json(filename):
    with open(filename, 'r') as fd:
        try:
            j = json.load(fd)
            yield j
        except:
            pass


def printout(monad, validate=None):
    """
    if validate is not None:
        not_valid_keys = monad.apply_validate(validate)
    else:
        not_valid_keys = monad.apply_validate()
    """
    keys = monad.key
    absolute_keys = monad.absolute_key
    result = monad.result
    str_json = json.dumps(result, indent=4, sort_keys=True)
    eg = getattr(monad, "eg", None)

    FORMAT = "Example {EG}\n\n" \
        "Keys:\n{KEYS}\n\nAbsolute keys:\n{AKEY}\n\nResult:\n{result}"

    print(FORMAT.format(
        EG=eg, KEYS=keys, result=str_json, AKEY=absolute_keys))


# example 1
def example_1(j1, j2):
    """
    Generate SAMPLE_KEYS key monad.
    Apply default rootuser value to SAMPLE_KEYS key monad.
    Remove nfs:// to SAMPLE_KEYS key monad.
    """
    sample_key_monad = generate_config(j1, SAMPLE_KEYS)
    default_root_valued_monad = default_root_user_value_map(sample_key_monad)
    remove_nfs_url_monad = remove_nfs_protocol_map(default_root_valued_monad)
    final_result = remove_nfs_url_monad
    final_result.eg = 1
    printout(final_result)


# example 2
def example_2(j1, j2):
    """
    Create SAMPLE_KEYS monad.
    Create EXTRA_KEYS monad.
    Aggregate both and apply default root value, remove nfs protocol.
    """
    sample_key_monad = generate_config(j1, SAMPLE_KEYS)
    seed_ilom_monad_from_another_json = generate_config(j2, EXTRA_KEYS)
    aggregate_monad = aggregate_map(sample_key_monad)(
        seed_ilom_monad_from_another_json)
    default_root_valued_monad = default_root_user_value_map(aggregate_monad)
    remove_nfs_url_monad = remove_nfs_protocol_map(default_root_valued_monad)
    final_result = remove_nfs_url_monad
    final_result.eg = 2
    printout(final_result)


# example 3
def example_3(j1, j2):
    """
    Validate for none.
    """
    none_key_monad_1 = generate_config(j1, SAMPLE_KEYS)
    none_key_monad_2 = generate_config(j1, NONE_KEYS)
    aggregate_monad = aggregate_map(none_key_monad_1)(none_key_monad_2)
    invalid_key_monad = validate_for_none_map(aggregate_monad)
    final_result = invalid_key_monad
    final_result.eg = 3
    printout(final_result)


# example 4
def example_4(j1, j2):
    """
    Apply default root to single key_monad.
    Apply nfs removale to single key_monad.
    Aggregate both.
    Create a single key_monad from another json file.
    Aggregate above 3.
    Apply validate for none on the final monad.
    """
    root_user = key_monad("rootuser", j1)
    rooted_monad = default_root_user_value_map(root_user)
    nfs_location = key_monad("nfs_location", j1)
    nfs_no_proc_monad = remove_nfs_protocol_map(nfs_location)

    monad_2 = aggregate_map(nfs_no_proc_monad)(rooted_monad)

    seed_ilom = key_monad('install_json/seed_ilom', j2)
    monad_3 = aggregate_map(seed_ilom)(monad_2)

    invalid_key_monad = validate_for_none_map(monad_3)

    final_result = monad_3
    final_result.eg = 4
    printout(final_result)

    final_result = invalid_key_monad
    final_result.eg = 4
    printout(final_result)


def opt_parser():
    parser = argparse.ArgumentParser(
        description='{0} argument parser'.format(sys.argv[0]),
        epilog="monad example script.")

    parser.add_argument('-eg', metavar='example number', type=int,
                        default=1,
                        dest='eg',
                        help='example number to run')
    global argument
    argument = parser.parse_args()


if __name__ == "__main__":
    opt_parser()
    j1 = next(get_json(INSTALL_JSON_FILE_1))
    j2 = next(get_json(INSTALL_JSON_FILE_2))
    examples = {1: example_1,
                2: example_2,
                3: example_3,
                4: example_4}[argument.eg](j1, j2)
