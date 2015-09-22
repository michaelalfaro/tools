#! usr/bin/env python

import subprocess


lamcon = 'contrasts/lamcon'
betacon = 'contrasts/betacon'


for i in range(100):
	print i
 	lamstring = lamcon + str(i) + '.txt'
 	betastring = betacon + str(i) + '.txt'
 	#print fstring
	#subprocess.call('./rateshiftcombined')
	cstring = './rateshiftcombined\n' + 'cp -r ' + 'lambdaContrasts.txt ' + lamstring
	cstring = cstring + '\n' + 'cp -r ' + 'betaContrasts.txt ' + betastring
	subprocess.call(cstring, shell=True)
	#print cstring
	#subprocess.call(cstring)

#burn = 4000



#for i in range(len(infiles)):
#	print i

appname = './computeMeanBranchLengths '




#for i in range(len(infiles)):
#	mystring = appname + infiles[i] + ' ' + mtrees[i] + ' ' + str(burn)
#	print mystring
#	subprocess.call(mystring, shell = True)



 






 