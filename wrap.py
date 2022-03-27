import hashlib
import json


def wrap_file(file, dest=None):
    if dest is None:
        dest = file
    with open(file, 'r') as src:
        lines = src.readlines()

    with open('wrapped.py', 'w') as wrapped:
        code = json.dumps(''.join(lines))
        hash = f'md5-hash={"".join([hex(x)[2:] for x in hashlib.md5(code.encode("utf-8")).digest()])}'
        wrapped.write(f'# Wrapped from {file} to {dest}\n')
        wrapped.write(f'# {hash}\n')
        wrapped.write(f'with open("{dest}", "w") as dest:\n')
        wrapped.write(f'dest.write('+code+')\n')
    print(f'Wrapped code with {hash}')


if __name__ == '__main__':
    wrap_file('cmd.py')
