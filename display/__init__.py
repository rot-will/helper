import display.console
def init():
    display.console.init()
    pass

def show(args):
    if args.display=='con':
        display.console.show(args)
    else:
        pass
    pass

def make_opt(arg):
    display.console.make_opt(arg)
    pass