# Isoviewer for Helios Automazioni srl CNC Machines

This software reads proprietary GCode files with PGR extension and shows the path followed by the tools during the job.

> This is **not** an official software developed by [Helios Automazioni srl](https://www.heliosautomazioni.com/it/home-it.html).
>
> I am employed as a CNC programmer at [Centro Marmi D'Arcangeli srl](https://www.cmdarcangeli.com), sometimes I found useful to see what a file contains, for this reason I decided to develop this tool.

## Features
- Import multiple files at once
- Possibility to specify the working area size
- The drawn path automatically fits the visible area
- Option to automatically regenarate the drawing, when the main window is resized, to fit the new size of the visible area
- Calculation of the distance traveled both for repositionings and millings
- Estimate of the working time given the speed of the tool (not reliable)

About the working time, the reason why it is not currently reliable, is that the machine doesn't really keep the speed constant while working, it could vary due to the hardness of the material, the complexity of the job and other reasons.
Where the job is at a constant depth the time results to be almost correct. 

## Tech
The whole software is written in `Python`, using `PySide6` to build the user interface.

## How to compile
To compile the software, `Python 3.8+`, `Qt 6.0+` and `PySide6` are required.
You can use your preferred method to compile the software, auto-py-to-exe for example if you want to use it on Windows platforms.
The main file in this project is `Isoviewer.py`.

## Installation
Inside the folder `dist` the latest compiled version of the software for Windows is available in a zip format.
There is no need to install the software.
Unpack the zip package, inside the folder `Isoviewer`, find and run the file `Isoviewer.exe`.