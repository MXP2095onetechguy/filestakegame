import fsglib
import tkinter as tk, tkinter.ttk as ttk
import getpass

class GameFrame(tk.Frame):
    def __init__(self, master : tk.Misc, game : fsglib.FileStakeGame):
        super().__init__(master)

        self.game = game

        # Create card inspector section
        mycardframe = tk.Frame(self)
        cardsframe = tk.Frame(mycardframe)
        vscroll = tk.Scrollbar(cardsframe, orient=tk.VERTICAL)
        hscroll = tk.Scrollbar(cardsframe, orient=tk.HORIZONTAL)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.mycards = tk.Listbox(cardsframe, yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)
        self.mycards.pack()
        self.mycardsrefresh = ttk.Button(mycardframe, text="Refresh", command=self.refreshmycards)
        cardsframe.pack()
        self.mycardsrefresh.pack()
        mycardframe.grid(row=0, column=0)
        self.refreshmycards()

        # Create textbox for viewing game state
        statframe = tk.Frame(self)
        self.statcmd = tk.Text(statframe, state=tk.DISABLED)
        self.statcmd.pack()
        playframe = tk.Frame(statframe)
        self.statcmdrefresh = ttk.Button(playframe, text="Refresh", command=self.refreshstatcmd)
        self.playround = ttk.Button(playframe, text="Play")
        self.playround.grid(row=0, column=0)
        self.statcmdrefresh.grid(row=0, column=1)
        playframe.pack()
        statframe.grid(row=0, column=1)
        self.refreshstatcmd()


    def __announcestatcmd(self, msg : str):
        self.statcmd.insert(tk.INSERT, f"{msg}\n")

    def refreshmycards(self):
        self.mycards.delete(0, tk.END)
        for card in self.game.inspect():
            self.mycards.insert(tk.END, fsglib.strcard(card))

    def refreshstatcmd(self):
        self.statcmd.config(state=tk.NORMAL)
        self.statcmd.delete('1.0', tk.END)
        self.__announcestatcmd(f"Round: {self.game.viewround()[0]}/{self.game.viewround()[1]}")
        self.__announcestatcmd(f"Points ({self.game.name1}/{self.game.name2}): {self.game.view()[0]}/{self.game.view()[1]}")
        self.statcmd.config(state=tk.DISABLED)


winroot = tk.Tk()
winroot.title("File Stake Game")
game = fsglib.FileStakeGame(None, 20, getpass.getuser(), "Robot", 7)
gf = GameFrame(winroot, game)
gf.pack()

winroot.mainloop()