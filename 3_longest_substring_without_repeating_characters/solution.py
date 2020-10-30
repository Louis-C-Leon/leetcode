class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        length = 0
        start = 0
        end = 0
        chars = set()
        while end < len(s):
            if s[end] in chars:
                chars.remove(s[start])
                start += 1
            else:
                chars.add(s[end])
                end += 1
                length = max(length, end - start)

        return length
