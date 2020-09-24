import os
from functools import lru_cache, wraps
import argparse

RESTRICTED_LIST = []


def walk_project(start_from, restrict_to=[]):
    def wrapper(func):
        @lru_cache(maxsize=1)
        def inner():
            root = os.path.dirname(__file__)
            base = list(os.walk(os.path.join(root, start_from)))
            migration_folders = filter(lambda x: 'migrations' in x[0], base)
            final_folders = []
            for path, _, files in migration_folders:
                for value in restrict_to:
                    if value in path:
                        paths = [
                            os.path.join(path, _file) 
                                for _file in files if not _file.startswith('__')
                        ]
                        final_folders.append(paths)
            return final_folders
        return func(inner())
    return wrapper


@walk_project('mywebsite', restrict_to=RESTRICTED_LIST)
def delete_migrations(paths):
    counter = 0
    for path in paths:
        if path:
            exists = os.path.exists(path)
            if exists:
                # os.remove(path)
                print('Deleting migration at:', path)
                counter += 1
    if counter == 0:
        print('No files were deleted.')
            

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Delete migration files')
    parser.add_argument('-a', '--apps', nargs='+', help='Applications to reset', required=True)
    parsed_args = parser.parse_args()
    for app in parsed_args.apps:
        RESTRICTED_LIST.append(app)
    delete_migrations
