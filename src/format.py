#!/usr/bin/python3


def format_cellosaurus_dump_as_dictionary(file):
    """
    Format Cellosaurus dump (.txt) in a dictionary with the informations that
        will integrating in Wikidata.
    :param file : the cellosaurus dump at .txt format
    :return :  a dictionary. In key, the Cellosaurus id for the cell line. In
        value, the informations on the cell line (name, aliases, external ids,
        species of origin, parent cell line, references, autologous cell line,
        sex of the species of origin, ctaegory of the cell line, etc...)
    """
    cellosaurus_dump_as_dictionary = {}
    with open(file) as file:
        AS = "NULL"
        SY = []
        MeSH = "NULL"
        CLO = []
        BTO = []
        EFO = []
        hPSCreg = "NULL"
        BCGO = []
        RX = []
        WW = []
        CC = []
        DI = []
        di_names = {}
        OX = []
        HI = []
        OI = []
        SX = []
        CA = "NULL"
        for line in file.readlines():
            if line.startswith("ID"):
                ID = line.rstrip("\n").split("   ")[1]
            if line.startswith("AC"):
                AC = line.rstrip("\n").split("   ")[1]
            if line.startswith("AS"):
                AS = line.rstrip("\n").split("   ")[1]
            if line.startswith("SY"):
                SY = line.rstrip("\n").split("   ")[1].split(";")
            if line.startswith("DR"):
                DR = line.rstrip("\n").split("   ")[1]
                if DR.startswith("MeSH"):
                    MeSH = DR.strip("MeSH; ")
                if DR.startswith("CLO"):
                    CLO.append(DR.strip("CLO;").strip(" "))
                if DR.startswith("BTO"):
                    BTO.append(DR.strip("BTO;").replace("BTO:", "BTO_").strip(" "))
                if DR.startswith("EFO"):
                    EFO.append(DR.strip("EFO;").strip(" "))
                if DR.startswith("hPSCreg"):
                    hPSCreg = DR.strip("hPSCreg;").strip(" ")
                if DR.startswith("BCGO"):
                    BCGO.append(DR.strip("BCGO;").strip(" "))
            if line.startswith("RX"):
                reference = line.rstrip("\n").split("   ")[1]
                if reference.startswith("PubMed") or reference.startswith("DOI"):
                    RX.append(reference.strip(";"))
            if line.startswith("WW"):
                WW.append(line.rstrip("\n").split("   ")[1])
            if line.startswith("CC"):
                comment = line.rstrip("\n").split("   ")[1]
                if "Problematic cell line:" in comment:
                    CC.append(comment.strip("Problematic cell line: ").split(".")[0])
            if line.startswith("DI"):
                disease = line.rstrip("\n").split("   ")[1]
                DI.append(disease.split(";")[1].strip(" "))
                di_names[disease.split(";")[1].strip(" ")] = (
                    disease.split(";")[2].strip(" ").strip("\n")
                )
            if line.startswith("OX"):
                species = line.rstrip("\n").split("   ")[1]
                OX.append(species.strip("NCBI_taxid=").split(";")[0])
            if line.startswith("HI"):
                hi = line.rstrip("\n").split("   ")[1].split(";")
                HI.append(hi[0].split(" !")[0])
            if line.startswith("OI"):
                oi = line.rstrip("\n").split("   ")[1].split(";")
                OI.append(oi[0].split(" !")[0])
            if line.startswith("SX"):
                SX.append(line.rstrip("\n").split("   ")[1])
            if line.startswith("CA"):
                CA = line.strip("\n").split("   ")[1]
            if line.startswith("//"):
                cellosaurus_dump_as_dictionary[AC] = {
                    "ID": ID,
                    "AS": AS,
                    "SY": SY,
                    "MeSH": MeSH,
                    "CLO": CLO,
                    "BTO": BTO,
                    "EFO": EFO,
                    "BCGO": BCGO,
                    "hPSCreg": hPSCreg,
                    "RX": RX,
                    "WW": WW,
                    "CC": CC,
                    "DI": DI,
                    "DI_names": di_names,
                    "OX": OX,
                    "HI": HI,
                    "OI": OI,
                    "SX": SX,
                    "CA": CA,
                }
                AC = "NULL"
                ID = "NULL"
                SY = []
                CLO = []
                MeSH = "NULL"
                BTO = []
                EFO = []
                BCGO = []
                AS = "NULL"
                RX = []
                WW = []
                CC = []
                DI = []
                di_names = {}
                OX = []
                HI = []
                OI = []
                SX = []
                CA = "NULL"
        return cellosaurus_dump_as_dictionary
