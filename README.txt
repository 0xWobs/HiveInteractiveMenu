# HiveInteractiveMenu
Startup file should be HiveInteractiveMenu.py

Very little error catching in place at the moment

accounts and keys need to be added to keys.json file to work
Other settings also in the keys.json file (staking times are in Minutes)
users should only need to install dependencies and modify the keys file to run the program

DEV - to get git to ignore the keys.json file if/when you put your keys in
Run "git update-index --skip-worktree keys.json"
This eliminates tracking of the keys file so it will not push your keys into the repo
To undo: "git update-index --no-skip-worktree keys.json"