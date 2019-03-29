from treelib import Node, Tree
from astropy.table import Table, Column
import numpy as np
from .tree_builder import TreeBuilder
from .data_controller import DataController
import logging


class ComparisonTree:

    def __init__(self, *, run_mode):
        self.builder = TreeBuilder()
        self.run_mode = run_mode

        if run_mode:
            logging.info("Run Mode: Enabled. Converting numeric\
             id's to SIMBAD entries.")
            dictandtree = self.builder.buildTree("data/simbad_raw.csv")
            self.tree = dictandtree[0]
            self.dict = dictandtree[1]
        else:
            self.tree = self.builder.buildTestTree()

    def showtree(self):
        '''
        Allows ComparisonTree user to call Tree show() function more easily.
        '''
        self.tree.show()

    def are_direct_match(self, Type_N, Type_S):
        return Type_N == Type_S

    def are_candidate_match(self, *, Type_N, Type_S):
        '''
        Maps NEDs entry to corresponding candidate (if any) and checks
        for equality with SIMBAD entry. True if equal, False otherwise.
        '''
        try:
            cmatch = DataController.candidate_match(Type_N) == Type_S
        except KeyError:
            return False

        if (cmatch):
            return True
        else:
            return False

    def are_siblings(self, firstNodeId, secNodeId):
        '''
        This function will return True if two nodes are siblings
        in the tree provided. It will return False otherwise.
        '''
        # tag->id dict has no entry for null string
        if firstNodeId == "" or secNodeId == "":
            return False

        if self.run_mode:
            firstNodeId = self.dict[firstNodeId]
            secNodeId = self.dict[secNodeId]

        if (self.tree.parent(firstNodeId).identifier == "root") or (self.tree.parent(secNodeId).identifier == "root"):
            return False

        siblings = self.tree.siblings(firstNodeId)

        for s in siblings:
            if s.identifier == secNodeId:
                return True
        return False

    def is_parent_of(self, firstNodeId, secNodeId):
        '''
        This method will return True if the first node is the parent of the
        second. It will return False otherwise.
        '''
        parent = self.tree.parent(secNodeId)

        # if second node has no parent
        if (parent == None):
            return False

        return parent.identifier == firstNodeId

    def of_type_match(self, firstNodeId, secNodeId):
        '''
        Returns True if:
        - either node is a parent of the other
        - either node is of the type of the other AND the parent is not a category object
        '''
        if firstNodeId == "" or secNodeId == "":
            return False

        if self.run_mode:
            firstNodeId = self.dict[firstNodeId]
            secNodeId = self.dict[secNodeId]

        if self.is_descendant_of(firstNodeId, secNodeId) or self.is_descendant_of(secNodeId, firstNodeId):
            return True  # Genuine ofType Match
        else:
            return False

    def is_descendant_of(self, firstNodeId, secNodeId):
        '''
        This method will return True if the first node is a descendent of the
        second. It will return False otherwise.
        '''
        # if self.run_mode:
        #    firstNodeId = self.dict[firstNodeId]
        #    secNodeId = self.dict[secNodeId]

        subtree = self.tree.subtree(secNodeId)

        return subtree.contains(firstNodeId)

    def share_common_ancestor(self, firstNodeId, secNodeId):
        '''
        This method will return True if the nodes corresponding to the given
        nodeIDs share a common ancestor. Return False othewise.
        '''
        # tag->id dict has no entry for null string
        if firstNodeId == "" or secNodeId == "":
            return False

        if self.run_mode:
            firstNodeId = self.dict[firstNodeId]
            secNodeId = self.dict[secNodeId]

        first_node = self.tree.get_node(firstNodeId)
        sec_node = self.tree.get_node(secNodeId)

        if self.is_descendant_of(firstNodeId, secNodeId) or self.is_descendant_of(secNodeId, firstNodeId):
            return True

        # If the nodes are at the top level they do not share a common
        # ancestor. ie. Star and Galaxy. and their parent is root.
        if (self.tree.parent(firstNodeId).is_root() or
                self.tree.parent(secNodeId).is_root()):
            logging.info("parent is root")
            return False

        # Otherwise traverse up to look for common ancestor.
        current_node_id = firstNodeId
        p = self.tree.parent(current_node_id)
        while (p and not p.identifier == "root"):
            logging.info("Current p is : {}".format(p))
            if (self.is_descendant_of(secNodeId, p.identifier)):
                return True
            else:
                p = self.tree.parent(p.identifier)
        return False

    def generalization_match():
        pass

    def compare_objects(self, t):
        '''
        Once you have the matched table is either generated or imported
        we need to do the comparisons between NED and SIMBAD objects.

        t - the combined table fetched or generated.
        '''
        tsize = len(t)

        cols = []
        cols.append(Column(name='Exact Match', length=tsize, dtype=bool))
        cols.append(Column(name='Candidate Match', length=tsize, dtype=bool))
        cols.append(Column(name='ofType Match', length=tsize, dtype=bool))
        cols.append(Column(name='Shared Category Match', length=tsize, dtype=bool))
        cols.append(Column(name='Non Match', length=tsize, dtype=bool))

        # Insert NED Analogues right after the Name_N column.
        t.add_column(Column(name="Type_N_Analogue", length=tsize, dtype=np.dtype(('U', 8))),
                     index=t.index_column("Type_N")+1)
        t.add_column(Column(name="Type_S_cond", length=tsize, dtype=np.dtype(('U', 8))),
                     index=t.index_column("Type_S")+1)
        t.add_columns(cols)

        for i in range(0, tsize):
            ned_analogue = DataController.ned_to_simbad(t["Type_N"][i])
            t["Type_N_Analogue"][i] = ned_analogue
            logging.debug("This is the value of Type_S being passed: {}".format(t["Type_S"][i]))
            t["Type_S_cond"][i] = DataController.simbad_long_to_small(
                t["Type_S"][i])

            if (self.are_direct_match(t["Type_N_Analogue"][i], t["Type_S_cond"][i])):
                t["Exact Match"][i] = True
                logging.info("match i={} - N: {} S: {}".format(i,
                                                               ned_analogue,
                                                               t["Type_S"][i]))
            elif (self.are_candidate_match(Type_N=t["Type_N_Analogue"][i], Type_S=t["Type_S_cond"][i])):
                t["Candidate Match"][i] = True
                logging.info("candidateMatch i={} - N: {} S: {}".format(i,
                                                                        ned_analogue,
                                                                        t["Type_S"][i]))
            elif (self.of_type_match(t["Type_N_Analogue"][i], t["Type_S_cond"][i])):
                t["ofType Match"][i] = True
                logging.info("ofType Match i={} - N: {} S: {}".format(i,
                                                                      ned_analogue,
                                                                      t["Type_S"][i]))
            elif self.share_common_ancestor(t["Type_N_Analogue"][i], t["Type_S_cond"][i]):
                t["Shared Category Match"][i] = True
                logging.info("Shared Category Match i={} - N: {} S: {}".format(i,
                                                                               ned_analogue,
                                                                               t["Type_S"][i]))
            else:
                t["Non Match"][i] = True
                logging.info("non-match i={} - N: {} S: {}".format(i,
                                                                   ned_analogue,
                                                                   t["Type_S"][i]))
        self.combined_table = t
