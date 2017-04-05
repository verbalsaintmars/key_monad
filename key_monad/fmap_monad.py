import copy
import re

from .common_func import modify_dict_result
from .common_func import remove_root_duplicate
from .key_monad import key_monad

NFS_REGEX = r"^nfs://"
NFS_REGEX_C = re.compile(NFS_REGEX, flags=re.IGNORECASE)
NO_NFS_REGEX = r"^(?!nfs://).*$"
NO_NFS_REGEX_C = re.compile(NO_NFS_REGEX, flags=re.IGNORECASE)
EMPTY_REGEX = r"^$"
EMPTY_REGEX_C = re.compile(EMPTY_REGEX)


def __add_nfs_protocal(matchgroup):
    return "nfs://" + matchgroup.group(0)


def aggregate_map(current_keymonad):
    def aggregate(assigned_keymonad):
        final_result = copy.deepcopy(current_keymonad.result)
        final_result.update(assigned_keymonad.result)
        aggregate_keys = list(
            set(current_keymonad.absolute_key +
                assigned_keymonad.absolute_key))
        return key_monad(aggregate_keys,
                         final_result,
                         current_keymonad.key_separator)
    return aggregate


def default_root_user_value_map(current_keymonad):
    ROOTUSER_KEYS = ("rootuser",)
    modified_result = modify_dict_result(
        current_keymonad.result,
        ROOTUSER_KEYS,
        EMPTY_REGEX_C,
        r"/root/root")
    return key_monad(
        current_keymonad.absolute_key,
        modified_result,
        current_keymonad.key_separator)


def remove_nfs_protocol_map(current_keymonad):
    CHECK_NFS_KEYS = ("nfs_location", "uri")
    modified_result = modify_dict_result(
        current_keymonad.result,
        CHECK_NFS_KEYS,
        NFS_REGEX_C,
        "")
    return key_monad(
        current_keymonad.absolute_key,
        modified_result,
        current_keymonad.key_separator)


def add_nfs_protocol_map(current_keymonad):
    CHECK_NFS_KEYS = ("nfs_location", "uri")
    modified_result = modify_dict_result(
        current_keymonad.result,
        CHECK_NFS_KEYS,
        NO_NFS_REGEX_C,
        __add_nfs_protocal)
    return key_monad(
        current_keymonad.absolute_key,
        modified_result,
        current_keymonad.key_separator)


def default_site_type_map(current_keymonad):
    """ Setup default site_type to 'dev' """
    SITE_TYPE_KEYS = ("site_type",)
    modified_result = modify_dict_result(
        current_keymonad.result,
        SITE_TYPE_KEYS,
        EMPTY_REGEX_C,
        r"prod")
    return key_monad(
        current_keymonad.absolute_key,
        modified_result,
        current_keymonad.key_separator)


def remove_duplicate_entry_map(current_keymonad):
    modified_result = remove_root_duplicate(
        current_keymonad.result)
    return key_monad(
        current_keymonad.absolute_key,
        modified_result,
        current_keymonad.key_separator)
