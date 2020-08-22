class Solution(object):
    def sortIndices(self, A):
        """"
        :type A: List[int]
        :rtyle: List[int]
        """
        def getVal(idx):
            return A[idx]
        
        indices = range(len(A))
        return sorted(indices, key=getVal)
    
    def maxWidthRamp(self, A):
        """
        :type A: List[int]
        :rtype: int
        """
        sorted = self.sortIndices(A)
        min_idx = len(sorted)
        answer = 0
        for idx in range(len(sorted)):
            answer = max(answer, sorted[idx] - min_idx)
            min_idx = min(min_idx, sorted[idx])
            
        return answer
