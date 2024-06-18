import display.console
import display.win
def init(display_pattern):
    if display_pattern=="con":
        display.console.init()
    elif display_pattern=="win":
        display.win.init()
    pass

def show(args):
    if args.display=='con':
        display.console.show(args)
    elif args.display=='win':
        display.win.show(args)
        pass
    pass

def make_opt(arg):
    display.console.make_opt(arg)
    pass