class Solution(object):
    
    
    def groupThePeople(self, groupSizes):
        """
        :type groupSizes: List[int]
        :rtype: List[List[int]]
        """
        output = []
        groups = {}
        for i in range(len(groupSizes)):
            size = groupSizes[i]
            if size in groups:
                groups[size].append(i)
            else:
                groups[size] = [i]
                
        for size in groups:
            idx = 0
            group = groups[size]
            while(len(group) > 0):
                subgroup = group[idx:idx + size]
                group = group[idx + size:]
                output.append(subgroup)
        
        return output
