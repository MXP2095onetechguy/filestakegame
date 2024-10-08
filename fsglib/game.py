import io, random, shlex, os, enum
from tkinter.messagebox import showinfo
import dataclasses
from threading import Event
import cmd, getpass
import typing


def filldeck(deck : list, count : int, sysrand : random.Random):
    from . import cards
    for i in range(count):
        deck.append(sysrand.choice(cards))

def helpfn():
    print("Help (command, description, usage):")
    print("inspect - See your own deck - inspect")
    print("use - use a card - use [index of card]")
    print("quit - Bail out and lose - bail")
    print("help - Print this help message - help")


@dataclasses.dataclass(frozen=False)
class Player(object):
    deck : list
    point : int
    name : str

class GameState(enum.Enum):
    CONTINUE = 1
    WIN = 2
    BADINPUT = 4

CardIndexer = typing.Callable[[], int]

class FileStakeGame(object):
    def __init__(self, filetostake : io.IOBase | None, rounds : int, name1 : str, name2 : str, startingdeck : int):
        self.me : Player = Player([], 0, name1)
        self.opponent : Player = Player([], 0, name2)

        self.name1 = name1
        self.name2 = name2
        self.winstate = GameState.CONTINUE
        self.fts = filetostake
        self.urounds = rounds
        self.rounds = self.urounds
        self.currentround = 1
        self.startingdeck = startingdeck
        self.sysrand = random.SystemRandom()
        self.allowpeek = Event()

        self.refilldeck()


    def ftscheck(self) -> io.IOBase | None:
        """Get a handle to the file at stake."""
        return self.fts
    
    def babymode(self) -> bool:
        """Check if babymode is active. Babymode is active if fts is None."""
        return self.fts is None
    

    def reset(self):
        """Reset the game. File stake is disabled for this one (baby mode)."""
        self.me = Player([], 0, self.name1)
        self.opponent = Player([], 0, self.name2)
        self.winstate = [0, GameState.CONTINUE]
        self.rounds = self.urounds
        self.currentround = 1
        self.allowpeek.clear()
        self.refilldeck()
        

    def cleardeck(self):
        """Clear the deck"""
        self.me.deck.clear()
        self.opponent.deck.clear()

    def refilldeck(self):
        """Clear and refill deck"""
        self.cleardeck()
        filldeck(self.me.deck, self.startingdeck, self.sysrand)
        filldeck(self.opponent.deck, self.startingdeck, self.sysrand)


    def __losefile(self):
        if self.ftscheck():
            self.fts.write(chr(0) * os.path.getsize(self.fts.name))


    def __doact(self, me : Player, opponent : Player, card, pfn : typing.Callable[[object], None]):
        from . import Card, PointCard, ActionCard, Actions, strdeck, strcard
        if isinstance(card, PointCard):
            card : PointCard = card
            pfn(f"{me.name} got {card.value} points")
            me.point = me.point + card.value

        # Action cards logic
        if isinstance(card, ActionCard):
            card : ActionCard = card
            opponentname = f"{opponent.name}'{'s' if opponent.name.casefold()[-1] != 's' else ''}"
            if card.action == Actions.STEAL:
                pfn(f"{me.name} stole {opponentname} card.")
                ocard = opponent.deck.pop(self.sysrand.randrange(len(opponent.deck)))
                me.deck.append(ocard)
                pfn(f"Its a card that reads: '{strcard(ocard)}'")
            elif card.action == Actions.DISCARD:
                pfn(f"{me.name} discarded {opponentname} card.")
                ocard = opponent.deck.pop(self.sysrand.randrange(len(opponent.deck)))
                pfn(f"It was a card that reads: '{strcard(ocard)}'")
            elif card.action == Actions.EXTEND:
                pfn(f"{me.name} extended the game by 7 more rounds")
                self.rounds = self.rounds + 7
            elif card.action == Actions.PEEK:
                self.allowpeek.set()
                pfn(f"{opponentname} deck after use:")
                pfn(strdeck(self.peek()))
            elif card.action == Actions.REFILL:
                self.refilldeck()
                pfn(f"{me.name} refilled the deck. Inspect again.")
            elif card.action == Actions.DEDUCT:
                pfn(f"{opponentname} points deducted by 5")
                opponent.point = opponent.point - 5

    def inspect(self) -> list:
        """Inspect my own deck"""
        return self.me.deck
    
    def peek(self) -> list | None:
        """Peek at opponent's deck if permitted. None returned means unpermitted"""
        v = (self.opponent.deck if self.allowpeek.is_set() else None)
        self.allowpeek.clear()
        return v
    
    def view(self) -> tuple[int, int]:
        """View the score (You/Opponent)"""
        return (self.me.point, self.opponent.point)
    
    def viewround(self) -> tuple[int, int]:
        """View the round information (Current round/Total rounds)"""
        return (self.currentround, self.rounds)

    def play(self, megetindex : CardIndexer = None, opponentgetindex : CardIndexer = None, pfn : typing.Callable[[object], None] = None) -> list[int, GameState]:
        """Play and advance a round"""
        from . import Card, PointCard, ActionCard, Actions, strdeck, strcard
        pfn = pfn if pfn else print

        opponentgetindex : CardIndexer = opponentgetindex if opponentgetindex else lambda : self.sysrand.randrange(len(self.opponent.deck))

        myindex : int = megetindex()
        opponentindex : int = opponentgetindex()

        if myindex  < 0 or myindex > (len(self.me.deck)-1):
            return [1, GameState.BADINPUT]
        elif opponentindex < 0 or opponentindex > (len(self.opponent.deck)-1):
            return [2, GameState.BADINPUT]
        
        mycard : Card = self.me.deck.pop(myindex)
        opponentcard : Card = self.opponent.deck.pop(opponentindex)

        self.__doact(self.me, self.opponent, mycard, pfn)
        self.__doact(self.opponent, self.me, opponentcard, pfn)

        self.currentround = self.currentround + 1

        if self.viewround()[0] > self.viewround()[1]:
            pfn("Game is over.")
            return self.quit()
        
        


        return [0, self.winstate]

    def quit(self):
        if self.me.point <= self.opponent.point:
            self.__losefile()
            self.winstate = [2, GameState.WIN]
        else:
            self.winstate = [1, GameState.WIN]
            
        return self.winstate

class FileStakeGameShell(cmd.Cmd):
    intro = "File Stake Card Game\nRun 'inspect' to see your current points and game round."
    prompt = "(FSC)> "

    def __init__(self, game : FileStakeGame):
        super().__init__()
        self.game = game


    def do_inspect(self, _):
        """Inspect game state like current rounds, points and your deck"""
        from . import strdeck
        print(f"Round (Current/Total) - {self.game.viewround()[0]}/{self.game.viewround()[1]}")
        print(f"Points ({self.game.name1}/{self.game.name2}) - {self.game.view()[0]}/{self.game.view()[1]}")
        print(f"You are {self.game.name1}")
        print(f"{'Baby mode is active; No files at stake' if self.game.babymode() else 'Your file file is at stake, play wisely.'}")
        print("")
        print(strdeck(self.game.inspect()))

    def do_quit(self, _):
        """Quit, bail (and potentially lose)"""
        v = self.game.quit()
        if v[1] == GameState.WIN and v[0] != 1:
            print("haha loser")
        return True
    
    def do_use(self, line):
        """Use a card and advance the round. (use [index]) """
        chunktokens = shlex.split(line)
        if len(chunktokens) < 1:
            return False
        
        cindex = None
        try:
            cindex = int(chunktokens[0])
        except ValueError:
            print("Card index is an invalid number. Try again with a valid number.")
            return False
        assert cindex is not None
        
        v = self.game.play(lambda : cindex, None, lambda s : print(s))
        if v[1] == GameState.BADINPUT:
            print(f"{self.game.name1}'{'s' if self.game.name1.casefold()[-1] != 's' else ''} card index is out of range. Try again with an index within range. Inspect if necessary.")
            return False
        elif v[1] == GameState.WIN:
            print(f"{self.game.name1 if (v[1] == 1) else self.game.name2} won!")
            return True
        

        







def main(fts : io.IOBase | None, rounds : int, startingdeck : int):
    import readline
    ftsgame = FileStakeGame(fts, rounds, getpass.getuser(), "Robot", startingdeck)
    FileStakeGameShell(ftsgame).cmdloop()

quickmain = lambda : main(None, 1, 7)
