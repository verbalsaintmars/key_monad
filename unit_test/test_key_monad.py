#!/bin/env python
import unittest
from compute.lib.key_monad.fmap_monad import aggregate_map
from compute.lib.key_monad.fmap_monad import default_root_user_value_map
from compute.lib.key_monad.fmap_monad import remove_nfs_protocol_map
from compute.lib.key_monad.generate_config import generate_config
from compute.lib.key_monad.key_monad import key_monad
from compute.lib.key_monad.validator_monad import validate_for_none_map


INSTALL_JSON_1_DICT = {
    "key_1": "key1",
    "nfs_location": "nfs://URL",
    "SUBKEY": {
        "sub_key_1": "subkey1",
        "nfs_location": "nfs://URL"
    },
    "rootuser": None
}

INSTALL_JSON_2_DICT = {
    "key_2": "key2",
    "nfs_location": "nfs://URL",
    "install_json": {
        "AmIEmpty": ""},
    "SUBKEY": {
        "sub_key_2": "subkey2",
        "nfs_location": "nfs://URL",
        "SUBKEY_LAYER_2": {
            "SUBKEY_LAYER_3": {
                "SUBKEY_LAYER_4": {
                    "key_2_nested_1": "key_2_nested_1",
                    "key_2_nested_2": "",
                }
            }
        }
    }
}


class TestKeyMonadV2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.json_dict_1 = INSTALL_JSON_1_DICT
        cls.json_dict_2 = INSTALL_JSON_2_DICT

    def test_generate_config(self):
        keys_from_json_dict_1 = (
            "key_1",
            "nfs_location",
            "SUBKEY",
            "SUBKEY/sub_key_1")
        key_monad_1 = generate_config(self.json_dict_1, keys_from_json_dict_1)
        keys = key_monad_1.key
        absolute_keys = key_monad_1.absolute_key
        result = key_monad_1.result
        expect_keys = set(['sub_key_1', 'key_1', 'SUBKEY', 'nfs_location'])
        expect_absolute_keys = \
            set(['SUBKEY/sub_key_1', 'nfs_location', 'key_1', 'SUBKEY'])
        expect_result = \
            {'sub_key_1': 'subkey1',
             'key_1': 'key1',
             'SUBKEY': {'sub_key_1': 'subkey1',
                        'nfs_location': 'nfs://URL'},
             'nfs_location': 'nfs://URL'}
        self.assertTrue(expect_keys == set(keys))
        self.assertTrue(expect_absolute_keys == set(absolute_keys))
        self.assertTrue(expect_result == result)

    def test_aggregate_key_monad(self):
        keys_from_json_dict_1 = (
            "key_1",
            "nfs_location",
            "SUBKEY/sub_key_1")

        keys_from_json_dict_2 = (
            "key_2",
            "SUBKEY/sub_key_2",
            "SUBKEY/SUBKEY_LAYER_2/SUBKEY_LAYER_3/"
            "SUBKEY_LAYER_4/key_2_nested_1")

        key_monad_1 = generate_config(self.json_dict_1, keys_from_json_dict_1)
        key_monad_2 = generate_config(self.json_dict_2, keys_from_json_dict_2)
        aggregate_monad = aggregate_map(key_monad_1)(key_monad_2)
        keys = aggregate_monad.key
        absolute_keys = aggregate_monad.absolute_key
        result = aggregate_monad.result
        expect_keys = set(['key_2_nested_1',
                           'nfs_location',
                           'sub_key_2',
                           'sub_key_1',
                           'key_1',
                           'key_2'])
        expect_absolute_keys = \
            set(['SUBKEY/sub_key_1',
                 'SUBKEY/sub_key_2',
                 'SUBKEY/SUBKEY_LAYER_2/SUBKEY_LAYER_3/'
                 'SUBKEY_LAYER_4/key_2_nested_1',
                 'nfs_location',
                 'key_1',
                 'key_2'])

        expect_result = \
            {'key_2_nested_1': 'key_2_nested_1',
             'nfs_location': 'nfs://URL',
             'sub_key_2': 'subkey2',
             'sub_key_1': 'subkey1',
             'key_1': 'key1',
             'key_2': 'key2'}

        self.assertTrue(expect_keys == set(keys))
        self.assertTrue(expect_absolute_keys == set(absolute_keys))
        self.assertTrue(expect_result == result)

    def test_aggregate_single_key_monad(self):
        key_monad_1 = key_monad("nfs_location", self.json_dict_1)
        key_monad_2 = key_monad("key_2", self.json_dict_2)
        aggregate_monad = aggregate_map(key_monad_1)(key_monad_2)
        keys = aggregate_monad.key
        absolute_keys = aggregate_monad.absolute_key
        result = aggregate_monad.result
        expect_keys = set(['nfs_location',
                           'key_2'])
        expect_absolute_keys = \
            set(['nfs_location',
                 'key_2'])

        expect_result = \
            {'nfs_location': 'nfs://URL',
             'key_2': 'key2'}

        self.assertTrue(expect_keys == set(keys))
        self.assertTrue(expect_absolute_keys == set(absolute_keys))
        self.assertTrue(expect_result == result)

    def test_default_root_user_value_map(self):
        key_monad_1 = key_monad("rootuser", self.json_dict_1)
        default_root_valued_monad = \
            default_root_user_value_map(key_monad_1)
        keys = default_root_valued_monad.key
        absolute_keys = default_root_valued_monad.absolute_key
        result = default_root_valued_monad.result
        expect_keys = set(['rootuser'])

        expect_absolute_keys = set(['rootuser'])

        # the rootuser has a default value, i.e: PICACHO
        expect_result = {'rootuser': 'PICACHO'}

        self.assertTrue(expect_keys == set(keys))
        self.assertTrue(expect_absolute_keys == set(absolute_keys))
        self.assertTrue(expect_result == result)

    def test_remove_nfs_protocol_map(self):
        key_monad_1 = remove_nfs_protocol_map(
            key_monad("nfs_location", self.json_dict_1))
        keys = key_monad_1.key
        absolute_keys = key_monad_1.absolute_key
        result = key_monad_1.result
        expect_keys = set(['nfs_location'])

        expect_absolute_keys = set(['nfs_location'])

        # the nfs_location has a "nfs://" removed.
        expect_result = {'nfs_location': 'URL'}

        self.assertTrue(expect_keys == set(keys))
        self.assertTrue(expect_absolute_keys == set(absolute_keys))
        self.assertTrue(expect_result == result)

    def test_validate_for_none_map(self):
        key_monad_1 = key_monad("/", self.json_dict_1)
        key_monad_2 = key_monad("/", self.json_dict_2)
        aggregate_monad = aggregate_map(key_monad_1)(key_monad_2)
        validated_monad = validate_for_none_map(aggregate_monad)

        keys = validated_monad.key
        absolute_keys = validated_monad.absolute_key
        result = validated_monad.result

        expect_keys = set(['rootuser', 'AmIEmpty', 'key_2_nested_2'])
        expect_absolute_keys = \
            set(['rootuser',
                 'install_json/AmIEmpty',
                 'SUBKEY/SUBKEY_LAYER_2/SUBKEY_LAYER_3/'
                 'SUBKEY_LAYER_4/key_2_nested_2'])

        # Those keys are empty or None
        expect_result = \
            {'rootuser': None, 'AmIEmpty': '', 'key_2_nested_2': ''}

        self.assertTrue(expect_keys == set(keys))
        self.assertTrue(expect_absolute_keys == set(absolute_keys))
        self.assertTrue(expect_result == result)
