class Solution(object):
    def maxIncreaseKeepingSkyline(self, grid):
        """
        :type grid: List[List[int]]
        :rtype: int
        """
        row_max = []
        col_max = []
        for idx in range(len(grid)):
            row = grid[idx]
            row_max.append(max(row))
            col = []
            for row in grid:
                col.append(row[idx])
            col_max.append(max(col))
        
        total = 0
        for rIdx in range(len(grid)):
            for cIdx in range(len(grid)):
                height = min(row_max[rIdx], col_max[cIdx])
                total = total + height - grid[rIdx][cIdx]
        return total        

