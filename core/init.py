import filestore.filesystem
import core.config
import information.log
import display

def init():
    core.config.init()
    information.log.init()
    filestore.filesystem.init()
    core.config.checkcfg()
    
def init2(display_pettern):
    if display_pettern=="win":
        filestore.filesystem.init_filestore(True)
    display.init(display_pettern)