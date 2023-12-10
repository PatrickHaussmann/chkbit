import hashlib
import datetime
import re


class Context:
    def __init__(self, verify_index, update, force, skip_symlinks, only_new, non_recursive, check_date):

        self.verify_index = verify_index
        self.update = update
        self.force = force
        self.skip_symlinks = skip_symlinks
        self.only_new = only_new
        self.non_recursive = non_recursive

        if check_date:
            # mtime in milliseconds as string
            if re.match(r"^\d+$", check_date):
                self.check_date = int(check_date)

            # YYYY-MM-DD
            elif re.match(r"^\d{4}-\d{2}-\d{2}$", check_date):
                self.check_date = datetime.datetime.strptime(check_date, "%Y-%m-%d").timestamp() * 1000

            # YYYY-MM-DD HH:MM:SS
            elif re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", check_date):
                self.check_date = datetime.datetime.strptime(check_date, "%Y-%m-%d %H:%M:%S").timestamp() * 1000

            else:
                print("invalid date format")
                exit(1)

        else:
            self.check_date = None
