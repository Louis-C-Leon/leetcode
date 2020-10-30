# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def addTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
        carry = 0
        head_node = ListNode()
        current = head_node
        while l1 or l2 or carry:
            total = 0
            if l1:
                total = total + l1.val
                l1 = l1.next
            if l2:
                total = total + l2.val
                l2 = l2.next
            total = total + carry
            digit = total % 10
            carry = total // 10
            current.val = digit
            if l1 or l2 or carry:
                current.next = ListNode()
                current = current.next

        return head_node

