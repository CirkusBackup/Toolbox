import maya.cmds as cmds


# adds value to an attribute
def addAttribute(shape, name: str, value):
    """
    Adds an attribute to an object.
    """
    if not cmds.attributeQuery(name, node=shape, exists=True):
        cmds.addAttr(shape, ln=name, dt='string')
    cmds.setAttr(f'{shape}.{name}', e=True, keyable=True)
    cmds.setAttr(f'{shape}.{name}', value, type='string')


# clean padding
def addPadding(s, padding):
    while len(s) < padding:
        s = f'0{s}'
    return s


# check if string contains any digits
def containsDigits(s):
    for char in list(s):
        if char.isdigit():
            return True
    return False
