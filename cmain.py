import fsglib, argparse, sys

parser = argparse.ArgumentParser(prog="File Stake Game", description="Game of cards, but you bet a file")
parser.add_argument("-f", "--file2stake", 
                    help="File to bet and stake. It will be deleted if you lose.", 
                    dest="file2stake",
                    action="store",
                    type=argparse.FileType("r+"))
parser.add_argument("-r", "--rounds", 
                    help="How many rounds to play with",
                    dest="rounds",
                    action="store",
                    required=True,
                    type=int)
parser.add_argument("-c", "--starting-deck",
                    help="How many cards to start with in your deck",
                    dest="cards",
                    action="store",
                    required=True,
                    type=int)

args = parser.parse_args(sys.argv[1:])
fsglib.main(args.file2stake, args.rounds, args.cards)