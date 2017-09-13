import os


class Path:
    def __init__(self, file):
        self.file = file

    def get_absolute_path(self, target_file):
        path, filename = os.path.split(os.path.realpath(self.file))
        return path + "/" + target_file
