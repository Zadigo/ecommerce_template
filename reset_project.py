import argparse
import os
from functools import lru_cache
from itertools import chain
from collections import deque

RESTRICTED_LIST = []

def walk_project(start_from, restrict_to=[]):
    def wrapper(func):
        @lru_cache(maxsize=1)
        def inner():
            root = os.path.dirname(__file__)
            base = list(os.walk(os.path.join(root, start_from)))
            migration_folders = filter(lambda x: 'migrations' in x[0], base)
            final_folders = deque()
            for path, _, files in migration_folders:
                paths = [
                    os.path.join(path, _file) 
                        for _file in files if not _file.startswith('__')
                ]
                final_folders.append(paths)

            final_folders = deque(chain(*final_folders))

            if restrict_to:
                for app in restrict_to:
                    for folder_path in final_folders:
                        if not app in folder_path:
                            final_folders.remove(folder_path)
            return final_folders
        return func(inner())
    return wrapper


@walk_project('mywebsite', restrict_to=RESTRICTED_LIST)
def delete_migrations(paths):
    counter = 0
    answer = input('You are about to delete all the migrations from your project. Continue? [y/n] ')
    if answer == 'y':
        for path in paths:
            if path:
                exists = os.path.exists(path)
                if exists:
                    os.remove(path)
                    print('Deleting migration at:', path)
                    counter += 1
                    print(f'Deleted:', counter, 'files')
        if counter == 0:
            print('No files were deleted.')
    else:
        print('Cancelled')
            

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Delete migration files')
    parser.add_argument('-a', '--apps', nargs='+', help='Applications to reset', required=False)
    parsed_args = parser.parse_args()
    for app in parsed_args.apps:
        RESTRICTED_LIST.append(app)
