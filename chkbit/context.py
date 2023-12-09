import hashlib


class Context:
    def __init__(self, verify_index, update, force, skip_symlinks, only_new, non_recursive):

        self.verify_index = verify_index
        self.update = update
        self.force = force
        self.skip_symlinks = skip_symlinks
        self.only_new = only_new
        self.non_recursive = non_recursive
