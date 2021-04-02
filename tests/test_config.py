#!/usr/bin/env python3
#
# PwnChain - Cascading different tools in automated fashion.
# Copyright (C) 2021 Nikolas Beisemann <nikolas@disroot.org>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import unittest
import pwnchain.config


class TestConfig(unittest.TestCase):
    """Unit tests for PwnChain configuration helpers."""


    def setUp(self):
        self.cfg = {
            "name": "unittest",
            "cmd": "echo {var1}",
            "vars": { "var1": "foo" },
            "patterns": [{ "pattern": "(fo)o", "groups": ["var2"], "log": "{var2}" }],
            "submodules": {
                "on_match": [{
                    "name": "on-match",
                    "cmd": "echo {var2}"
                }],
                "always": [{
                    "name": "always",
                    "cmd": "echo {var2}{var3}",
                    "vars": { "var3": 42 },
                    "patterns": [{
                        "pattern": "(fo[0-9])[0-9]",
                        "groups": ["var4"],
                        "log": "{var4}"
                    }]
                }]
            }
        }


    def test_update_cfg_vars(self):
        pwnchain.config.update_cfg_vars(self.cfg, 'unit', 'var', 'bar')
        self.assertEqual(self.cfg['vars']['var1'], 'bar')
        self.assertFalse('vars' in self.cfg['submodules']['on_match'][0])
        self.assertEqual(self.cfg['submodules']['always'][0]['vars']['var3'], 42)

        pwnchain.config.update_cfg_vars(self.cfg, 'match', 'newvar', 'val')
        self.assertFalse('newvar' in self.cfg['vars'])
        self.assertEqual(self.cfg['submodules']['on_match'][0]['vars']['newvar'], 'val')
        self.assertFalse('newvar' in self.cfg['submodules']['always'][0]['vars'])

        pwnchain.config.update_cfg_vars(self.cfg, 'always', 'v', 'nowstring')
        self.assertEqual(self.cfg['vars']['var1'], 'bar')
        self.assertFalse('v' in self.cfg['vars'])
        self.assertFalse('v' in self.cfg['submodules']['on_match'][0]['vars'])
        self.assertEqual(self.cfg['submodules']['always'][0]['vars']['var3'], 'nowstring')
        self.assertFalse('v' in self.cfg['submodules']['always'][0]['vars'])


    def test_update_cfg_enabled(self):
        pwnchain.config.update_cfg_enabled(self.cfg, 'test', True)
        self.assertEqual(self.cfg['enabled'], True)
        self.assertFalse('enabled' in self.cfg['submodules']['on_match'][0])
        self.assertFalse('enabled' in self.cfg['submodules']['always'][0])

        pwnchain.config.update_cfg_enabled(self.cfg, 'match', False)
        self.assertEqual(self.cfg['enabled'], True)
        self.assertEqual(self.cfg['submodules']['on_match'][0]['enabled'], False)
        self.assertFalse('enabled' in self.cfg['submodules']['always'][0])

        pwnchain.config.update_cfg_enabled(self.cfg, 'always', True)
        self.assertEqual(self.cfg['enabled'], True)
        self.assertEqual(self.cfg['submodules']['on_match'][0]['enabled'], False)
        self.assertEqual(self.cfg['submodules']['always'][0]['enabled'], True)
