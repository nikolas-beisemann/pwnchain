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

"""Definition of a PwnChain module.

A module is a named element of a PwnChain execution tree, which has a command to execute, and
potential submodules, which are run after the command has been executed.
"""


import logging
from threading import Thread
import re
from os import path
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
from base64 import b64decode
from urllib.request import urlopen


class Module:
    """Represents a single module as defined in the config json."""

    def __init__(self, thread_pool=None, cfg=None, var=None, log_handler=None):
        """Set up run environment."""
        if thread_pool is not None:
            self.thread_pool = thread_pool
        else:
            self.thread_pool = []
        if cfg is not None:
            self.cfg = cfg
        if var is not None:
            self.var = var.copy()
        else:
            self.var = {}
        self.log_handler = log_handler
        if "vars" in self.cfg:
            for (key, val) in self.cfg["vars"].items():
                self.var[key] = val
        self.logger = logging.getLogger(self.cfg["name"].format(**self.var))
        if self.log_handler is not None:
            self.logger.addHandler(self.log_handler)
        self.tmp_files = []


    def run(self, save_logfiles):
        """Spawn module in separate thread."""
        thread = Thread(target = self.run_worker, args = (save_logfiles,))
        thread.start()
        self.thread_pool.append(thread)


    def run_worker(self, save_logfiles):
        """Run module."""
        if self.should_not_run():
            return
        self.unpack_files()
        cmd = self.cfg["cmd"].format(**self.var)
        patterns = []
        if "patterns" in self.cfg:
            for pattern_dict in self.cfg["patterns"]:
                log_msg = None
                if "log" in pattern_dict:
                    log_msg = pattern_dict["log"]
                patterns.append({
                    "pattern": re.compile(pattern_dict["pattern"].format(**self.var)),
                    "groups": pattern_dict["groups"],
                    "log": log_msg
                    })
        logfile = None
        if save_logfiles and "logfile" in self.cfg:
            logfile = save_logfiles + path.sep + self.cfg["logfile"].format(**self.var)
        self.logger.debug("var=%s", self.var)
        self.logger.debug("cmd=%s", cmd)

        for line in self.exec_cmd(cmd, logfile):
            for pattern_dict in patterns:
                match = pattern_dict["pattern"].match(line)
                if match:
                    idx = 1
                    for group in pattern_dict["groups"]:
                        self.var[group.format(**self.var)] = match.group(idx)
                        idx += 1
                    if pattern_dict["log"]:
                        self.logger.info(pattern_dict["log"].format(**self.var))
                    self.run_submodules("on_match", save_logfiles)

        self.run_submodules("always", save_logfiles)


    def run_submodules(self, modgroup, save_logfiles):
        """Run submodules within the modgroup list."""
        if "submodules" in self.cfg and modgroup in self.cfg["submodules"]:
            for post_task in self.cfg["submodules"][modgroup]:
                sub_task = Module(self.thread_pool, post_task, self.var, self.log_handler)
                sub_task.run(save_logfiles)


    def should_not_run(self):
        """Check if preconditions for running the module are given."""
        if "enabled" in self.cfg:
            if not self.cfg["enabled"]:
                self.logger.debug("skipping because module is disabled")
                return True
        if "condition" in self.cfg:
            condition = self.cfg["condition"].format(**self.var)
            if eval(condition):
                self.logger.debug("pre-condition '%s' passed", condition)
            else:
                self.logger.debug("skipping because of pre-condition '%s'", condition)
                return True
        return False


    def exec_cmd(self, cmd, logfile):
        """Generator executing a command yielding output."""
        with Popen(cmd.split(), stdout = PIPE, stderr = None, universal_newlines = True,
            bufsize = 1) as proc:
            logfile_fp = None
            if logfile:
                try:
                    logfile_fp = open(logfile, "w")
                except OSError:
                    self.logger.warning("failed to open %s for writing", logfile)
            for line in proc.stdout:
                self.logger.debug(line)
                if logfile_fp:
                    logfile_fp.write(line)
                yield line
            if logfile_fp:
                logfile_fp.close()


    def unpack_files(self):
        """Process the files list."""
        if "files" not in self.cfg:
            return
        for file_dict in self.cfg["files"]:
            self.logger.debug("unpacking %s with type %s", file_dict["name"], file_dict["type"])
            tmp_file = NamedTemporaryFile(buffering = 0)
            self.tmp_files.append(tmp_file)
            self.var[file_dict["name"]] = tmp_file.name
            if file_dict["type"] == "text":
                tmp_file.write(file_dict["content"].encode())
            elif file_dict["type"] == "base64":
                tmp_file.write(b64decode(file_dict["content"]))
            elif file_dict["type"] == "wget":
                tmp_file.write(urlopen(file_dict["content"]).read())


    def wait_until_complete(self):
        """Block until the threadpool is joined."""
        for thread in self.thread_pool:
            thread.join()
        self.thread_pool = []
