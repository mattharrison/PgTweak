import re

NODE_TYPES = {
    'Append':1,
    'Hash':1,
    'Hash Join':1,
    'HashAggregate':1,
    'Index Scan':1,
    'Nested Loop':1,
    'Result':1,
    'Seq Scan':1,
    'Sort':1,

    }

class Node(object):
    def __init__(self, name, parent):
        self.parent = parent
        self.name = name
        self.children = []
        self.data = []
        self.table = None # for Seq Scan
        self.index = None # for Index Scan
        self.column = None # for Index Scan
        self.estimated = None
        self.actual = None
        self.level = None # spaces before content used for parent detection

    def __str__(self):
        return ' '*self.level + self.name
class NodeData(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class EstimatedData(object):
    def __init__(self, start, end, rows, width):
        self.start = start
        self.end = end
        self.rows = rows
        self.width = width

def get_estimated(line):
    """
    >>> e = get_estimated(' (cost=2747.32..2747.32 rows=2 width=282) ')
    >>> e.start
    '2747.32'
    >>> e.end
    '2747.32'
    >>> e.rows
    '2'
    >>> e.width
    '282'
    """
    start_idx = line.index('cost=')
    end_idx = line.index(')')
    line = line[start_idx:end_idx]
    split = line.split(' ')
    cost = split[0]
    dot_dot_idx = cost.index('..')
    start = cost[cost.index('=')+1:dot_dot_idx]
    end = cost[dot_dot_idx+2:]

    rows = split[1].split('=')[-1]

    width = split[2].split('=')[-1]
    return EstimatedData(start, end, rows, width)

class ActualData(object):
    def __init__(self, start, end, rows, loops):
        self.start = start
        self.end = end
        self.rows = rows
        self.loops = loops

def get_actual(line):
    start_idx = line.index('time=')
    end_idx = line.index(')', start_idx)
    line = line[start_idx:end_idx]
    split = line.split(' ')
    cost = split[0]
    dot_dot_idx = cost.index('..')
    start = cost[cost.index('=')+1:dot_dot_idx]
    end = cost[dot_dot_idx+2:]

    rows = split[1].split('=')[-1]

    loops = split[2].split('=')[-1]
    return ActualData(start, end, rows, loops)
    

def build_tree(results):
    """
    Given EXPLAIN ANALYZE results return the root node
    
    """
    root = None
    if "\n" in results:
        results = results.split("\n")
    parent = None
    last_node = None
    for line in results:
        if 'QUERY PLAN' in line:
            continue
        elif line.startswith('--'):
            continue
        elif 'cost=' in line and 'actual time=' in line:
            stripped = line.lstrip()

            leading_space = len(line) - len(stripped)
            if last_node and leading_space > last_node.level:
                parent = last_node
            while parent and leading_space <= parent.level:
                parent = parent.parent
            
            node = parse_node_line(line, parent, leading_space)

            if parent is None:
                root = node
                parent = node
            last_node = node
        else:
            data = parse_data_line(line)
            parent.data.append(data)
    return root
            
def parse_data_line(line):
    line = line.strip()
    colon_idx = line.find(':')
    name = line[:colon_idx]
    data = line[colon_idx+1:]
    return NodeData(name, data)

def get_name(line):
    first_paren = line.index('(')
    name = line[:first_paren].rstrip()

    arrow = '->  '
    if arrow in name:
        name = name[len(arrow):]

    other = None
    if name.startswith('Seq Scan'):
        seq_re = re.compile(r'(\s+\w+)* on (?P<table>\w+)')
        other = seq_re.search(name).group('table')
        name = 'Seq Scan'
    elif name.startswith('Index Scan'):
        idx_re = re.compile(r'Index Scan using (?P<index>\w+) on (?P<col>\w+)')
        idx = idx_re.search(name).group('index')
        col = idx_re.search(name).group('col')
        other = (idx, col)
        name = 'Index Scan'

    assert name in NODE_TYPES
    return name, other

def parse_node_line(line, parent, depth=None):
    stripped = line.lstrip()
    leading_space = len(line) - len(stripped)
    name, other = get_name(stripped)
    
    estimated = get_estimated(stripped)
    actual = get_actual(stripped)
    node = Node(name, parent)
    node.estimated = estimated
    node.actual = actual
    node.level = leading_space
    if name == 'Seq Scan':
        node.table = other
    elif name == 'Index Scan':
        node.index = other[0]
        node.col = other[1]
    if parent:
        parent.children.append(node)
    return node
    
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
