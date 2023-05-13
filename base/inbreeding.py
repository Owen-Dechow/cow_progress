def calculate_inbreeding(p):
    paternal = map_parents(p["sire"], {}, 0)
    fraternal = map_parents(p["dam"], {}, 0)

    inbreeding = 0
    for animal_paternal, depths_paternal in paternal.items():
        if animal_paternal in fraternal:
            for depth_fraternal in fraternal[animal_paternal]:
                for depth_paternal in depths_paternal:
                    inbreeding += 0.5 ** (depth_paternal + depth_fraternal + 1)

    return inbreeding


def map_parents(p, dic, depth):
    if p["id"] + p["sex"] in dic:
        dic[p["id"] + p["sex"]].append(depth)
    else:
        dic[p["id"] + p["sex"]] = [depth]

    if p["sire"]:
        dic = map_parents(p["sire"], dic, depth + 1)

    if p["dam"]:
        dic = map_parents(p["dam"], dic, depth + 1)

    return dic
