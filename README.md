# DCC-EX_py


[![image](https://img.shields.io/pypi/v/DCC-EX_py.svg)](https://pypi.python.org/pypi/DCC-EX_py)


A simple way to connect to your DCC-EX controlled model railroad using python code without having to write DCC-EX commands manually.

[DCC-EX](https://dcc-ex.com/#gsc.tab=0) is an Arduino powered DIY tool for running DCC model trains on a layout.
This package wraps the protocol described in the [DCC-EX Native Commands Summary Reference](https://dcc-ex.com/reference/software/command-summary-consolidated.html) to be easy to use from python code.


-   Free software: MIT License
-   Documentation: https://github.com/Zenith08/DCC-EX_py/wiki

This package is in early development, breaking changes may happen until it is marked version 1.0.

## Features

-   Connects to a DCC-EX base station and wraps commands to make automating layouts easier.
-   Parses feedback from the command station and provides callbacks for important events.

## Get Started
Documentation is available on the [GitHub Wiki](https://github.com/Zenith08/DCC-EX_py/wiki) including code for the examples.

## Examples
### Single Sound-Enabled Train:
[![Amtrak Example](http://img.youtube.com/vi/8A_f9tJLWSE/0.jpg)](https://youtu.be/8A_f9tJLWSE)

This video shows a train running a simple loop with sound triggers and stopping based on sensors in the track.

### Multiple Complex Trains
[![Multitrain Example](http://img.youtube.com/vi/ylQdYiYuVxI/0.jpg)](https://youtu.be/ylQdYiYuVxI)

This video shows what can be done when multiple trains are programmed to perform complex behavior. The routes are all pre-planned and designed to loop.

Be aware that the crossing signal is being controlled by EX-RAIL automation on the command station instead of externally by the python script.

<sub><sup>This project is not an official DCC-EX project nor is it endorsed by them. I just used the name that best decribes the funcionality and will change it if it creates issues.</sup></sub>
