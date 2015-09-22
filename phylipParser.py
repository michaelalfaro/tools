#simple phylip parser
#need to swap taxon names in phylip formatted file with another list which contains exact same taxon name PLUS ranks

#should rename this. phylip parsing is easy. the useful thing this is doing is replacing old names with new names


#first read in file
filename = "4c4_cytb_rag1_rhodopsin.names.phy"
data = {}
ff = open(filename, 'r')
phy = ff.readlines()
#line 1 is # species, # sites
species, sites = phy[0].split()
#taxa, seqs = [],[]
#go through each line. split on space. place element 0 in names, element 1 in seqs
for i in range(1, len(phy)):
    data[phy[i].split()[0]] = phy[i].split()[1]
#may need a check that all data entries are valid. not sure if newline character is being enterd into dictionary

weird = [] #hold bad names
#going to make a new dictionary with keys 
kk = data.keys()
nd = {} #new dictionary
for name in kk:
    if(name.split('|')[2]):
        nd[name] = name.split('|')[2]
    else:
        weird.append(name)
        
#nd now contains key-value pairs of short name-rank, name



#get the original short names as a check
filename = "4c4_cytb_rag1_rhodopsin.phy"
shortnames = []
ff = open(filename, 'r')
phy = ff.readlines()
#line 1 is # species, # sites
#species, sites = phy[0].split()
#taxa, seqs = [],[]
#go through each line. split on space. place element 0 in names, element 1 in seqs
for i in range(1, len(phy)):
    shortnames.append(phy[i].split()[0])
    
    
#next get tree as object
tree = open('test.phy').readlines()[0]
#iterate through keys and search for them in tree
counter = 0
for name in shortnames:
    if tree.find(name) != -1:
        counter+=1
    else:
        print(name + 'not found')

counter
namemap = {} #hold shortnames-longnames as key-value
# now need a dictionary of short names and long names
# iter through shortnames and search for them in longnames
for name in shortnames:
    for key in data.keys():
        if key.find('|' + name +'|') != -1:
            if not namemap.has_key(name):
                namemap[name] = key
            elif namemap.has_key(name):
                print('taxon already entered\t' + name + '\tunentered value:\t' + key + '\tdict value:\t' + namemap[name])
        else:
            print("can't find " + name)
            
            
# just want names not in data.keys
kk = data.keys()
missing = []
for name in shortnames:
    if not name in kk:
        missing.append(name)
        
            




oo = set(shortnames)

ndnames = set(nd.values()) # names I created by splitting rank names
len(ndnames.values()) == len(oo)

#read in a test line


#now, can we search a line for each key?

for line in somefile:
   for key in nd.iterkeys():
       if line.



#now compare names to keys. if key contains name, replace key. need to update dictionary I think
#first compare names and keys


#to fix names in newick format
#search for name in line
#if find name in line
#replace name with name in dictionary

data = {}


