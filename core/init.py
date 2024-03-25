import filestore.filesystem
import core.config
import information.log
import display
def init():
    core.config.init()
    information.log.init()
    filestore.filesystem.init()
    display.init()
    core.config.checkcfg()
    pass