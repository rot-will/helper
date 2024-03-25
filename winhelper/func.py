import re
def get_cmd_info(path):
    f=open(path,'rb')
    data=f.read().decode('gbk')
    cmd=re.findall('set c=(.*)',data)[0].strip()
    try:
        des=re.findall('set des=(.*)',data)[0].strip()
    except:
        des=''
    try:
        ico=re.findall('set ico=(.*)',data)[0].strip()
    except:
        ico=''
    real_dir=''
    try:
        real_dir=re.findall('set real_dir="(.*?)"',data)[0].strip()
    except IndexError:
        pass
    precom=''
    dl=data.splitlines()
    status=False
    for i in dl:
        if '%c%' in i:
            status=False
        if status:
            precom+=i+'\r\n'
        if 'set c=' in i:
            status=True
    precom=precom.strip()
    is_start=False
    if 'start ""'  in data:
        is_start=True
    return cmd,des,precom,is_start,real_dir,ico