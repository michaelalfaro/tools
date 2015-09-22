##these are utilities I 
from ete2 import Tree, TreeStyle, NodeStyle, CircleFace, faces
import re
import colorsys
from numpy import random
#from __future__ import division
from collections import OrderedDict
import random
import shutil
import os

def getPamlPars(ctl):
    #extract arguments froma paml ctl file and stick them into an ordered dictionary
    pardict = OrderedDict()

    for line in ctl.splitlines():
        if line.partition("*")[0]:
            key, value = line.partition("*")[0].strip().split("=")
            #print key.strip(), value
            pardict[key.strip()] = value
    return pardict


def writeCTL(hessian, tree_title, partitions, template_ctl, run = 1):
    #writes PAML control file
    if hessian == "hessian":
        template_ctl["usedata"] = "3"
    elif hessian == "post-hessian":
        template_ctl["usedata"] = "2"
    else:
        print "\nneed information for usedata argument\n"
    number_partitions = os.path.basename(partitions).split("_")[0]
    template_ctl["seqfile"] = os.path.basename(partitions)
    template_ctl["treefile"] = tree_title
    n1 = number_partitions + "_partitions"
    n2 = tree_title
    n3 = "_run_{}".format(run)
    template_ctl["outfile"] = "{}_{}_{}.out".format(n1, n2, n3)
    template_ctl["ndata"] = number_partitions
    #print "\nNew file"
    print len(template_ctl.keys())
    ctl_name = "ctl_{}_{}_{}_{}.ctl".format(hessian, n3, n1, n2 )

    #helper function to write ctl files, takes a dictionary of parameters to update (pars)
    temp_ctl = r"""
              seed = {seed}
           seqfile = {seqfile}
          treefile = {treefile}
           outfile = {outfile}

             ndata = {ndata}
           seqtype = {seqtype}    * 0: nucleotides; 1:codons; 2:AAs
           usedata = {usedata}    * 0: no data; 1:seq like; 2:normal approximation; 3:out.BV (in.BV)
             clock = {clock}    * 1: global clock; 2: independent rates; 3: correlated rates
           RootAge = {RootAge}  * safe constraint on root age, used if no fossil for root.

             model = {model}    * 0:JC69, 1:K80, 2:F81, 3:F84, 4:HKY85
             alpha = {alpha}    * alpha for gamma rates at sites
             ncatG = {ncatG}   * No. categories in discrete gamma

         cleandata = {cleandata}    * remove sites with ambiguity data (1:yes, 0:no)?

           BDparas = {BDparas}   * birth, death, sampling
       kappa_gamma = {kappa_gamma}      * gamma prior for kappa
       alpha_gamma = {alpha_gamma}      * gamma prior for alpha

       rgene_gamma = {rgene_gamma}    * gammaDir prior for rate for genes
      sigma2_gamma = {sigma2_gamma}  * gammaDir prior for sigma^2     (for clock=2 or 3)

          finetune = {finetune} * auto (0 or 1): times, rates, mixing, paras, RateParas, FossilErr

             print = {print}
            burnin = {burnin}
          sampfreq = {sampfreq}
           nsample = {nsample}

    *** Note: Make your window wider (100 columns) before running the program.
    """
    
    populated_ctl = temp_ctl.format(**template_ctl)
    
    with open(ctl_name, "w") as ff:
            ff.write(populated_ctl) 
            ff.close()


def makeGroups(tree, taxonList, staticColor = None):
    #pass in tree, list of taxa subtending node, return list with mrca of that subclade + all taxa in it, and passes along a user defined color if passed in
    subClade = tree.get_common_ancestor(taxonList)
    return [subClade.nodeid, subClade, staticColor]
###label all nodes of interest 

def random_color(h=None, l=None, s=None):
    if h is None:
        h = random.random()
    if l is None:
        l = random.random()
    if s is None:
        s = random.random()
    return hls2hex(h, l, s)

def rgb2hex(rgb):
    return '#%02x%02x%02x' % rgb

def hls2hex(h, l, s):
    return rgb2hex( tuple(map(lambda x: int(x*255), colorsys.hls_to_rgb(h, l, s))))


def rankify(tree, rankset):
    #call this to add rank labels to the nodes of a tree
    for node in tree.traverse():
        print node.name
        if node.name in rankset:
            family = rankset[node.name]
            print family
            print type(node)
            node.add_face( faces.TextFace(family, ftype="Arial", fsize=12, fgcolor="red"), 0, position = "branch-right" )
    return tree        

def facify(tree, imagedict):
    #call this to add images to a tree if you have a dictionary of images matching nodes
    for node in tree.traverse():
        if node.name in imagedict:
            #print "{} in face_dict ".format(node.name)
            node.add_face(imagedict[node.name], column  = 1, position = "branch-right")

def mylayout(node, number_nodes=True, label_support_with_numbers=False):
    #width is set to 2 to increase visibility in large trees when exporting
    node.img_style["hz_line_width"]=4
    node.img_style["vt_line_width"]=4
    #counter2 = 0
    # If node is a leaf, add the nodes name and a its scientific
    # name
    if node.is_leaf():
        node.img_style["size"] = 0
        color = "#000000"
        faces.add_face_to_node( faces.TextFace(node.name, ftype="Arial", fsize=20, fstyle = "italic", fgcolor=color), node, 0 )
        #try adding the family to the tip as well
        #if node.name in ranks:
            #family = ranks[node.name]
            #faces.add_face_to_node( faces.TextFace(family, ftype="Arial", fsize=12, fgcolor="red"), node, 0 )
        if node.up is None:
            node.img_style["size"]=0
            node.dist = 0.35 # you may need to change this value to fit the aspect of your tree
            node.img_style["hz_line_color"] = "#ffffff"
            if UNROOTED:
                node.img_style["vt_line_type"] = 0.001
        
        #if node.name in face_dict:
        #    print "{} in face_dict ".format(node.name)
        #    faces.add_face_to_node(face_dict[node.name], node, column  = 1, position = "branch-right") #WOuld relly like the image to appear on outside of tre
            #print "found {} matches".format(counter2)
            
            #node.img_style["size"] = 16
            #node.img_style["shape"] = "sphere"
            #node.img_style["fgcolor"] = "#AA0000"

        # Sets the style of leaf nodes
        #node.img_style["size"] = 12
        #node.img_style["shape"] = "circle"
    #If node is an internal node
    else:
        #support_face = CircleFace(radius=100, color="Thistle", style="circle")    
        #support_face.opacity = 0.3
        #faces.add_face_to_node(support_face, node, 0, position="float")
        
        ###make bubble proportional to boostrap support
        # Creates a sphere face whose size is proportional to node's
        # feature "weight"
        #C = CircleFace(radius=node.support, color="Black", style="sphere")
        # Let's make the sphere transparent 
        #C.opacity = 1.0
        # And place as a float face over the tree
        #faces.add_face_to_node(C, node, 0, position="float")
      
        #print "current node id :" + str(node.nodeid)
        #print "is node in BG_COLORS? " + str(node.nodeid) in BG_COLORS
        #if node.nodeid in BG_COLORS:
            #print "this node is in colors" + node.nodeid
            #node.img_style["bgcolor"] = BG_COLORS[str(node.nodeid)]
            #print BG_COLORS[node.nodeid]
        # Sets the style of internal nodes
        node.img_style["size"] = 0
        #node.img_style["shape"] = "circle"
        #node.img_style["fgcolor"] = "#000000"
        
        num = node.nodenumber
        if number_nodes == True:
            faces.add_face_to_node(faces.TextFace(num, ftype="Arial", fsize=12, fgcolor="purple"), node, 0, position = "branch-right")
        # is the internal node an order?
        if node.order:
            faces.add_face_to_node(faces.TextFace(node.order, ftype="Arial", fsize=25, fgcolor="#black"), node, 0)
        
        if label_support_with_numbers:
            faces.add_face_to_node(faces.TextFace(node.support, ftype="Arial", fsize=10, fgcolor="black"), node, 0, position = "branch-top")
            if node.bootstrap:
                faces.add_face_to_node(faces.TextFace(node.bootstrap, ftype="Arial", fsize=10, fgcolor="grey"), node, 0, position = "branch-bottom")
        makeSupportSymbols(node, node.bootstrap)   

def calibrations_layout(node):
    #width is set to 2 to increase visibility in large trees when exporting
    node.img_style["hz_line_width"]=4
    node.img_style["vt_line_width"]=4
    
    if node.is_leaf():
        node.img_style["size"] = 0
        color = "#000000" # these two lines hide the default node symbol for tips. They are replaced by the textface below
        faces.add_face_to_node( faces.TextFace(node.name, ftype="Arial", fsize=20, fstyle = "italic", fgcolor=color), node, 0 )
        #try adding the family to the tip as well
        #if node.name in ranks: # note that ranks is a dictionary that has not been passed in to the function. Could be trouble!
            #family = ranks[node.name]
            #faces.add_face_to_node( faces.TextFace(family, ftype="Arial", fsize=12, fgcolor="red"), node, 0 )
        if node.up is None:
            node.img_style["size"]=0
            node.dist = 0.35 # you may need to change this value to fit the aspect of your tree
            node.img_style["hz_line_color"] = "#ffffff"
            if UNROOTED:
                node.img_style["vt_line_type"] = 0.001
        #add faces to nodes that have images. face_dict is defined outside this function too....
        #if node.name in face_dict:
            #faces.add_face_to_node(face_dict[node.name], node, column  = 1, position = "branch-right")

    #If node is an internal node
    else:
        #color the node if is is a major clade
        #if node.nodeid in BG_COLORS:
            #node.img_style["bgcolor"] = BG_COLORS[str(node.nodeid)]
        # Sets the style of internal nodes
        node.img_style["size"] = 0
        #node.img_style["shape"] = "circle"
        #node.img_style["fgcolor"] = "#000000"
        
        #label internal nodes with nodenumber
        num = node.nodenumber
        faces.add_face_to_node(faces.TextFace(num, ftype="Arial", fsize=16, fgcolor="purple"), node, 0, position = "branch-right")
        # add paml calibrations
        if "paml_cal" in node.features:
            faces.add_face_to_node(faces.TextFace(node.paml_cal, ftype="Arial", fsize=16, fgcolor="black"), node, 0, position = "branch-right")
        if "raw_cal" in node.features:
            faces.add_face_to_node(faces.TextFace(node.raw_cal, ftype="Arial", fsize=16, fgcolor="orange"), node, 0, position = "branch-right")
            


    
    
  #  for node in tt.traverse("postorder"):
   # node.add_features( nodeid = str(uuid.uuid1() ) )
   # node.add_features( nodenumber = str(counter) )# for calibrations
    #node.add_features( order = None)
            
def attachSupport(target_tree, source_tree):
# this function takes the support values from a source tree and puts them on the common nodes of the target tree
    sourceclades = {}
    for node in source_tree.traverse("preorder"):
        if not node.is_leaf():
            kids = (node.get_leaves())
            labels = frozenset([kid.name for kid in kids])            
            support = node.support 
            sourceclades[(labels)] = support
    #now traverse the target tree
    for node in target_tree.traverse("preorder"):
        if not node.is_leaf():
            kids = (node.get_leaves())
            node_hash = frozenset([kid.name for kid in kids])
            node.add_features( bootstrap = sourceclades.get(node_hash) )# for calibrations
            #print node.support, node.bootstrap, node_hash, "\t", len(node_hash), "\n", 
    #return sourceclades
    
def makeSupportSymbols(node, secondary_support):
    #function to make circle with size scaled to base support value and color of circle scaled to the level of the second support value
    opacity = 0.01
    # Let's make the sphere transparent 
    if secondary_support == None:
        circle_color = "Grey"
        opacity = 1.0
        factor = 6
    elif secondary_support >=95.0:
        circle_color = "Black"
        opacity = 1.0
        factor = 10
    elif secondary_support >=70.0:
        circle_color = "Black"
        opacity = 1.0
        factor = 8
    elif secondary_support <70.0:
        circle_color = "Black"
        opacity = 1.0
        factor = 6
    else:
        print "secondary value unexpected: {}".format(secondary_support())
        circle_color = "Red"
        opacity = 1.0
    #circle_color = "#33343E" #a black from the pomacanthus drawing
    #print "color is {}, bootstrap is {}, opacity is {}".format(color, secondary_support, opacity)
    support_face = CircleFace(radius=node.support * factor, color=circle_color, style="circle")    
    support_face.opacity = opacity
    faces.add_face_to_node(support_face, node, 0, position="float-behind")

def addPamlCalibration(lower = None, upper = None, desired_time_scale = 10.0):
    #given an upper and/or lower bound, add a calibration feature to the tree that matches the format needed for mcmc
    #time_scale is the number of MY that 1 time unit will represent in the mcmctree analysis
    #defaults to 1 unit = 10 MY
    if lower:
        scaled_lower = lower / desired_time_scale
    if upper:
        scaled_upper = upper / desired_time_scale
    calibration_str = ""
    """
    if lower and str(lower) != "nan":
        calibration_str += "L({},0.1,1.0,1e-300)".format(lower / desired_time_scale) #for hard lower bound
    if upper and str(upper) != "nan":
        calibration_str += "<{}".format(upper / desired_time_scale )   
    """
    if lower and upper and str(lower) != "nan" and str(upper) != "nan":
        calibration_str = "'B({},{},1e-300,0.05)'".format(scaled_lower, scaled_upper)
    elif not upper and lower and str(lower) != "nan":
    #lower and str(lower) != "nan" and not upper:
        calibration_str = "'L({},0.1,0.5,1e-300)'".format(scaled_lower)
    elif not lower and upper and str(upper) != "nan":
        calibration_str = "'U({}, 0.05)'".format(scaled_upper)
        #print "the cali strin is {}".format(calibration_str)
    return calibration_str


def makePamlTree(treestring):
    #takes a tree, removes NHX annotation but leaves the calibration specification for PAML
    pattern1 = r"\[&&NHX:nodenumber=\d+\]"
    #pattern2 = r"\[&&NHX:nodenumber=\d+:\w+_\w+=([()Le<>\d+.]+)]"
    pattern2 = r"\[&&NHX:nodenumber=\d+:\w+_\w+=('[LB_\d.e-]+')\]"
    pp2 = re.compile(pattern2)
    pattern3 = r"('[LUB])_([\d._e-]+)_(')"
    pp3 = re.compile(pattern3)
   # pattern4
    #print "\n here is the treestring\n", treestring
    temptree = re.sub(pattern1, "", treestring)
    temptree2 = pp2.sub(r"\1", temptree)
    temptree3 = pp3.sub(r"\1(\2)\3", temptree2)
    #temptree4 = 
    finaltree = temptree3.replace("_", ",")
    print "\n\n\n\nthis is finaltree\n", finaltree
    return finaltree


"""
def annotatePaml(target_tree, scheme):
    # tree to use for annotations and a scheme dictionary with node numbers (matching tree) and lower/upper bounds as values
    for calibration_node_number in scheme:
        
        lower, upper = scheme[calibration_node_number]
        print "node is {} lower is {} upper is {}".format(calibration_node_number, lower, upper)
        calibration_text = addPamlCalibration(lower, upper) #get the calibration string
        print "calibration text is {}".format(calibration_text)
        target_calibration_node = target_tree.search_nodes(nodenumber = str(calibration_node_number))
        #print target[0].nodenumber, calibration_text
        target_calibration_node[0].add_features( paml_cal = calibration_text )
    calibration_tree_nhx = target_tree.write(features = ["nodenumber", "paml_cal"], format = 9,format_root_node=True)
    return makePamlTree(calibration_tree_nhx) #title of the tree?
"""
def annotatePaml(target_tree, scheme, raw = False):
    # tree to use for annotations and a scheme dictionary with node numbers (matching tree) and lower/upper bounds as values
    for calibration_node_number in scheme:
        #print calibration_node_number
        lower, upper = scheme[calibration_node_number]
        print "\n in annotatePaml"
        print "node is {} lower is {} upper is {}\t".format(calibration_node_number, lower, upper)

        if str(lower) == "nan":
            lower = None
        if str(upper) == "nan":
            upper = None
        #print "\n", lower, upper
        

        calibration_text = addPamlCalibration(lower, upper) #get the calibration string
        print "calibration text is {}".format(calibration_text)
        target_calibration_node = target_tree.search_nodes(nodenumber = str(calibration_node_number))
        print "targ cali node is {} and text is {}\n".format(target_calibration_node[0].nodenumber, calibration_text)
        target_calibration_node[0].add_features( paml_cal = str(calibration_text) )
        if raw == True:
            print "raw is true"
            rawtxt = "Lower:{} Upper:{}".format(str(lower), str(upper))
            print "the raw txt is: {}".format(rawtxt)
            target_calibration_node[0].add_features( raw_cal = str(rawtxt) )
            
    calibration_tree_nhx = target_tree.write(features = ['nodenumber', "raw_cal", "paml_cal"], format = 9,format_root_node=True)
    print "***this is the nhx tree***\n\n" + calibration_tree_nhx
    return makePamlTree(calibration_tree_nhx) #title of the tree?    


def annotateAndReturn(target_tree, scheme, raw = False):
    # gives the annoated tree in ete2 format
    for calibration_node_number in scheme:
        #print calibration_node_number
        lower, upper = scheme[calibration_node_number]
        print "\n in annotatePaml"
        print "node is {} lower is {} upper is {}\t".format(calibration_node_number, lower, upper)

        if str(lower) == "nan":
            lower = None
        if str(upper) == "nan":
            upper = None
        #print "\n", lower, upper
        

        calibration_text = addPamlCalibration(lower, upper) #get the calibration string
        print "calibration text is {}".format(calibration_text)
        target_calibration_node = target_tree.search_nodes(nodenumber = str(calibration_node_number))
        print "targ cali node is {} and text is {}\n".format(target_calibration_node[0].nodenumber, calibration_text)
        target_calibration_node[0].add_features( paml_cal = str(calibration_text) )
        if raw == True:
            print "raw is true"
            rawtxt = "Lower:{} Upper:{}".format(str(lower), str(upper))
            print "the raw txt is: {}".format(rawtxt)
            target_calibration_node[0].add_features( raw_cal = str(rawtxt) )
            
    #calibration_tree_nhx = tt.write(features = ['nodenumber', "raw_cal", "paml_cal"], format = 9,format_root_node=True)
    return target_tree
    #return makePamlTree(calibration_tree_nhx) #title of the tree?   

def writePamlTree(treestr, title, numtaxa, numtrees, return_tree = False):
    #converts names back to match alignment, prepares a file for mcmctree
    #also returns the tree as a string
    t1 = treestr.lower().replace(" ", "_")
    t2 = t1.replace("takifugu_ocellatus","takifugu_occelatus")
    t3 = t2.replace("coruscum","coruscum2")
    t4 = t3.replace("'b", "'B")
    t4 = t4.replace("'u", "'U")
    t4 = t4.replace("'l", "'L")
    with open(title, 'w') as the_file:
        the_file.write("{} {} \n".format(numtaxa, numtrees))
        the_file.write(t4)
        the_file.close()
    if return_tree:
        return t4

def copyPamlAlignment(alignpath, writepath):
    shutil.copy(alignpath, writepath)

def writePamlCtl(hessian, tree_title, partitions, template_ctl):
    if hessian == "hessian":
        template_ctl["usedata"] = "3"
    elif hessian == "post-hessian":
        template_ctl["usedata"] = "2"
    else:
        print "\nneed information for usedata argument\n"
    number_partitions = os.path.basename(partitions).split("_")[0]
    template_ctl["seqfile"] = os.path.basename(partitions)
    template_ctl["treefile"] = tree_title
    n1 = number_partitions + "_partitions"
    n2 = tree_title
    template_ctl["outfile"] = "{}_{}.out".format(n1, n2)
    template_ctl["ndata"] = number_partitions
    #print "\nNew file"
    print len(template_ctl.keys())
    ctl_name = "ctl_{}_{}_{}.ctl".format(hes, n1, n2 )
    with open(ctl_name, "w") as ff:
        for key, value in template_ctl.items():
            line = key + " = " + str(value) + "\n"
            ff.writelines(line) 
    ff.close()


def setTreeStyle(style, layoutfunction):
    #consolidate options for showing trees
    #pass in string "circle" or "rect" and a layout function
    I = TreeStyle()
    if style == "circle":
        I.tree_width = 1200
        I.layout_fn = layoutfunction
        I.show_branch_length = False
        #I.show_branch_support = True
        I.show_leaf_name = False
        I.mode = "c"
        I.force_topology = True
        #I.legend_position = 3
        I.extra_branch_line_type = 1
        I.guiding_lines_type = 1
        I.guiding_lines_color = "#666666"
        I.extra_branch_line_color = "#666666"
        I.optimal_scale_level = "full"
        I.root_opening_factor = 0
        
    elif style =="rect":
        I = TreeStyle()
        I.layout_fn = layoutfunction
        I.show_leaf_name = False
        I.force_topology = True
        I.optimal_scale_level = "semi"
        
    else:
        I.layout_fn = layoutfunction
        I.show_leaf_name = False
        I.force_topology = True
        I.optimal_scale_level = "semi"
    return I

    

    