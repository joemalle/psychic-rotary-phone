import copy
from itertools import chain

# vs is a set of integers representing vtxs
# es is a set of pairs of integers representing (src, dst) vtxs
#
class Graph:
  def __init__(self):
    self.vs = set()
    self.es = set()
  
  def __repr__(self):
    return str(self.__dict__)

  def addVtx(self, req = -1):
    if req == -1:
      newV = max(self.vs) + 1 if self.vs else 0
    else:
      newV = req
    assert req not in self.vs
    self.vs.add(newV)
    return newV

  def hasVtx(self, v):
    return v in self.vs
 
  def checkEdge(self, e):
    v0, v1 = e
    assert(self.hasVtx(v0))
    assert(self.hasVtx(v1))
    
  def addEdge(self, e):
    self.checkEdge(e)
    self.es.add(e)
    return e
  
  def hasEdge(self, e):
    self.checkEdge(e)
    return e in self.es

  def removeEdge(self, e):
    assert(self.hasEdge(e))
    self.es.remove(e)

  def edgeFilter(self, v, i):
    assert(self.hasVtx(v))
    return [e for e in self.es if e[i] == v]

  def outEdges(self, v):
    return self.edgeFilter(v, 0)

  def inEdges(self, v):
    return self.edgeFilter(v, 1)

  def allEdges(self, v):
    return list(set(self.outEdges(v) + self.inEdges(v)))

  def inDegree(self, v):
    return len(self.inEdges(v))

  def outDegree(self, v):
    return len(self.outEdges(v))

  def degree(self, v):
    return len(self.allEdges(v))

  def removeVtx(self, v):
    assert(self.hasVtx(v))
    for e in self.allEdges(v):
      self.removeEdge(e)
    self.vs.remove(v)

  def replaceOutEdges(self, v0, v1):
    assert(self.hasVtx(v0))
    assert(self.hasVtx(v1))
    for oute in self.outEdges(v0):
      assert(oute[0] == v0)
      self.removeEdge(oute)
      self.addEdge((v1, oute[1]))

  def replaceInEdges(self, v0, v1):
    assert(self.hasVtx(v0))
    assert(self.hasVtx(v1))
    for ine in self.inEdges(v0):
      assert(ine[1] == v0)
      self.removeEdge(ine)
      self.addEdge((ine[0], v1))

  def replace(self, v0, v1):
    self.replaceOutEdges(v0, v1)
    self.replaceInEdges(v0, v1)

  class DFS:
    def __init__(self, g, _is, preorder, postorder, onvisited):
      self.g = g
      self._is = _is
      self.preorder = preorder
      self.postorder = postorder
      self.onvisited = onvisited
      self.visited = set()
    
    def visit(self, v):
      if v in self.visited:
        self.onvisited(v)
        return
      self.visited.add(v)
      self.preorder(v)
      for i in self._is:
        for e in self.g.edgeFilter(v, i):
          assert(e[i] == v)
          self.visit(e[1 - i])
      self.postorder(v)

    def run(self):
      for v in self.g.vs:
        self.visit(v)

  def toposorted(self):
    class Cycle(BaseException):
      pass
    try:
      order = []
      stack = set()
      def preorder(v):
        stack.add(v)
      def postorder(v):
        order.append(v)
        stack.remove(v)
      def onvisited(v):
        if v in stack:
          raise Cycle
      self.DFS(self, set([1]), preorder, postorder, onvisited).run()
      return order
    except Cycle:
      return None

  def streamFilter(self, v, _is):
    vs = set()
    def preorder(v):
      vs.add(v)
    def postorder(v):
      pass
    def onvisited(v):
      pass
    self.DFS(self, _is, preorder, postorder, onvisited).visit(v)
    return vs

  def upstream(self, v):
    return self.streamFilter(v, set([1]))

  def downstream(self, v):
    return self.streamFilter(v, set([0]))

  def componentHelper(self, v):
    return self.streamFilter(v, set([0, 1]))

  def splitIntoComponents(self):
    v2c = {}
    c2g = []
    nextC = 0
    for v in self.vs:
      if v in v2c:
        continue
      c = nextC
      nextC += 1
      c2g.append(Graph())
      for newV in self.componentHelper(v):
        assert(newV not in v2c)
        v2c[newV] = c
        c2g[c].addVtx(req=newV)
    for e in self.es:
      assert(v2c[e[0]] == v2c[e[1]])
      c = v2c[e[0]]
      c2g[c].addEdge(e)
    return c2g

  def isomorphism(self, other):
    if len(self.vs) != len(other.vs):
      return None
    
    if len(self.es) != len(other.es):
      return None
    
    g0 = copy.deepcopy(self)
    g1 = copy.deepcopy(other)

    def addFullyConnectedVtx(g):
      newV = g.addVtx()
      for v in g.vs:
        g.addEdge((newV, v))
      return newV
    
    v0 = addFullyConnectedVtx(g0)
    v1 = addFullyConnectedVtx(g1)

    v2v = {}
    v2v_rev = {}

    def recurse(v0, v1):
      if (v0 in v2v) != (v1 in v2v_rev):
        return False

      if v0 not in v2v:
        assert(v1 not in v2v_rev)

        if g0.inDegree(v0) != g1.inDegree(v1):
          return False

        if g0.outDegree(v0) != g1.outDegree(v1):
          return False

        v2v[v0] = v1
        v2v_rev[v1] = v0

        def match(n0s, n1s):
          assert(len(n0s) == len(n1s))

          if not n0s and not n1s:
            return True

          for i0 in range(len(n0s)):
            for i1 in range(i0, len(n1s)):
              n1s[i0], n1s[i1] = n1s[i1], n1s[i0]
              if recurse(n0s[i0], n1s[i0]):
                break
              n1s[i0], n1s[i1] = n1s[i1], n1s[i0]
            else:
              return False
          return True

        if match(
          [e[0] for e in g0.inEdges(v0)],
          [e[0] for e in g1.inEdges(v1)]
        ):
          if match(
            [e[1] for e in g0.outEdges(v0)],
            [e[1] for e in g1.outEdges(v1)]
          ):
            return True

        del v2v[v0]
        del v2v_rev[v1]

        return False

      else:
        assert(v2v_rev[v2v[v0]] == v0)
        return v2v[v0] == v1

    if recurse(v0, v1):
      del v2v[v0]
      return v2v
    else:
      return None

def get_g012():
  g = Graph()
  v0 = g.addVtx()
  v1 = g.addVtx()
  v2 = g.addVtx()
  g.addEdge((v0, v1))
  g.addEdge((v1, v2))

  assert(not g.inEdges(0))
  assert([(0, 1)] == g.inEdges(1))
  assert([(1, 2)] == g.inEdges(2))
  assert([(0, 1)] == g.outEdges(0))
  assert([(1, 2)] == g.outEdges(1))
  assert(not g.outEdges(2))
  return g

def test_addVtx():
  g = Graph()
  v0 = g.addVtx()
  assert(g.hasVtx(v0))
  v1 = g.addVtx()
  assert(g.hasVtx(v1))
  assert(v0 != v1)

def test_addEdge():
  g = Graph()
  v0 = g.addVtx()
  v1 = g.addVtx()
  assert(not g.outEdges(v0))
  assert(not g.outEdges(v1))
  assert(not g.inEdges(v0))
  assert(not g.inEdges(v1))
  g.addEdge((v0, v1))
  assert(g.hasEdge((v0, v1)))
  assert([(v0, v1)] == g.outEdges(v0))
  assert(not g.outEdges(v1))
  assert(not g.inEdges(v0))
  assert([(v0, v1)] == g.inEdges(v1))

def test_removeEdge():
  g = get_g012()
  g.removeEdge((0, 1))
  assert([(1, 2)] == list(g.es))

def test_removeVtx():
  g = get_g012()
  g.removeVtx(1)
  assert(not g.es)

def test_replaceOut():
  g = get_g012()
  v3 = g.addVtx()
  g.replaceOutEdges(1, v3)
  assert(not g.inEdges(0))
  assert([(0, 1)] == g.inEdges(1))
  assert(not g.inEdges(3))
  assert([(3, 2)] == g.inEdges(2))
  assert([(0, 1)] == g.outEdges(0))
  assert(not g.outEdges(1))
  assert([(3, 2)] == g.outEdges(3))
  assert(not g.outEdges(2))

def test_replaceIn():
  g = get_g012()
  v3 = g.addVtx()
  g.replaceInEdges(1, v3)
  assert(not g.inEdges(0))
  assert([(0, 3)] == g.inEdges(3))
  assert(not g.inEdges(1))
  assert([(1, 2)] == g.inEdges(2))
  assert([(0, 3)] == g.outEdges(0))
  assert(not g.outEdges(3))
  assert([(1, 2)] == g.outEdges(1))
  assert(not g.outEdges(2))

def test_replace():
  g = get_g012()
  v3 = g.addVtx()
  g.replace(1, v3)
  assert(not g.allEdges(1))

def test_toposort():
  # basic
  g = get_g012()
  assert([0,1,2] == g.toposorted())
  # cycle
  g = get_g012()
  g.addEdge((2, 0))
  assert(None == g.toposorted())
  # diamond
  g = get_g012()
  g.addVtx()
  g.addEdge((0, 3))
  g.addEdge((3, 2))
  assert(0 == g.toposorted()[0])
  assert(2 == g.toposorted()[-1])

def test_streams():
  # basic
  g = get_g012()
  assert(set([0,1,2]) == g.downstream(0))
  assert(set([1,2]) == g.downstream(1))
  assert(set([2]) == g.downstream(2))
  assert(set([0]) == g.upstream(0))
  assert(set([1,0]) == g.upstream(1))
  assert(set([2,1,0]) == g.upstream(2))
  # cycle
  g = get_g012()
  g.addEdge((2, 0))
  assert(g.vs == g.downstream(0))
  assert(g.vs == g.downstream(1))
  assert(g.vs == g.downstream(2))
  assert(g.vs == g.upstream(0))
  assert(g.vs == g.upstream(1))
  assert(g.vs == g.upstream(2))
  # diamond
  g = get_g012()
  g.addVtx()
  g.addEdge((0, 3))
  g.addEdge((3, 2))
  assert(g.vs == g.downstream(0))
  assert(set([3, 0]) == g.upstream(3))
  assert(set([3, 2]) == g.downstream(3))

def test_components():
  g = get_g012()
  g.addVtx()
  assert(set([3]) == g.componentHelper(3))
  assert(2 == len(g.splitIntoComponents()))

  g.addEdge((0, 3))
  assert(1 == len(g.splitIntoComponents()))

def test_degree():
  g = get_g012()
  assert(1 == g.degree(0))
  assert(0 == g.inDegree(0))
  assert(1 == g.outDegree(0))
  assert(2 == g.degree(1))
  assert(1 == g.degree(2))
  g.addVtx()
  assert(0 == g.degree(3))
  g.addEdge((3,3))
  assert(1 == g.degree(3))

def test_isomorphism():
  g0 = get_g012()
  assert(g0.isomorphism(g0))
  g1 = get_g012()
  assert(g0.isomorphism(g1))
  v10 = g1.addVtx()
  assert(not g0.isomorphism(g1))
  v00 = g0.addVtx()
  assert(g0.isomorphism(g1))
  v01 = g0.addVtx()
  assert(not g0.isomorphism(g1))
  v11 = g1.addVtx()
  assert(g0.isomorphism(g1))
  g1.addEdge((v11, v10))
  assert(not g0.isomorphism(g1))
  g0.addEdge((v00, v01))
  assert(g0.isomorphism(g1))

def main():
  test_addVtx()
  test_addEdge()
  test_removeEdge()
  test_removeVtx()
  test_replaceIn()
  test_replaceOut()
  test_replace()
  test_toposort()
  test_streams()
  test_components()
  test_degree()
  test_isomorphism()

if __name__ == "__main__":
   main()

