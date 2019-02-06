from treelib import Node, Tree
from TreeBuilder import TreeBuilder


class ComparisonTree:

    def __init__(self, *, run_mode):
        self.builder = TreeBuilder()
        self.run_mode = run_mode

        if run_mode:
            dictandtree = self.builder.buildTree("simbad_raw.csv")
            self.tree = dictandtree[0]
            self.dict = dictandtree[1]
        else:
            self.tree = self.builder.buildTestTree()

    def showTree(self):
        '''
        Allows ComparisonTree user to call Tree show() function more easily.
        '''
        self.tree.show()

    def areSiblings(self, firstNodeId, secNodeId):
        '''
        This function will return True if two nodes are siblings
        in the tree provided. It will return False otherwise.
        '''
        if self.run_mode:
            print("Run Mode: Enabled. Converting nid's to SIMBAD entries.")
            firstNodeId = self.dict[firstNodeId]
            secNodeId = self.dict[secNodeId]
        else:
            print("Test variable is set, using literal id's.")

        siblings = self.tree.siblings(firstNodeId)

        for s in siblings:
            if s.identifier == secNodeId:
                return True
        return False

    def isParentOf(self, firstNodeId, secNodeId):
        '''
        This method will return True if the first node is the parent of the
        second. It will return False otherwise.
        '''
        if self.run_mode:
            print("Run Mode: Enabled. Converting nid's to SIMBAD entries.")
            firstNodeId = self.dict[firstNodeId]
            secNodeId = self.dict[secNodeId]
        else:
            print("Test variable is set, using literal id's.")

        parent = self.tree.parent(secNodeId)

        # if second node has no parent
        if (parent == None):
            return False

        return parent.identifier == firstNodeId

    def isOfType(self, firstNodeId, secNodeId):
        '''
        This method will return True if the first node is a descendent of the
        second (ie. if it is the the same type). It will return False otherwise.
        '''
        if self.run_mode:
            print("Run Mode: Enabled. Converting nid's to SIMBAD entries.")
            firstNodeId = self.dict[firstNodeId]
            secNodeId = self.dict[secNodeId]
        else:
            print("Test variable is set, using literal id's.")

        subtree = self.tree.subtree(secNodeId)

        return subtree.contains(firstNodeId)

    def test(self, firstNodeId, secNodeId):
        return areSiblings(firstNodeId, secNodeId)

        if self.run_mode:
            print("Run Mode: Enabled. Converting nid's to SIMBAD entries.")
            firstNodeId = self.dict[firstNodeId]
            secNodeId = self.dict[secNodeId]
        else:
            print("Test variable is set, using literal id's.")

    def shareCommonAncestor(self, firstNodeId, secNodeId):
        '''
        This method will return True if the nodes corresponding to the given
        nodeIDs share a common ancestor. Return False othewise.
        '''
        if self.run_mode:
            print("Run Mode: Enabled. Converting nid's to SIMBAD entries.")
            firstNodeId = self.dict[firstNodeId]
            secNodeId = self.dict[secNodeId]
        else:
            print("Test variable is set, using literal id's.")

        first_node = self.tree.get_node(firstNodeId)
        sec_node = self.tree.get_node(secNodeId)

        # If the nodes are at the top level they do not share a common
        # ancestor. ie. Star and Galaxy. and their parent is root.
        if (self.tree.parent(firstNodeId).is_root() or
                self.tree.parent(secNodeId).is_root()):
            return False
        else:
            return True

        # Otherwise traverse up to look for common ancestor.
        current_node_id = firstNodeId
        p = self.tree.parent(current_node_id)
        while (p and not p.identifier == "root"):
            if (self.isOfType(secNodeId, p.identifier)):
                return True
            else:
                p = self.tree.parent(p.identifier)
        return False
