# Micropython Command Prompt

THis is the code for a small "command prompt" for micropython, which lets you create, view and delete
files and directories and has a few other utility commands.

All this code was tested on an esp32, but should work with any micropython supporting
microcontroller

### info.txt
Some short notes to self on how to install micropython

### wrap.py
Execute [wrap.py](wrap.py) with the file you want to upload your microcontroller
specified. This will create a python file write template that you can now copy and 
paste from [wrapped.py](wrapped.py) into your command prompt.

### run_terminal.py
a collection of terminal launching commands

### cmd: initialization
Upload [cmd.py](cmd.py) to your microcontroller into the root directory.<br>
Next, upload the file [boot.py](boot.py), which replaces the  existing boot.py.<br>
To start the cmd, enter the following commands:
```py
>>> from cmd import cmd
>>> cmd()
```
To finish initialization, enter these commands once you have started the cmd:
```
/>mkf .boot
/>boot refresh
```
### cmd: commands
most commands are intuitive on how to use them and can be viewn with `help`.
```
boot   [refresh|list|order|remove|add|update]
mkf    <file>
pyver
cd     <dir>
exec   <command>
ver
help
eval   <expr>
rename <old_fname> <new_fname>
cat    <file>
exit
run    <command>
sys
pyimp
rmf    <file>
walk   (<dir>)
dir    (<dir>)
mkdir  <dir>
rmdir  <dir>
```

### cmd: boot
the `boot` command allows you to add custom commands to the boot order
#### add boot command:
`/>boot add [py|run|exec] NAME value`
#### remove boot :
`/>boot remove NAME`
#### change value:
`/>boot update [py|run|exec] NAME value`
#### set order:
`/>boot order NAME order_int`
#### list:
`/>boot list`
#### refresh (should happen automatically but can be used when file got corrupted or needs to be generated the first time):
`/>boot refresh`
#### boot command types:
py -> execute a python command:<br>
`/>boot add py GREET print('\nWelcome, DragonFighter603!\n')`<br>
`/>boot add py START_CMD from cmd import cmd;cmd()`<br>
`/>boot order START_CMD 1024` (giving START_CMD a higher value so it's executed after greet)<br>
<br>
exec -> executes a .py file<br>
`/>boot add exec NAME path/to/file.py`<br>
<br>
run -> executes a command<br>
`/>boot add exec WALK_FILES walk`<br>
