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


"""Helper functions for modifying module configuration."""


import re
import logging


def update_cfg_vars(cfg, mod, key, val):
    """Update variables of module and all submodules."""
    if re.search(mod, cfg["name"]):
        if 'vars' in cfg:
            for var in cfg["vars"]:
                if re.search(key, var):
                    logging.debug("set %s.vars.%s=%s", cfg['name'], var, val)
                    cfg["vars"][var] = val
        else:
            cfg["vars"] = { key: val }
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
