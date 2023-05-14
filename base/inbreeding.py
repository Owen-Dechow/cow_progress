def calculate_inbreeding(p):
    paternal = map_parents(p["sire"], {}, 0, "Y")
    fraternal = map_parents(p["dam"], {}, 0, "X")

    inbreeding = 0
    for animal_paternal, depths_paternal in paternal.items():
        if animal_paternal in fraternal:
            for depth_fraternal in fraternal[animal_paternal]:
                for depth_paternal in depths_paternal:
                    inbreeding += 0.5 ** (depth_paternal + depth_fraternal + 1)

    return inbreeding


def map_parents(p, dic, depth, sex):
    if p["id"] + p["sex"] in dic:
        dic[p["id"] + sex].append(depth)
    else:
        dic[p["id"] + sex] = [depth]

    if p["sire"]:
        dic = map_parents(p["sire"], dic, depth + 1, "Y")

    if p["dam"]:
        dic = map_parents(p["dam"], dic, depth + 1, "X")

    return dic
