class _Link(object):
    def __init__(self,val):
        self.data=val
        self.next=None

class LinkedList(object):
    def __init__(self,in_list=None):
        """
        params:
        =======
        head : optional initial data for linked list
        input_list : optional parameter.  if specified, list will be converted to linked list
        """
        self.head=None
        self.tail=None
        if in_list is not None:
            for item in in_list:
                self.new_link(item)

    def iterate(self,yieldNode=False):
        curr = self.head
        while curr is not None:
            temp = curr
            curr = curr.next
            if yieldNode: 
                yield temp
            else:
                yield temp.data
  
    def new_link(self,val):
        newlink=_Link(val)
        if self.head == None:
            self.head=newlink
        if self.tail != None:
            self.tail.next = newlink
        self.tail=newlink

        
    def pop(self,index=0):
        prev=None
        curr=self.head
        i=0
        while curr!=None and i<index:
            prev=curr
            curr=curr.next
            i+=1
        if prev==None:
            self.head=curr.next
            return curr.data
        else:
            prev.next=curr.next
            return curr.data
