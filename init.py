import filestore.filesystem
import config.config
import information.log
import display


def init():
    config.config.init()
    information.log.init()
    filestore.filesystem.init()
    display.init()
    pass