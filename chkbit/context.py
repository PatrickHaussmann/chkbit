import hashlib


class Context:
    def __init__(self, verify_index, update, force, skip_symlinks):

        self.verify_index = verify_index
        self.update = update
        self.force = force
        self.skip_symlinks = skip_symlinks
