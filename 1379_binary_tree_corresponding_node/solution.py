# Definition for a binary tree node.
# class TreeNode(object):
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution(object):
    def bfs(self, node, target):
        """
        :type node: TreeNode
        :type target: TreeNode
        :rtype: TreeNode
        """
        current = node
        queue = [node]
        while (len(queue) > 0 and current.val != target.val):
            current = queue.pop(0)
            if (current.left != None):
                queue.append(current.left)
            if (current.right != None):
                queue.append(current.right)
        return current


<< << << < HEAD

== == == =

>>>>>> > 21bb8bf94b167aacfe6b5af85bd614c655e83723


def getTargetCopy(self, original, cloned, target):
    """
        :type original: TreeNode
        :type cloned: TreeNode
        :type target: TreeNode
        :rtype: TreeNode
        """


<< << << < HEAD
res = self.bfs(cloned, target)
return res
== == == =
result = self.bfs(cloned, target)
return result

>>>>>> > 21bb8bf94b167aacfe6b5af85bd614c655e83723
