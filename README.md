# Album plugin for packaging solutions into executables

This plugin is used to create executables from solutions, so a solution can be run with a simple
double click. The executables can be distributed to a different system running the same operating system.
 To create executables for different operating systems, run the this plugin on 
the a system running the target operating system.
The target system doesn't need to have anything preinstalled, the executable will install every 
needed component (Miniconda, album, album-gui) into the ~/.album directory if they are not already
installed on the system.


## Installation:
1. [Install Album](https://docs.album.solutions/en/latest/installation-instructions.html#)
2. Activate the album environment:
```
conda activate album
```
3. Install the album package plugin:
```
pip install HERE LINK
```

## Usage:
To create an executable which launches the solution with a graphical user interface run following command:
```
album package /path/to/your/solution.py /your/output/path
```
To create an executable which launches the solution in a commandline run following command:
```
album package /path/to/your/solution.py /your/output/path --no_gui
```
### Input parameter:
- solution: The album solution.py file which should be packed into an executable
- output_path: The path where the executable should be saved
- no_gui: If this parameter is set than an executable is created which launches the solution in a commandline
if not the executable will launch the solution.py with a graphical user interface.
