# Isoviewer

This software reads proprietary GCode files, specifically for CNC machines manufactured by [Helios Automazioni](https://www.heliosautomazioni.com/it/home-it.html) and shows the path followed by the tools to engrave, cut or mill.

## Tech
The whole software is written in `Python` using `PySide6` to build the user interface.

## Features
- Import multiple files at once
- Possibility to specify the working area size
- The path automatically fits the visible area
- Option to automatically regenarate the drawing on main window resizing to fit the new size of the visible area
- Calculation of the distance travelled both for repositionings and millings
- Estimate of the working time given the tool speed (not yet reliable)

About the working time, the reason why it is not currently reliable, is that the machine doesn't really keep the speed constant while working, it could vary due to the material hardness or the job complexity. Where the job is at a constant depth the time results to be almost correct. 

## Installation
To compile the software, `Python 3.8+`, `Qt 6.0+` and `PySide6` are required.