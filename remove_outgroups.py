#!/usr/bin/env python

#I am struggling to remove the four outgroups from this .tre file without messing up its functionality. Osmar Luiz needs this .tre file without the outgroups included in order to complete his functional trait analysis. Do you think you can somehow remove (acanthurus_olivaceus, naso_unicornis, pomacanthus_paru, Platax_orbicularis1) and send back to me ASAP? Many thanks.


import dendropy

phy = dendropy.Tree.get_from_path("FinalDatedChaetTree_no_duplicates, Jan. 4, 2016.tre", schema="nexus", extract_comment_metadata=True)

outgroups = [x.replace("_", " ") for x in "acanthurus_olivaceus naso_unicornis pomacanthus_paru Platax_orbicularis1".split(" ")]

phy2 = phy.clone(depth=2)

inclusion_set = [nd.taxon for nd in phy2.leaf_node_iter() if nd.taxon.label not in outgroups]

phy2.retain_taxa(inclusion_set)

phy2.write_to_path("FinalDatedChaetTree_no_duplicates_no_outgroups_May_2_2016.tre", schema="nexus")

