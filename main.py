#!/usr/bin/env python3

import argparse, sys
import tkinter
from tkinter.filedialog import askopenfile
from tkinter.messagebox import showwarning
from tkinter.simpledialog import askinteger
import fsglib

kparser = argparse.ArgumentParser(prog="Filestake", 
                            description="Fun game for playing cards.")

args = kparser.parse_args()
showwarning(title="Warning!", message="""This game can take a your file to stake at. 
            If you lose and put a file for stake, that file will be deleted.
            If you want baby mode, or no files at stake, then don't choose.
            To enable babymode, when asked for a file, cancel the dialog box.""")

# Use tkinter for GUI
root = tkinter.Tk()
filetostake = askopenfile(mode="r+", title="File to stake?")
rounds = askinteger(title="Rounds?", prompt="How many rounds to play?", initialvalue=20, minvalue=7, parent=root)
startingdeck = askinteger(title="Starting deck", prompt="How many cards to start at your deck?", initialvalue=7, minvalue=7, parent=root)
root.quit()

# Precaution
if not rounds or not startingdeck:
    showwarning(title="Incomplete options", message="Incomplete amount of options provided! Game won't run.\nPlease fill all the options next time!")
    sys.exit(1)

# Start game
fsglib.main(filetostake, rounds, startingdeck=startingdeck)