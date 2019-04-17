import unittest
import cylinder1 as c
import numpy as np 

class TestCylinder(unittest.TestCase):
    def setUp(self):
        self.cylinders = [c.Cylinder([1,2,3],[4,5,2],1,0,4), c.Cylinder([6,7,8],[9,10,11],9,3,4), c.Cylinder([11,12,13],[14,15,4],9,2,3)] 
        self.nodes = [c.Node(x) for x in self.cylinders]
        self.hr = c.CylinderHierarchy()
        self.cs = c.CylinderHierarchy()
        rootnode = c.Node(c.Cylinder([11,12,13],[14,15,4],9,2,3), left=1, right=16)
        node1 = c.Node(c.Cylinder([11,12,13],[14,15,4],9,2,3), left=2, right = 13)
        node2 = c.Node(c.Cylinder([11,12,13],[14,15,4],9,2,3), left=3, right = 4)
        node3 = c.Node(c.Cylinder([11,12,13],[14,15,4],9,2,3), left=5, right = 10)
        node4 = c.Node(c.Cylinder([11,12,13],[14,15,4],9,2,3), left=6, right = 7)
        node5 = c.Node(c.Cylinder([11,12,13],[14,15,4],9,2,3), left=8, right = 9)
        node6 = c.Node(c.Cylinder([11,12,13],[14,15,4],9,2,3), left=11, right = 12)
        node7 = c.Node(c.Cylinder([11,12,13],[14,15,4],9,2,3), left=14, right = 15)
        self.cs.nodes = [rootnode,node1,node2,node3,node4,node5,node6,node7]
        self.c1 = c.Cylinder(np.array([0,0,0]),np.array([0,0,1]),1,0,9)
        self.c2 = c.Cylinder(np.array([5,5,0]),np.array([1,0,0]),1,-9,9)
    def test_nodeisleaf(self):
        node = self.nodes[0]
        node.left=1
        node.right=2
        self.assertTrue(node.is_leaf_node, 'Is leaf node not working for node instance')
        node.left=1
        node.right=10
        self.assertFalse(node.is_leaf_node, 'Is leaf node not working for node instance')
    def test_addroot(self):
        self.hr.add_root(self.nodes[0])
        self.assertEqual(self.hr.nodes[0].left, 1)
        self.assertEqual(self.hr.nodes[0].right, 2)
        self.assertEqual(len(self.hr.nodes), 1)
        self.hr.nodes=[]
        rootnode=c.Node(c.Cylinder([11,12,13],[14,15,4],9,2,3))
        node1=c.Node(c.Cylinder([11,12,13],[14,15,4],9,2,3))
        node2=c.Node(c.Cylinder([11,12,13],[14,15,4],9,2,3))
        node3=c.Node(c.Cylinder([11,12,13],[14,15,4],9,2,3))
        oldroot=c.Node(c.Cylinder([11,12,13],[14,15,4],9,2,3))
        oldroot.left=1
        oldroot.right=8
        node1.left=2
        node1.right=3
        node2.left=4
        node2.right=5
        node3.left=6
        node3.right=7
        self.hr.nodes=[node1,oldroot,node2,node3]
        self.assertEqual(len(self.hr.nodes),4)
        self.hr.add_root(rootnode)
        self.assertEqual(node1.left,3)
        self.assertEqual(node1.right,4)
        self.assertEqual(oldroot.right,9)
        self.assertEqual(oldroot.left,2)
        currut=None
        for item in self.hr.nodes:
            if self.hr.is_root_node(item):
                currut=item
        self.assertEqual(currut.left,1)
        self.assertEqual(currut.right,10)
    def test_getsiblings(self):
        siblings = self.cs.get_siblings(self.cs.nodes[2],self_include=True)
        self.assertEqual(len(siblings),3)
        self.assertIn(self.cs.nodes[2], siblings)
        self.assertIn(self.cs.nodes[3], siblings)
        self.assertIn(self.cs.nodes[6], siblings)
        siblings_ns = self.cs.get_siblings(self.cs.nodes[2],self_include=False)
        self.assertEqual(len(siblings_ns),2)
        self.assertIn(self.cs.nodes[3], siblings_ns)
        self.assertIn(self.cs.nodes[6], siblings_ns)
        siblings_ns = self.cs.get_siblings(self.cs.nodes[4],self_include=True)
        self.assertEqual(len(siblings_ns),2)
        self.assertIn(self.cs.nodes[4], siblings_ns)
        self.assertIn(self.cs.nodes[5], siblings_ns)
    def test_addchild(self):
        newnode=c.Node(c.Cylinder([11,12,13],[14,15,4],9,2,3), left=1, right = 1)
        self.cs.add_child(self.cs.nodes[4],newnode)
        self.assertEqual(self.cs.nodes[0].left,1)
        self.assertEqual(self.cs.nodes[0].right,18)
        self.assertEqual(len(self.cs.nodes),9)
    def test_insertnode(self):
        self.assertEqual(len(self.cs.nodes),8)
        newnode=c.Node(c.Cylinder([11,12,13],[14,15,4],9,2,3), left=1, right=1)
        self.cs.insert_node(self.cs.nodes[3],newnode,side='left')
        self.assertEqual(len(self.cs.nodes),9)
        self.assertEqual(self.cs.nodes[0].right,18)
        newnode=c.Node(c.Cylinder([11,12,13],[14,15,4],9,2,3), left=1, right=1)
        self.cs.insert_node(self.cs.nodes[3],newnode,side='right')
        self.assertEqual(self.cs.nodes[0].right,20)
        #pool=self.cs.get_siblings(self.cs.nodesp[2],self_include=True)
        #self.assertEqual(len(pool),4)
    def test_deletenode(self):
        self.cs.delete_node(self.cs.nodes[3])
        self.assertEqual(self.cs.nodes[0].right,10)
        self.assertEqual(len(self.cs.nodes),5)
    def test_getallchildren(self):
        children = self.cs.get_all_children(self.cs.nodes[0], self_include=True)
        self.assertEqual(len(children), len(self.cs.nodes))
        children = self.cs.get_all_children(self.cs.nodes[0], self_include=False)
        self.assertEqual(len(children), len(self.cs.nodes)-1)
    def test_forceinsert(self):
        newnode=c.Node(c.Cylinder([11,12,13],[14,15,4],9,2,3), left=1, right=1)
        self.cs.force_insert_node(self.cs.nodes[0],newnode)
        rootnode=self.cs.root_node
        self.assertEqual(rootnode.left,1)
        self.assertEqual(rootnode.right,18)
    def test_getroot(self):
        root=self.cs.root_node
        self.assertEqual(root,self.cs.nodes[0])
    def test_cydistance(self):
        res = c.cydistance(self.c1,self.c2)
        if abs(res - 3.0)<1.0e-6:
            self.assertTrue(True)
        else:
            self.assertTrue(False)


def main():
    unittest.main()

if __name__ == '__main__':
    main()       
        
    

