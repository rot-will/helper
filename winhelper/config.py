import re
def ParseConfig(conf_path):
    f=open(conf_path)
    regs="(.*?\{)|([ \n]*[\w+]:.*?, *[ \n]*)|( *[\w+]:.*? *\n)|([ \n\r]*\})"
    
    pass

