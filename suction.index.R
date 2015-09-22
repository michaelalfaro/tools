###solve for isocurve area of suction index


###old python code
# ep_area = phenotype[0]
         inlever = phenotype[1]
         outlever = phenotype[2]
         gape = phenotype[3]
         buccal = phenotype[4]
         numerator = ep_area*(inlever/outlever)
         denominator = ((2.0/3.0) * gape * buccal)
         self.funct_val = numerator/denominator

Micropterus.notius <- c(59.9,    3.35,    22.4,    15.2,    15.5)
Archoplites.interruptus <- c(69.8,    4.48,    20.6,    12,    18.5)
Lepomis.cyanellus <- c(84.7,    4.4,    22.65,    11.8,    15)
Lepomis.humilis <- c(79.1,    4.8,    20.72,    10.4,    12.2)
Lepomis.symmetricus <- c(54,    3.75,    16.28,    7.6 ,   9.2)
Lepomis.gibbosus <- c(117.6,    6.34,    25.03,    8.8,    15.4)
     
         
SI <- function(x) #pass SI a vector with elements epax, in, out, gape, buccal
	{
		epax <- x[1]
		inlever <- x[2]
		outlever <-x[3]
		gape <-x[4]
		buccal <- x[5]
		MA <- inlever/outlever
		numerator <- epax * MA
		denominator <- 2.0 / 3.0 * gape * buccal
		return(numerator/denominator)
	}
	
library(pastecs)
species <- read.table('~/Dropbox/dualevolve stuff/centrarchid_data.txt', as.is = F, header = T)

#get SIs for all fish across inlever/outlever combos holding other variables fixed
ep <- 50.0
mean.gape <- mean(species$Gapewidth_mm)
mean.buccal <- mean(species$Buccallength_mm)

min.inlever <- min(species$Lin_mm)
max.inlever <- max(species$Lin_mm)
min.outlever <- min(species$Lout_mm)
max.out <- max(species$Lout_mm)

SI(Micropterus.notius)
library(cubature)
adaptIntegrate(SI, c(50, 2, 20, 10, 10), c(60, 4, 30, 20, 20)) #this finds the integral for the entire space. What if we want the integral when SI is constrained to a particular value?

adaptIntegrate(f, lowerLimit, upperLimit, ..., tol = 1e-05, fDim = 1,
               maxEval = 0, absError=0, doChecking=FALSE)
	