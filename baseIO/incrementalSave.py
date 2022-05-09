import os
import re

import maya.cmds as cmds


def GetFilename(short):
    """
    Get and return the filename.
    """
    filename = cmds.file(query=True, sceneName=True, shortName=short)
    return filename


def simpleSplit(s, c, n):
    """
    Split words.
    """
    words = s.split(c)
    return c.join(words[:n])


def ListAllFiles():
    """
    Return a list of other files in the current directory.
    """
    removeFilename = GetFilename(False).rsplit('/', 1)
    files = os.listdir(removeFilename[0])
    allinitialless = []
    for item in files:
        # check for initials
        end = item.split('_')[-1]
        if any(char.isdigit() for char in end):
            initialless = item.rsplit('.', 1)[0]
        else:
            initialless = item.rsplit('_', 1)[0]
        versionless = simpleSplit(initialless, '_', -1)
        allinitialless.append(initialless)
    return allinitialless


"""
    Version Incrementing
"""


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


def RemoveInitials(s, c, n):
    hasVersion = 0
    words = s.split(c)
    for w in words:
        if hasNumbers(w):
            hasVersion = 1
    if hasVersion == 1:
        name = c.join(words)
        # check if filename has initials
        if words[-1].isalpha():
            name = c.join(words[:n])
        return name
    else:
        name = s.rsplit('.', 1)[0]
        return name


def RemoveVersion(s, c, n):
    """
    Return the string with the version stripped.
    """
    words = s.split(c)
    name = c.join(words)
    version = words[-1].lower()
    # check if filename has version
    if (version.replace("v", "")).isdigit():
        name = c.join(words[:n])
    return name


def CurrentVersion(filename):
    """
    Returns the current version.
    """
    version = '0'
    # check if version exists
    if any(char.isdigit() for char in filename):
        removeLetters = re.sub('[a-z]*\.?[a-zA-Z]', "", filename)
        while (removeLetters[-1] == '_'):
            removeLetters = removeLetters[:-1]

        splitNumbers = removeLetters.split('_')
        version = splitNumbers[-1]
    return version


def NextVersionAsString(filename):
    """
    Increments the current version and returns the next.
    """
    versionString = (CurrentVersion(filename))
    nextVersion = int(versionString) + 1
    nextVersionString = str(nextVersion)

    while len(nextVersionString) < 3:
        nextVersionString = '0' + nextVersionString
    return nextVersionString


def CreateCandidate(filename):
    initialless = RemoveInitials(filename, '_', -1)
    versionless = RemoveVersion(initialless, '_', -1)
    candidate = (versionless + '_v' + NextVersionAsString(initialless))
    return candidate


def CompareCandidate(candidate, allFiles, folder, initials):
    nextCandidate = candidate
    success = False

    while not success:
        foundMatch = False
        for f in allFiles:
            if nextCandidate == f:
                foundMatch = True
                nextCandidate = CreateCandidate(f)

        if not foundMatch:
            success = True
            break

    if success:
        intitialsExt = ''
        if len(initials) > 0:
            intitialsExt = '_' + initials

        fullNewName = (folder + '/' + nextCandidate + intitialsExt + '.mb')
        cmds.file(rename=fullNewName)
        cmds.file(save=True)


def IncrementCurrentFile(**keyword_parameters):
    fullFilename = GetFilename(False).rsplit('/', 1)
    folder = fullFilename[0]
    filename = fullFilename[-1]
    remove_extension = RemoveInitials(filename, '.', -1)

    candidate = CreateCandidate(remove_extension)

    allFiles = ListAllFiles()

    initials = ''
    if 'initials' in keyword_parameters:
        initials = keyword_parameters['initials']

    CompareCandidate(candidate, allFiles, folder, initials)
