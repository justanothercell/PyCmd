import json
import os
import re
import sys


version = '1.10.4'


commands = {}


def splitstr(string: str, sep=None, max=None):
    if sep is None:
        substr = string.split()
    else:
        substr = string.split(sep=sep)
    if max is None:
        return substr
    result = substr[:max]
    result.append((' ' if sep is None else sep).join(substr[max:]))
    return result


def table(data, cgettr):
    if len(data) == 0:
        return ''
    columns = []
    m = []
    for c in cgettr:
        columns.append([c(d) for d in data])
        m.append(max([len(c) for c in columns[-1]]))
    return '\n'.join(
        ' '.join(f'{columns[r][i]:<{m[r]}}' for r in range(len(columns))) for i in range(len(columns[0])))


class Command:
    def __init__(self, name, argnr, func, register=True, arg_str=''):
        self.name = name
        self.argnr = argnr
        self.func = func
        self.sub_commands = {}
        self.arg_str = arg_str
        if register:
            commands[name] = self

    def execute(self, args):
        if len(self.sub_commands) > 0:
            assert len(args) > 0, f'No subcommand specified for "{self.name}"\nExpected [{"|".join(self.sub_commands)}]'
            if args[0] in self.sub_commands:
                self.sub_commands[args[0]].execute(args[1:])
                return
            else:
                raise Exception(f'Unknown sub command "{args[0]}" for "{self.name}".\nExpected [{"|".join(self.sub_commands)}]')
        if self.func is None:
            raise Exception(f'Invalid command "{self.name}"')
        if isinstance(self.argnr, int):
            assert len(args) == self.argnr, f'Expected {self.argnr} args, got {len(args)}'
        if isinstance(self.argnr, tuple):
            assert self.argnr[0] <= len(args) <= self.argnr[1], f'Expected {self.argnr[0]} to {self.argnr[1]} args, got {len(args)} '
        self.func(*args)


class SubCommand(Command):
    def __init__(self, name, argnr, func, command, arg_str=''):
        super().__init__(name, argnr, func, register=False, arg_str=arg_str)
        self.command: Command = command
        self.command.sub_commands[name] = self


def humanbytes(B):
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776

    if B < KB:
        return '{0}'.format(B), 'B'
    elif KB <= B < MB:
        return '{0:.2f}'.format(B / KB), 'KB'
    elif MB <= B < GB:
        return '{0:.2f}'.format(B / MB), 'MB'
    elif GB <= B < TB:
        return '{0:.2f}'.format(B / GB), 'GB'
    elif TB <= B:
        return '{0:.2f}'.format(B / TB), 'TB'


def isfile(path):
    # if that doesnt work, back to good old try/except OSError - open(path, 'r')
    return os.stat(path)[-1] != 0


def walk(path, go_deep):
    path = '.' if path is None else path
    d = os.getcwd()
    os.chdir(path)
    files = os.listdir()
    print(f'{"Walk through" if go_deep else "Contents of"} "{os.getcwd()}":')
    print('')
    listf = []

    def subdir(path, indent):
        fs = os.listdir(path)
        lfs = []
        i = 0
        for F in fs:  # │ — └ ├   <->  | - L |
            listf.append((path + '/' + F, '|   ' * indent + ('L--' if i == len(fs) - 1 else '|--') + ' ' + F))
            if not isfile(path + '/' + F):
                listf.extend(subdir(path + '/' + F, indent + 1))
            i += 1
        return lfs

    x = 0
    for f in files:
        listf.append((f, f))
        if not isfile(f) and go_deep:
            listf.extend(subdir(os.getcwd() + '/' + f, 1))
        x += 1

    if len(files) > 0:
        print(table([(c[1], isfile(c[0]), humanbytes(os.stat(c[0])[6])) for c in listf],
                    (lambda c: c[0],
                     lambda c: f' {(c[0].split(".")[-1] if len(c[0].split(".")) > 1 else " ")}' if c[1] else ' ',
                     lambda c: ' file' if c[1] else ' dir',
                     lambda c: ' ' + c[2][0],
                     lambda c: c[2][1])))
    else:
        print('This folder is empty')
    os.chdir(d)


def cat(file: str):
    print(f'Contents of "{os.getcwd()}{"/" if len(os.getcwd()) > 1 else ""}{file}":')
    print()
    with open(file, 'r') as read:
        print(''.join(read.readlines()))
    print()


def mkf(file: str):
    with open(file, 'w'):
        pass


Command('cd', 1, os.chdir, arg_str='<dir>')
Command('walk', (0, 1), lambda x=None: walk(x, True), arg_str='(<dir>)')
Command('dir', (0, 1), lambda x=None: walk(x, False), arg_str='(<dir>)')
Command('cat', 1, cat, arg_str='<file>')
Command('mkdir', 1, os.mkdir, arg_str='<dir>')
Command('rmdir', 1, os.rmdir, arg_str='<dir>')
Command('mkf', 1, mkf, arg_str='<file>')
Command('rename', 2, os.rename, arg_str='<old_fname> <new_fname>')
Command('rmf', 1, os.remove, arg_str='<file>')
Command('sys', 0, lambda: print(os.uname()))
Command('ver', 0, lambda: print(version))
Command('pyver', 0, lambda: print(sys.version))
Command('pyimp', 0, lambda: print(sys.implementation))
Command('help', 0, lambda: print(table(list(commands.values()), (lambda c: c.name,
                                                            lambda c: (str(c.argnr) if c.arg_str == '' and c.argnr != 0 else c.arg_str) if len(c.sub_commands) == 0 else f'[{"|".join(c.sub_commands.keys())}]'))))
Command('cd', 1, os.chdir, arg_str='<dir>')
Command('exit', 0, sys.exit)
Command('run', (1, 255), lambda *x: run(' '.join(x)), arg_str='<command>')

Command('eval', (1, 255), lambda *x: print(eval(' '.join(x))), arg_str='<expr>')
Command('exec', (1, 255), lambda *x: exec(' '.join(x)), arg_str='<command>')

# exec NAME execfile("path/to/foo.py")
# py NAME function(or=import)
# run NAME walk
boot = Command('boot', (1, 255), None)
SubCommand('list', 0, lambda: print('List of all boot commands scripts: \n\n' + table(get_boots(),
                              (lambda c: c[0].split('/')[0],
                               lambda c: c[0].split('/')[1] if len(c[0].split('/')) == 2 else '',
                               lambda c: '  '+c[1],
                               lambda c: '  '+c[2]))), boot)

SubCommand('refresh', 0, lambda: update_boot(), boot)

add_boot_cmd = SubCommand('add', 3, None, boot)
SubCommand('exec', (2, 255), lambda *x: add_boot('exec', ' '.join(x)), add_boot_cmd)
SubCommand('py', (2, 255), lambda *x: add_boot('py', ' '.join(x)), add_boot_cmd)
SubCommand('run', (2, 255), lambda *x: add_boot('run', ' '.join(x)), add_boot_cmd)

update_boot_cmd = SubCommand('update', 3, None, boot)
SubCommand('exec', (2, 255), lambda *x: add_boot('exec', ' '.join(x), is_update=True), update_boot_cmd)
SubCommand('py', (2, 255), lambda *x: add_boot('py', ' '.join(x), is_update=True), update_boot_cmd)
SubCommand('run', (2, 255), lambda *x: add_boot('run', ' '.join(x), is_update=True), update_boot_cmd)

SubCommand('remove', 1, lambda x: remove_boot(x), boot)
SubCommand('order', 2, lambda x, o: boot_order(x, o), boot)


def get_boots():
    with open('/.boot', 'r') as dotboot:
        return sorted([splitstr(line.strip(), max=2) for line in dotboot.readlines()],
                      key=lambda x: int(x[0].split('/')[1]) if len(x[0].split('/')) == 2 else 0)


def boot_order(boot_name, order):
    boot_name = boot_name.upper()
    boots = get_boots()
    i = 0
    for b in boots:
        if b[1] == boot_name:
            boots[i][0] = f'{boots[i][0].split("/")[0]}/{order}'
            with open('/.boot', 'w') as bootfile:
                for line in [' '.join(b) for b in boots]:
                    bootfile.write(line + '\n')
            update_boot()
            break
        i += 1
    else:
        raise Exception(f'Could not set order of boot command "{boot_name}" as no boot has that name')


def add_boot(b_type: str, command: str, is_update=False):
    new_boot = splitstr(command, max=1)
    boot_name = new_boot[0].upper()
    boots = get_boots()
    if is_update:
        i = 0
        for b in boots:
            if b[1] == boot_name:
                the_boot = boots.pop(i)
                break
            i += 1
        else:
            raise Exception(f'Could not remove boot command "{boot_name}" as no boot has that name')
    regex = '^[A-Za-z_][A-Za-z0-9_]*'
    assert re.search(regex, boot_name), f'Invalid boot command name "{boot_name}"'
    assert boot_name not in [b[1] for b in boots], f'Boot command "{boot_name}" already exists'
    b_type += ('/'+new_boot[0].split('/')[1]) if len(new_boot[0].split('/')) == 2 else ''
    boots.append([b_type, boot_name, new_boot[1]])
    with open('/.boot', 'w') as bootfile:
        for line in [' '.join(b) for b in boots]:
            bootfile.write(line+'\n')
    update_boot()


def remove_boot(boot_name: str):
    boot_name = boot_name.upper()
    boots = get_boots()
    i = 0
    for b in boots:
        if b[1] == boot_name:
            boots.pop(i)
            with open('/.boot', 'w') as bootfile:
                for line in [' '.join(b) for b in boots]:
                    bootfile.write(line + '\n')
            update_boot()
            break
        i += 1
    else:
        raise Exception(f'Could not remove boot command "{boot_name}" as no boot has that name')


def update_boot():
    with open('/.boot') as bootfile:
        scripts = [splitstr(line.strip(), max=2) for line in bootfile.readlines()]
    with open('/entrypoint.py', 'w') as entry:
        entry.write('from cmd import run\n\n')
        if len(scripts) == 0:
            entry.write(f'# No boot commands were found\n')
        else:
            entry.write(f'# Executing {len(scripts)} boot commands on boot\n')
            for script in scripts:
                entry.write(f'# {"   ".join(script)}\n')
                type_ = script[0].split('/')[0]
                if type_ == 'py':
                    entry.write(f'{script[2]}\n')
                if type_ == 'exec':
                    entry.write(f'execfile({json.dumps(script[2])})\n')
                if type_ == 'run':
                    entry.write(f'run({json.dumps(script[2])})\n')


def cmd():
    print(f'hi from cmd.py v{version}')
    while True:
        run(input(f'{os.getcwd()}>'))


def run(cmd_):
    args = cmd_.split()
    try:
        if args[0] in commands:
            commands[args[0]].execute(args[1:])
        else:
            raise Exception(f'unknown command "{args[0]}"')
    except Exception as e:
        print(f'Encountered exception while executing "{args[0]}":')
        print(f'    {type(e).__name__}: {e}')


if __name__ == '__main__':
    cmd()
