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


import logging
from tempfile import NamedTemporaryFile
import unittest
from io import StringIO
from pwnchain.module import Module


class TestModule(unittest.TestCase):
    """Unit tests for PwnChain modules."""


    def setUp(self):
        """Creating a module test module."""
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
            },
            "files": [
                {
                    "name": "file1",
                    "type": "text",
                    "content": "some text\non two lines\n"
                },
                {
                    "name": "file2",
                    "type": "base64",
                    "content": "c29tZSB0ZXh0Cm9uIHR3byBsaW5lcwo="
                }
            ]
        }
        logging.basicConfig(level=logging.INFO)
        self.log = StringIO()
        log_handler = logging.StreamHandler(self.log)
        log_handler.setLevel(logging.INFO)
        self.mod = Module(cfg=self.cfg, log_handler=log_handler)
        self.tmp = NamedTemporaryFile(buffering=0)


    def tearDown(self):
        """Joining spawned threads after test run."""
        self.mod.wait_until_complete()


    def test_exec_cmd(self):
        """Testing the exec_cmd method."""
        for line in self.mod.exec_cmd('echo foo', self.tmp.name):
            self.assertEqual(line, 'foo\n')
        tmp_file = open(self.tmp.name, 'rb')
        self.assertEqual(tmp_file.read(), b'foo\n')
        tmp_file.close()


    def test_unpack_files(self):
        """Testing the unpack_files method."""
        self.assertFalse('file1' in self.mod.var)
        self.assertFalse('file2' in self.mod.var)
        self.mod.unpack_files()
        self.assertTrue('file1' in self.mod.var)
        self.assertTrue('file2' in self.mod.var)
        for k in range(2):
            tmp_file = open(self.mod.var[f'file{k+1}'], 'rb')
            self.assertEqual(tmp_file.read().decode(), self.cfg['files'][0]['content'])
            tmp_file.close()


    def test_should_not_run(self):
        """Testing the should_not_run method."""
        self.assertFalse(self.mod.should_not_run())
        self.mod.cfg['enabled'] = True
        self.assertFalse(self.mod.should_not_run())
        self.mod.cfg['enabled'] = False
        self.assertTrue(self.mod.should_not_run())
        self.mod.cfg['enabled'] = True
        self.mod.cfg['condition'] = 'True'
        self.assertFalse(self.mod.should_not_run())
        self.mod.cfg['condition'] = 'False'
        self.assertTrue(self.mod.should_not_run())


    def test_run(self):
        """Testing the run method."""
        self.mod.run(False)
        self.mod.wait_until_complete()
        self.log.flush()
        self.assertEqual(self.log.getvalue(), 'fo\nfo4\n')


if __name__ == '__main__':
    unittest.main()
