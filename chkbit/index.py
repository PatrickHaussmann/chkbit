import fnmatch
import os
import subprocess
import sys
import json
from enum import Enum
import time
from chkbit import hashfile, hashtext

VERSION = 3  # index version
INDEX = ".chkbit"
IGNORE = ".chkbitignore"


class Stat(Enum):
    ERR_DMG = "DMG"
    ERR_BITROT = "DMG"  # legacy
    ERR_IDX = "EIX"
    WARN_OLD = "old"
    NEW = "new"
    UPDATE = "upd"
    OK = "ok "
    SKIP = "skp"
    INTERNALEXCEPTION = "EXC"
    FLAG_MOD = "fmod"


class Index:
    def __init__(self, path, files, *, log=None):
        self.path = path
        self.files = files
        self.old = {}
        self.new = {}
        self.ignore = []
        self.load_ignore()
        self.updates = []
        self.modified = True
        self.log = log

    @property
    def ignore_file(self):
        return os.path.join(self.path, IGNORE)

    @property
    def idx_file(self):
        return os.path.join(self.path, INDEX)

    def should_ignore(self, name):
        for ignore in self.ignore:
            if fnmatch.fnmatch(name, ignore):
                return True
        return False

    def _setmod(self):
        self.modified = True

    def _log(self, stat, name):
        if self.log:
            self.log(stat, os.path.join(self.path, name))

    # calc new hashes for this index
    def update(self, context):
        for name in self.files:
            if context.only_new and name in self.old:
                continue
            if self.should_ignore(name):
                self._log(Stat.SKIP, name)
                continue
            
            self.new[name] = self._calc_file(name)

    # check/update the index (old vs new)
    def check_fix(self, force):
        for name in self.new.keys():
            if not name in self.old:
                self._log(Stat.NEW, name)
                self._setmod()
                continue

            a = self.old[name]
            b = self.new[name]
            amod = a["mtime"]
            bmod = b["mtime"]
            if a["hash"] == b["hash"]:
                # ok, if the content stays the same the mod time does not matter
                self._log(Stat.OK, name)
                if amod != bmod:
                    self._setmod()
                continue

            if amod == bmod:
                # damage detected
                self._log(Stat.ERR_DMG, name)
                # replace with old so we don't loose the information on the next run
                # unless force is set
                if not force:
                    self.new[name] = a
                else:
                    self._setmod()
            elif amod < bmod:
                # ok, the file was updated
                self._log(Stat.UPDATE, name)
                self._setmod()
            elif amod > bmod:
                self._log(Stat.WARN_OLD, name)
                self._setmod()

    def _calc_file(self, name):
        path = os.path.join(self.path, name)
        info = os.stat(path)
        mtime = int(info.st_mtime * 1000)
        return {"mtime": mtime, "hash": hashfile(path)}

    def save(self):
        if self.modified:
            data = {"v": VERSION, "files": self.new, "mtime": int(time.time() * 1000)}
            text = json.dumps(self.new, separators=(",", ":"))
            data["files_hash"] = hashtext(text)

            with open(self.idx_file, "w", encoding="utf-8") as f:
                json.dump(data, f, separators=(",", ":"), indent=4)
            self.modified = False
            return True
        else:
            return False

    def load(self):
        if not os.path.exists(self.idx_file):
            return False
        self.modified = False
        with open(self.idx_file, "r", encoding="utf-8") as f:
            data = json.load(f)

            if "v" in data and data["v"] != VERSION:
                self._log(Stat.ERR_IDX, self.idx_file)
                return False
            
            self.old = data["files"]
            text = json.dumps(self.old, separators=(",", ":"))
            if data.get("files_hash") != hashtext(text):
                self.modified = True      

            self.mtime = data.get("mtime")
        
        self._log(Stat.ERR_IDX, self.idx_file)  
        return True

    def load_ignore(self):
        if not os.path.exists(self.ignore_file):
            return
        with open(self.ignore_file, "r", encoding="utf-8") as f:
            text = f.read()

        self.ignore = list(
            filter(
                lambda x: x and x[0] != "#" and len(x.strip()) > 0, text.splitlines()
            )
        )
