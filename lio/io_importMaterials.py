import json

import maya.cmds as cmds


def processSelection():
    refs = []
    shapes = []

    grpSel = cmds.ls(sl=True)
    allDecending = cmds.listRelatives(grpSel, allDescendents=True, f=True)
    allDecendingShapes = cmds.ls(allDecending, s=True, l=True)
    for shape in allDecendingShapes:
        try:
            originRef = cmds.getAttr(f'{shape}.alembicName')
            refs.append(originRef)
            shapes.append(shape)
        except:
            pass
    refs = list(set(refs))
    return refs, shapes


def reconnectMatarials(allConnections, namespace):
    print(namespace)
    for c in allConnections:
        # make connections
        c = c.replace('"', '')
        try:
            cmds.connectAttr(c.split(',')[0], f'{namespace}:{c.split(",")[1]}')
        except:
            pass


def assignMaterials():
    materialData = processSelection()
    refs = materialData[0]
    shapes = materialData[1]

    IDOnShapes = []

    for shape in shapes:
        try:
            shapeID = cmds.getAttr(f'{shape}.IOID')
            IDOnShapes.append([shape, shapeID])
        except:
            pass

    for ref in refs:
        materialSets = []
        materials = []
        uniqueMaterials = []
        allConnections = []
        project = cmds.workspace(q=True, directory=True, rd=True)
        JSONPath = f'{project}renderData/alembicShaders/{ref}/{ref}.json'
        print(JSONPath)

        # TODO  this whole method should be re-written. The level on indentation
        #       is way above what it should be.
        with open(JSONPath) as data_file:
            data = json.load(data_file)
            for obj in (data["shapes"]):
                for objSet in IDOnShapes:
                    if obj["IOID"] in (objSet[1]):

                        for material in (obj["materials"]):
                            # print material.keys()[0]

                            setName = f'{ref}_{material.keys()[0]}_SET'

                            for f in material.values()[0]:
                                objSetf = f'{objSet[0]}{f}'
                                try:
                                    cmds.sets(objSetf, add=setName)
                                except:
                                    createSetResult = cmds.sets(em=True, name=setName)
                                    cmds.sets(objSetf, add=setName)

                            materialSets.append([setName, (material.keys()[0])])
                        # check json for rig connections
                        try:
                            allConnections = allConnections + obj["controls"]
                            uniqueMaterials.append([setName, (material.keys()[0])])
                        except:
                            pass

        materialSets = [list(tupl) for tupl in {tuple(item) for item in materialSets}]

        for m in materialSets:
            materialPath = project + f'renderData/alembicShaders/{ref}/{ref}_{m[1]}.mb'
            ns = ref

            for u in uniqueMaterials:
                if m == u:
                    print('should be unique')
                    count = 0
                    while cmds.namespace(exists=ns):
                        count += 1
                        ns = ref + str(count)
            cmds.file(materialPath, i=True, type='mayaBinary', ignoreVersion=True, mergeNamespacesOnClash=True,
                      namespace=ns)
            materialName = f'{ns}:{m[1]}'
            try:
                cmds.sets(cmds.sets(m[0], q=True), e=True, forceElement=materialName)
            except:
                print(f'failed to assign {materialName}')
            # reconnect rig to shading network
            try:
                reconnectMatarials(allConnections, ns)
            except:
                pass
            # remove temporary sets
            cmds.delete(m[0])
