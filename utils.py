from datetime import date

def get_first_day(for_date=None):
    if for_date is None:
        for_date = date.today()

    return date(for_date.year, for_date.month, 1)

def get_next_month(for_date=None):
    if for_date is None:
        for_date = date.today()

    if for_date.month == 12:
        month = for_date.month + 1
        year = for_date.year
    else:
        month = 1
        year = for_date.year + 1
    return date(year, month, 1)


class DnTree:
    """Represents set of distinguished names as a tree."""
    
    def __init__(self, all_dn=set()):
        """Initialize tree.
        
        all_dn --- set of dn to initially add to a tree
        """
        self.childs = {}
        self.parent = {}
        self.fake_parent = {} # distinguished name of a node
                              # that should be a parent
                              # but not exists in a current tree
        
        self.dn_set = set() # all nodes in a tree
        
        self.parent[""] = ""
        self.childs[""] = [] # used by get_roots()
        
        for dn in all_dn:
            self.add(dn)
            
    def __str__(self):
        """Draw tree in ASCII graphics."""
        
        def print_node(dn, prefix=""):
            if self.parent[dn] == "":
                ret1 = "%s-%s\n" % ( prefix, dn)
            else:
                ret1 = "%s-%s\n" % ( prefix, self.get_rdn(dn))
            for i in self.get_childs(dn):
                ret1 += print_node(i, prefix+" |")
            return ret1
            
        ret = ""
        for i in self.get_roots():
            ret += print_node(i)
        return ret
    
    def get_roots(self):
        """Get list root nodes without parent."""
        try:
            return self.childs[""]
        except KeyError:
            return []
            
    def get_childs(self, dn):
        if dn in self.childs.keys():
            return self.childs[dn]
        return []
        
    def get_parent_dn(self, dn):
        """Returns distinguished name of parent node (if it belongs to tree,
        else return empty string).
        
        dn --- distinguished name of node, which parent to return
        """
        _len = dn.find(".")
        if _len == -1:
            return ""
        else:
            if dn[_len+1:] in self.dn_set:
                return dn[_len+1:]
            else:
                return ""
            
    def get_fake_parent_dn(self, dn):
        """Get distinguished name of node that should be a parent node of node
        with distinguished name dn, although it does not exist in current tree.
        
        dn --- distinguished name of node, which fake parent to return
        """
        _len = dn.find(".")
        if _len == -1:
            return ""
        else:
            return dn[_len+1:]
            
    def get_rdn(self, dn):
        """Get relative distinguished name.
        
        dn --- distinguished name
        """
        _len = dn.find(".")
        if _len == -1:
            return dn
        else:
            return dn[:_len]
        
    def add(self, dn):
        """Add node to tree.
        
        dn --- distinguished name of node.
        """
        
        if dn in self.dn_set:
            raise ValueError('A record with dn=%s already exists!' % dn)
            
        if DEBUG:
            print 'tree add %s' % dn
        
        parent_dn = self.get_parent_dn(dn)
        fake_parent = self.get_fake_parent_dn(dn)

        if parent_dn != fake_parent:
            try:
                self.fake_parent[fake_parent].append(dn)
            except KeyError:
                self.fake_parent[fake_parent] = [dn]
                
        self.parent[dn] = parent_dn
        try:
            self.childs[parent_dn].append(dn)
        except KeyError:
            self.childs[parent_dn] = [dn]
            
        try:
            for i in self.fake_parent.pop(dn):
                if DEBUG:
                    print 'dntree: add: removing %s from childs[""]' % i
                self.childs[""].remove(i)
                self.parent[i] = dn
                try:
                    self.childs[dn].append(i)
                except KeyError:
                    self.childs[dn] = [i]
        except KeyError:
            pass
        
        self.dn_set.add(dn)
        
    def rename(self, old_dn, new_dn):
        """Rename node.
        
        old_dn --- old distinguished name of node.
        new_dn --- new distinguished name of node.
        """
        if old_dn not in self.dn_set:
            raise ValueError("A record with dn=%s don't exists!" % new_dn)
        if new_dn in self.dn_set:
            raise ValueError("A record with dn=%s already exists!" % new_dn)
        self.remove(old_dn)
        self.add(new_dn)
        
    def remove(self, dn):
        """Remove node from tree.
        
        dn --- distinguished name of node.
        """
        
        if dn not in self.dn_set:
            raise ValueError('A record with dn=%s doesn\'t exists!' % dn)
        
        parent = self.get_parent_dn(dn)
        fake_parent = self.get_fake_parent_dn(dn)
        
        if parent != fake_parent:
            self.fake_parent[fake_parent].remove(dn)
        
        self.childs[parent].remove(dn)
        
        if dn in self.childs.keys():
            childs = tuple(self.childs[dn])
            for i in childs:
                self.remove(i)
            self.childs.pop(dn)
            
        self.parent.pop(dn)
        self.dn_set.remove(dn)

