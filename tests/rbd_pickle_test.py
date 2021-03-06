#! /usr/bin/env python2

import sys
import os
sys.path.insert(0, os.path.join("@CMAKE_CURRENT_BINARY_DIR@", '../binding/python'))

import pickle

import eigen3 as e3
import spacevecalg as sva
import rbdyn as rbd

if __name__ == '__main__':
  # regiter custom pickle function
  rbd.copy_reg_pickle()

  # create a body with random inertia
  def makeBody(bId, bName):
    I = sva.RBInertiad(e3.Vector3d.Random().x(),
                       e3.Vector3d.Random(), e3.Matrix3d.Random())
    return rbd.Body(I, bId, bName)

  body = makeBody(4, 'testBody')

  jR = rbd.Joint(rbd.Joint.Rev, e3.Vector3d.Random().normalized(), True, 5, 'jR')
  jP = rbd.Joint(rbd.Joint.Prism, e3.Vector3d.Random().normalized(),
                 False, 10, 'jP')
  jS = rbd.Joint(rbd.Joint.Spherical, False, 100, 'jS')
  jPla = rbd.Joint(rbd.Joint.Planar, True, 0, 'jPla')
  jC = rbd.Joint(rbd.Joint.Cylindrical, e3.Vector3d.Random().normalized(),
                 False, 50, 'jC')
  jFree = rbd.Joint(rbd.Joint.Free, True, 2344, 'jFree')
  jFix = rbd.Joint(rbd.Joint.Fixed, False, 3998, 'jFix')

  mb = rbd.MultiBody([makeBody(i, 'body%s' % i) for i in xrange(7)],
                     [jR, jP, jS, jPla, jC, jFree, jFix],
                     range(-1, 6), range(0, 7), range(-1, 6),
                     [sva.PTransformd(e3.Vector3d(0.,i,0.)) for i in xrange(7)])


  def test(v, func):
    pickled = pickle.dumps(v)
    v2 = pickle.loads(pickled)
    assert(func(v, v2))

  def bodyEq(b1, b2):
    return b1.inertia() == b2.inertia() and\
      b1.name() == b2.name() and\
      b1.id() == b2.id()

  def jointEq(j1, j2):
    return j1.type() == j2.type() and\
      j1.name() == j2.name() and\
      j1.id() == j2.id() and\
      j1.direction() == j2.direction() and\
      list(j1.motionSubspace()) == list(j2.motionSubspace())

  def multiBodyEq(mb1, mb2):
    isEq = True
    for b1, b2 in zip(mb1.bodies(), mb2.bodies()):
      isEq &= bodyEq(b1, b2)
    for j1, j2 in zip(mb1.joints(), mb2.joints()):
      isEq &= jointEq(j1, j2)

    mb1T = (list(mb1.predecessors()), list(mb1.successors()),
            list(mb1.parents()), list(mb1.transforms()))
    mb2T = (list(mb2.predecessors()), list(mb2.successors()),
            list(mb2.parents()), list(mb2.transforms()))
    return isEq and mb1T == mb2T


  # body
  test(body, bodyEq)

  # joints
  test(jR, jointEq)
  test(jP, jointEq)
  test(jS, jointEq)
  test(jPla, jointEq)
  test(jC, jointEq)
  test(jFree, jointEq)
  test(jFix, jointEq)

  # multiBody
  test(mb, multiBodyEq)
