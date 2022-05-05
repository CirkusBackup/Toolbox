import os
import maya.cmds as cmds
import subprocess
from textwrap import dedent


def _maya_batch_exe() -> str:
    """Returns the location of the maya batch executable"""
    return f'{os.getenv("MAYA_LOCATION")}\\bin\\mayabtach.exe'


def submitToSmedge(packetSize: int, priority: int, sim: bool, foam: bool, mesh: bool):
    # Query values from UI

    submit = 'C:/Program Files/Smedge/Submit.exe'
    working_dir = submit.rsplit('/', 1)[0]

    # set the working dir and PATH to the directory
    os.chdir(working_dir)
    os.putenv("PATH", working_dir)
    # now set submit to just the basename of the executable
    submit = submit.rsplit('/', 1)[1]

    # get start and end frames from timeline
    startFrameFloat = cmds.playbackOptions(q=True, minTime=True)
    startFrame = str(f'{startFrameFloat:g}')
    endFrameFloat = cmds.playbackOptions(q=True, maxTime=True)
    endFrame = str(f'{endFrameFloat:g}')

    # set naming
    filename: str = cmds.file(q=True, sn=True)
    shortname: str = cmds.file(q=True, sn=True, shn=True)
    smedgeName: str = f'bifrost: {shortname.split(".")[0]}'
    extra: str = ''
    jobID: str = ''
    bifrostLiquidContainer = ''  # TODO get the bifrost container to set it's attributes

    # mesh cache
    cmds.setAttr(f'{bifrostLiquidContainer}.liquidmeshCacheControl', 0)
    cmds.setAttr(f'{bifrostLiquidContainer}.enableLiquidMeshCache', 0)
    cmds.setAttr(f'{bifrostLiquidContainer}.liquidmeshCachePath', '', type="string")
    cmds.setAttr(f'{bifrostLiquidContainer}.liquidmeshCacheFileName', '', type="string")

    # check what to do
    if sim:
        extra = '-UsageLimit 1 -DistributeMode \"Forward\"'
        # clear cache inputs
        if mesh == 1:
            # liquid cache
            cmds.setAttr(f'{bifrostLiquidContainer}.enableLiquidCache', 0)
            cmds.setAttr(f'{bifrostLiquidContainer}.liquidCacheControl', 0)
            cmds.setAttr(f'{bifrostLiquidContainer}.liquidCachePath', '', type="string")
            cmds.setAttr(f'{bifrostLiquidContainer}.liquidCacheFileName', '', type="string")
            # solid cache
            cmds.setAttr(f'{bifrostLiquidContainer}.enableSolidCache', 0)
            cmds.setAttr(f'{bifrostLiquidContainer}.solidCacheControl', 0)
            cmds.setAttr(f'{bifrostLiquidContainer}.solidCachePath', '', type="string")
            cmds.setAttr(f'{bifrostLiquidContainer}.solidCacheFileName', '', type="string")

        # set variables on bifrost nodes
        # turn mesh off
        # turn evaluate on
        # evaluation type to simulation
        # clear all cache variables

        # save file
        cmds.file(rename='%s.sim' % (filename.rsplit('.', 1)[0]))
        cmds.file(save=True)
        # submit string

        cmd = dedent(f'''
        {submit} Script
        -Type "Generic Script"
        -Name "{smedgeName} - SIM"
        -Priority {priority} {extra}
        -Pool "Redshift"
        -ErrorStarts "Failed"
        -Range "{startFrame}-{endFrame}"
        -PacketSize {packetSize}
        -Command "{_maya_batch_exe()}" "{filename.split('.', 1)[0]}"
        "-command" "MeshBifrost($(SubRange.Start),$(SubRange.End),{int(sim)},{int(foam)},{int(mesh)})"
        ''').replace('\n', ' ')

        print(cmd)
        # do it
        jobID = subprocess.check_output(cmd, stdin=None, stderr=None, shell=False)
        print(str(jobID).split(' ')[-1])

    if mesh:
        extra = f'-WaitForJobID {jobID.split(" ")[-1]} -WaitForWholeJob 0'
        if sim == 1:
            print('wait for sim to finish')
            # extra = 'wait for sim to finish'
        cmds.file(rename=f'{filename.rsplit(".", 1)[0]}.mesh')
        cmds.file(save=True)
        # submit string
        cmd = dedent(f'''
        {submit} Script
        -type "Generic Script"
        -Paused
        -Name "{smedgeName} - MESH"
        -Priority {priority} {extra}
        -Pool "Redshift"
        -ErrorStarts "Failed"
        -Range "{startFrame}-{endFrame}"
        -Command "{_maya_batch_exe()}" "{filename.rsplit('.', 1)[0]}"
        "-command" "MeshBifrost($(SubRange.Start),$(SubRange.End),{int(sim)},{int(foam)},{int(mesh)})"
        ''').replace('\n', ' ')

        print(cmd)
        # do it
        result = subprocess.check_output(cmd, stdin=None, stderr=None, shell=False)

    # set filename back
    cmds.file(rename=filename)
    cmds.file(save=True)


submitToSmedge(4, 100, True, False, True)
