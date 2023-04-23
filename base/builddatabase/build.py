from .. import models

with open("correlations.txt") as cor_data, open ("ptas.txt") as pta_data:
    for line in pta_data.readlines():
        name, sd = line.strip().removesuffix("\n").split(":")
        
        trait = models.Trait()
        trait.name = name
        trait.standard_deviation = float(sd)
        trait.save()

    PTAs = models.Trait.objects.all()
    for rowIDX, line in enumerate(cor_data):
        linedata = line.strip().removesuffix("\n").split(" ")
        while " " in linedata:
            linedata.remove(" ")
        for colIDX, val in enumerate(linedata):
            correlation = models.Correlation()
            correlation.trait_a, correlation.trait_b = PTAs[rowIDX], PTAs[colIDX]
            correlation.factor = val
            correlation.save()