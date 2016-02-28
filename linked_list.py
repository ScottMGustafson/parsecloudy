class _Link(object):
    def __init__(self,val):
        self.data=val
        self._next=None
    def gonext(self):
        return self._next
    def __str__(self):
        return str(self.data)

class LinkedList(object):
    def __init__(self,in_list=None):
        """
        params:
        =======
        head : optional initial data for linked list
        input_list : optional parameter.  if specified, list will be converted 
                    to linked list
        """
        self.head=None
        self.tail=None
        if in_list is not None:
            for item in in_list:
                self.new_link(item)
  
    def new_link(self,val):
        newlink=_Link(val)
        if self.head == None:
            self.head=newlink
        if self.tail != None:
            self.tail._next = newlink
        self.tail=newlink
  
    def pop(self,index=0):
        prev=None
        curr=self.head
        i=0
        while curr!=None and i<index:
            prev=curr
            curr=curr._next
            i+=1
        if prev==None:
            self.head=curr._next
            return curr.data
        else:
            prev._next=curr._next
            return curr.data
    def __str__(self):
        curr=self.head
        s=''
        while curr:
            s+=str(curr.data)+'\n'
            curr=curr.gonext()
        return s
