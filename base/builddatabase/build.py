from .. import models

RELPATH = "base/builddatabase/"

def build():
    with open(RELPATH + "correlations.txt") as cor_data, open (RELPATH + "ptas.txt") as pta_data:
        for line in pta_data.readlines():
            name, sd = line.strip().removesuffix("\n").split(":")
            
            trait = models.Trait()
            trait.name = name
            trait.standard_deviation = float(sd)
            trait.average = 0
            trait.save()

        PTAs = models.Trait.objects.all()
        for rowIDX, line in enumerate(cor_data):
            linedata = line.strip().removesuffix("\n").split(" ")
            while "" in linedata:
                linedata.remove("")
            for colIDX, val in enumerate(linedata):
                correlation = models.Correlation()
                print(val, colIDX)
                correlation.trait_a, correlation.trait_b = PTAs[rowIDX], PTAs[colIDX]
                correlation.factor = val
                correlation.save()