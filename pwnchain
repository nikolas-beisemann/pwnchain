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

"""PwnChain is a tool for cascading different tools in an automated fashion."""

import logging
import re
from argparse import ArgumentParser, RawTextHelpFormatter
import json
from sys import stdin
from pwnchain_module import Module


VERSION = "0.2.0"


def update_cfg_vars(cfg, mod, key, val):
    """Update variables of module and all submodules."""
    if re.search(mod, cfg["name"]):
        for var in cfg["vars"]:
            if re.search(key, var):
                logging.debug("set %s.vars.%s=%s", cfg['name'], var, val)
                cfg["vars"][var] = val
    if "submodules" in cfg:
        for subtype in [ "on_match", "always" ]:
            if subtype in cfg["submodules"]:
                for subcfg in cfg["submodules"][subtype]:
                    update_cfg_vars(subcfg, mod, key, val)


def update_cfg_enabled(cfg, mod, enabled):
    """Update enabled state of module and all submodules."""
    if re.search(mod, cfg["name"]):
        cfg["enabled"] = enabled
        logging.debug("set %s.enabled=%s", cfg['name'], enabled)
    if "submodules" in cfg:
        for subtype in [ "on_match", "always" ]:
            if subtype in cfg["submodules"]:
                for subcfg in cfg["submodules"][subtype]:
                    update_cfg_enabled(subcfg, mod, enabled)


if __name__ == '__main__':
    parser = ArgumentParser(formatter_class = RawTextHelpFormatter)
    parser.add_argument("--version", action = "version", version = VERSION)
    with open("LICENSE") as fp:
        parser.add_argument("--show-license", action = "version", version = fp.read(),
            help = "show program's license details and exit")
    parser.add_argument("-v", "--verbose", action = "store_true",
        help = "print debug log messages")
    parser.add_argument("-o", "--save-logfiles", metavar = "directory",
        help = "save the output of each command to a given directory")
    parser.add_argument("-s", "--set-var", action = "append", metavar = "module:key:val",
        help = "override a module variable specified within the configuration")
    parser.add_argument("--enable-mod", action = "append", metavar="module",
        help = "enable a module which is marked enabled=False in the configuration")
    parser.add_argument("--disable-mod", action = "append", metavar="module",
        help = "disable a module which is marked enabled=True in the configuration")
    parser.add_argument("cfg", nargs = '?', help = ".json configuration file")

    args = parser.parse_args()

    print(f"""==========================================================================
= PwnChain v{VERSION}                                                        =
==========================================================================
= Copyright (C) 2021 Nikolas Beisemann <nikolas@disroot.org>.            =
= This program comes with ABSOLUTELY NO WARRANTY; for details use        =
= '--show-license'.                                                      =
= This is free software, and you are welcome to redistribute it under    =
= certain conditions; use '--show-license' for details.                  =
==========================================================================
    """)

    if args.verbose:
        logging.basicConfig(level = logging.DEBUG)
        logging.debug("verbose tracing enabled")
    else:
        logging.basicConfig(level = logging.INFO)

    cfg_data = stdin
    if args.cfg:
        cfg_data = open(args.cfg)
    json_cfg = json.load(cfg_data)
    logging.debug("config %s read", json_cfg)

    if args.set_var:
        for entry in args.set_var:
            (e_mod, e_key, e_val) = entry.split(':')
            logging.debug("trying to override variable '%s=%s' in '%sq'", e_key, e_val, e_mod)
            update_cfg_vars(json_cfg, e_mod, e_key, e_val)
    if args.enable_mod:
        for entry in args.enable_mod:
            update_cfg_enabled(json_cfg, entry, True)
    if args.disable_mod:
        for entry in args.disable_mod:
            update_cfg_enabled(json_cfg, entry, False)

    task = Module(cfg=json_cfg)
    task.run(args.save_logfiles)
    task.wait_until_complete()
