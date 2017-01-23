import re
from common_func import check_dict_result
from key_monad import key_monad

EMPTY_REGEX = r"^$"
EMPTY_REGEX_C = re.compile(EMPTY_REGEX)


def validate_for_none_map(current_keymonad):
    list_of_validate_key_path = check_dict_result(
        current_keymonad.result,
        EMPTY_REGEX_C,
        current_keymonad.key_separator)

    return key_monad(
        list_of_validate_key_path,
        current_keymonad.result,
        current_keymonad.key_separator)
