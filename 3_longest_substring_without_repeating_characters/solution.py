class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        length = 0
        i = 0
        while i < len(s):
            dict = {}
            curr_len = 0
            unique = True
            while unique == True and i < len(s):
                char = s[i]
                if char in dict:
                    unique = False
                    i = dict[char] + 1
                else:
                    curr_len += 1
                    dict[char] = i
                    i += 1
            if curr_len > length:
                length = curr_len
        return length

