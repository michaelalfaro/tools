def SIcalc(phenotype)
	ep_area = 50
	inlever = phenotype[0]
	outlever = phenotype[1]
	gape = 12.5
	buccal = 15.0
    numerator = ep_area*(inlever/outlever)
    denominator = ((2.0/3.0) * gape * buccal)
    return 	numerator/denominator

  EP = uni(17, 134)
            IN = uni(2, 8)
            OUT = uni(14, 30)
            GAPE = uni(4, 21)
            BUCCAL = uni(8, 22)