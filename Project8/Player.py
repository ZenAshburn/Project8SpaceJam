from CollideObjectBase import SphereCollideObject
from panda3d.core import *
from direct.task.Task import TaskManager
from typing import Callable
from direct.task import Task
from SpaceJamClasses import Missile
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import CollisionHandlerEvent
from direct.interval.LerpInterval import LerpFunc
from direct.particles.ParticleEffect import ParticleEffect
import SpaceJamClasses as spaceJamClasses
import re
import random

class Dumbledore(SphereCollideObject):

    def __init__(self, loader: Loader, taskMgr: TaskManager, accept: Callable[[str, Callable], None], modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):

        super(Dumbledore, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0.32, -0.25, 0), 1.0)
        
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex,1)

        self.reloadTime = 2.0
        self.burstRefreshTime = 10.0
        self.missileDistance = 4000
        self.missileBay = 1
        self.burstCount = 1

        self.cntExplode = 0
        self.explodeIntervals = {}

        self.ogDroneCount = spaceJamClasses.Drone.droneCount
        self.currentDroneCount = spaceJamClasses.Drone.droneCount

        self.cTrav = CollisionTraverser()

        self.handler = CollisionHandlerEvent()

        self.handler.addInPattern('into')
        base.accept('into', self.HandleInto)

        base.taskMgr.add(self.CheckIntervals, 'checkMissiles', 34)

        self.SetKeyBindings()
        self.EnableHUD()
        self.SetParticles()
        
    def ForwardBurst(self, keyDown):

        if keyDown:
            base.taskMgr.add(self.ApplyFBurst, 'forward-burst')

        else:
            base.taskMgr.remove('forward-burst')

    def ApplyFBurst(self, task):

        if self.burstCount == 1:
            rate = 100
            trajectory = base.render.getRelativeVector(self.modelNode, Vec3.forward())
            trajectory.normalize()

            self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)

            self.burstCount -= 1

            return Task.done
        
        else:
            if not base.taskMgr.hasTaskNamed('refresh'):
                print('Initializing refresh...')

                base.taskMgr.doMethodLater(0, self.RefreshBurst, 'refresh')
                return Task.cont
            
    def RightBurst(self, keyDown):

        if keyDown:
            base.taskMgr.add(self.ApplyRBurst, 'right-burst')

        else:
            base.taskMgr.remove('right-burst')

    def ApplyRBurst(self, task):

        if self.burstCount == 1:
            rate = 100
            trajectory = base.render.getRelativeVector(self.modelNode, Vec3.right())
            trajectory.normalize()

            self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)

            self.burstCount -= 1

            return Task.done
        
        else:
            if not base.taskMgr.hasTaskNamed('refresh'):
                print('Initializing refresh...')

                base.taskMgr.doMethodLater(0, self.RefreshBurst, 'refresh')
                return Task.cont
            
    def LeftBurst(self, keyDown):

        if keyDown:
            base.taskMgr.add(self.ApplyLBurst, 'left-burst')

        else:
            base.taskMgr.remove('left-burst')

    def ApplyLBurst(self, task):

        if self.burstCount == 1:
            rate = 100
            trajectory = base.render.getRelativeVector(self.modelNode, Vec3.left())
            trajectory.normalize()

            self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)

            self.burstCount -= 1

            return Task.done
        
        else:
            if not base.taskMgr.hasTaskNamed('refresh'):
                print('Initializing refresh...')

                base.taskMgr.doMethodLater(0, self.RefreshBurst, 'refresh')
                return Task.cont
    
    def BackwardBurst(self, keyDown):

        if keyDown:
            base.taskMgr.add(self.ApplyBBurst, 'backward-burst')

        else:
            base.taskMgr.remove('backward-burst')

    def ApplyBBurst(self, task):

        if self.burstCount == 1:
            rate = 100
            trajectory = base.render.getRelativeVector(self.modelNode, Vec3.back())
            trajectory.normalize()

            self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)

            self.burstCount -= 1

            return Task.done
        
        else:
            if not base.taskMgr.hasTaskNamed('refresh'):
                print('Initializing refresh...')

                base.taskMgr.doMethodLater(0, self.RefreshBurst, 'refresh')
                return Task.cont
    
    def Thrust(self, keyDown):

        if keyDown:
            base.taskMgr.add(self.ApplyThrust, 'forward-thrust')
            
        else:
            base.taskMgr.remove('forward-thrust')
    
    def ApplyThrust(self, task):

        rate = 5
        trajectory = base.render.getRelativeVector(self.modelNode, Vec3.forward())
        trajectory.normalize()

        self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)

        return Task.cont

    def LeftTurn(self, keyDown):

        if keyDown:
            base.taskMgr.add(self.ApplyLeftTurn, 'left-turn')

        else:
            base.taskMgr.remove('left-turn')

    def ApplyLeftTurn(self, task):

        rate = -0.5
        self.modelNode.setH(self.modelNode.getH() + rate)
        return Task.cont
    
    def RightTurn(self, keyDown):

        if keyDown:
            base.taskMgr.add(self.ApplyRightTurn, 'right-turn')

        else:
            base.taskMgr.remove('right-turn')

    def ApplyRightTurn(self, task):

        rate = 0.5
        self.modelNode.setH(self.modelNode.getH() + rate)
        return Task.cont
    
    def Climb(self, keyDown):

        if keyDown:
            base.taskMgr.add(self.ApplyClimb, 'climb')

        else:
            base.taskMgr.remove('climb')

    def ApplyClimb(self, task):

        rate = 0.5
        self.modelNode.setP(self.modelNode.getP() + rate)
        return Task.cont
    
    def Dive(self, keyDown):

        if keyDown:
            base.taskMgr.add(self.ApplyDive, 'dive')

        else:
            base.taskMgr.remove('dive')
    
    def ApplyDive(self, task):

        rate = -0.5
        self.modelNode.setP(self.modelNode.getP() + rate)
        return Task.cont
    
    def LeftRoll(self, keyDown):

        if keyDown:
            base.taskMgr.add(self.ApplyLeftRoll, 'left-roll')

        else:
            base.taskMgr.remove('left-roll')

    def ApplyLeftRoll(self, task):

        rate = -0.5
        self.modelNode.setR(self.modelNode.getR() + rate)
        return Task.cont
    
    def RightRoll(self, keyDown):

        if keyDown:
            base.taskMgr.add(self.ApplyRightRoll, 'right-roll')

        else:
            base.taskMgr.remove('right-roll')

    def ApplyRightRoll(self, task):

        rate = 0.5
        self.modelNode.setR(self.modelNode.getR() + rate)
        return Task.cont
    
    def Fire(self):
        if self.missileBay:
            
            travRate = self.missileDistance

            aim = base.render.getRelativeVector(self.modelNode, Vec3.forward())
            aim.normalize()

            fireSolution = aim * travRate
            inFront = aim * 150

            travVec = fireSolution + self.modelNode.getPos()
            self.missileBay -= 1
            tag = 'Missile' + str(Missile.missileCount)

            posVec = self.modelNode.getPos() + inFront

            currentMissile = Missile(base.loader, './Assets/Phaser/phaser.egg', base.render, tag, posVec, 4.0)
            
            base.cTrav.addCollider(currentMissile.collisionNode, self.handler)

            Missile.Intervals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, startPos = posVec, fluid = 1)

            Missile.Intervals[tag].start()
            print(self.missileBay, 'missiles remaining.')

        else:

            if not base.taskMgr.hasTaskNamed('reload'):
                print('Initializing reload...')

                base.taskMgr.doMethodLater(0, self.Reload, 'reload')
                return Task.cont

    def RefreshBurst(self, task):

        if task.time > self.burstRefreshTime:

                self.burstCount += 1

                if self.burstCount > 1:
                    self.burstCount = 1
                
                print("Refresh complete. Burst is ready.")

                return Task.done
            
        elif task.time <= self.burstRefreshTime:
            return Task.cont 

    def Reload(self, task):
        if self.currentDroneCount == self.ogDroneCount or self.currentDroneCount > self.ogDroneCount - 15:
            if task.time > self.reloadTime:

                self.missileBay += 1

                if self.missileBay > 1:
                    self.missileBay = 1
                
                print("Reload complete. 1 missile remaining.")

                return Task.done
            
            elif task.time <= self.reloadTime:
                return Task.cont
            
        elif self.currentDroneCount <= self.ogDroneCount - 15 and self.currentDroneCount > self.ogDroneCount - 30:

            if task.time > self.reloadTime:

                self.missileBay += 2

                if self.missileBay > 2:
                    self.missileBay = 2
                
                print("Reload complete. 2 missile remaining.")

                return Task.done
            
            elif task.time <= self.reloadTime:
                return Task.cont

        elif self.currentDroneCount <= self.ogDroneCount - 30 and self.currentDroneCount > self.ogDroneCount - 45:

            if task.time > self.reloadTime:

                self.missileBay += 3

                if self.missileBay > 3:
                    self.missileBay = 3
                
                print("Reload complete. 3 missiles remaining.")

                return Task.done
            
            elif task.time <= self.reloadTime:
                return Task.cont

        elif self.currentDroneCount <= self.ogDroneCount - 45 and self.currentDroneCount > self.ogDroneCount - 60:

            if task.time > self.reloadTime:

                self.missileBay += 4

                if self.missileBay > 4:
                    self.missileBay = 4
                
                print("Reload complete. 4 missiles remaining.")

                return Task.done
            
            elif task.time <= self.reloadTime:
                return Task.cont

        elif self.currentDroneCount <= self.ogDroneCount - 60 and self.currentDroneCount > self.ogDroneCount - 75:

            if task.time > self.reloadTime:

                self.missileBay += 5

                if self.missileBay > 5:
                    self.missileBay = 5
                
                print("Reload complete. 5 missiles remaining.")

                return Task.done
            
            elif task.time <= self.reloadTime:
                return Task.cont

        elif self.currentDroneCount <= self.ogDroneCount - 75 and self.currentDroneCount > self.ogDroneCount - 90:

            if task.time > self.reloadTime:

                self.missileBay += 6

                if self.missileBay > 6:
                    self.missileBay = 6
                
                print("Reload complete. 6 missiles remaining.")

                return Task.done
            
            elif task.time <= self.reloadTime:
                return Task.cont

        elif self.currentDroneCount <= self.ogDroneCount - 90 and self.currentDroneCount == 0:

            if task.time > self.reloadTime:

                self.missileBay += 7

                if self.missileBay > 7:
                    self.missileBay = 7
                
                print("Reload complete. 7 missiles remaining.")

                return Task.done
            
            elif task.time <= self.reloadTime:
                return Task.cont
        
    def CheckIntervals(self, task):
        for i in Missile.Intervals:
            if not Missile.Intervals[i].isPlaying():
                Missile.cNodes[i].detachNode()
                Missile.fireModels[i].detachNode()

                del Missile.Intervals[i]
                del Missile.fireModels[i]
                del Missile.cNodes[i]
                del Missile.collisionSolids[i]

                break
        
        return Task.cont
    
    def EnableHUD(self):
        self.Hud = OnscreenImage(image = "./Assets/Hud/Reticle3b.png", pos = Vec3(0, 0, 0), scale = 0.1)
        self.Hud.setTransparency(TransparencyAttrib.MAlpha)

    def HandleInto(self, entry):
        fromNode = entry.getFromNodePath().getName()
        intoNode = entry.getIntoNodePath().getName()

        intoPosition = Vec3(entry.getSurfacePoint(base.render))

        tempVar = fromNode.split('_')
        shooter = tempVar[0]
        tempVar = intoNode.split('-')
        tempVar = intoNode.split('_')
        victim = tempVar[0]

        pattern = r'[0-9]'
        strippedString = re.sub(pattern, '', victim)

        if (strippedString == "Drone"):
            Missile.Intervals[shooter].finish()
            print(victim, 'hit at', intoPosition)
            self.currentDroneCount -= 1
            self.DroneDestroy(victim, intoPosition)

        if (strippedString == "DroneOrbiter"):
            Missile.Intervals[shooter].finish()
            print(victim, 'hit at', intoPosition)
            self.currentDroneCount -= 1
            self.DroneDestroy(victim, intoPosition)

        if (strippedString == "DroneSummon"):
            Missile.Intervals[shooter].finish()
            print(victim, 'hit at', intoPosition)
            self.currentDroneCount -= 1
            spaceJamClasses.Boss.summonCount -= 1
            self.DroneDestroy(victim, intoPosition)

        if (strippedString == "Boss"):
            Missile.Intervals[shooter].finish()
            print(victim, 'hit at', intoPosition)

            if spaceJamClasses.Boss.summonCount > 0:
                Missile.Intervals[shooter].finish()
                print(victim, 'is invulnerable while his summons are alive!')

            elif spaceJamClasses.Boss.HP > 1:
                spaceJamClasses.Boss.HP -= 1
                Missile.Intervals[shooter].finish()
                print(victim, 'HP is reduced by 1!')

            else:
                print(victim, "is defeated!")
                self.DroneDestroy(victim, intoPosition)

        if (strippedString == "Planet"):
            Missile.Intervals[shooter].finish()
            self.PlanetDestroy(victim)

        if (strippedString == "Station"):
            Missile.Intervals[shooter].finish()
            self.SpaceStationDestroy(victim)

        else:
            Missile.Intervals[shooter].finish()

    def DroneDestroy(self, hitID, hitPosition):
        nodeID = base.render.find(hitID)
        nodeID.detachNode()

        self.explodeNode.setPos(hitPosition)
        self.Explode(hitPosition)

    def PlanetDestroy(self, victim: NodePath):
        nodeID = base.render.find(victim)

        base.taskMgr.add(self.PlanetShrink, name = "PlanetShrink", extraArgs = [nodeID], appendTask = True)

    def PlanetShrink(self, nodeID: NodePath, task):
        if task.time < 2.0:
            if nodeID.getBounds().getRadius() > 0:
                scaleSubtraction = 10
                nodeID.setScale(nodeID.getScale() - scaleSubtraction)
                temp = 30 * random.random()
                nodeID.setH(nodeID.getH() + temp)
                return task.cont
            
        else:
            nodeID.detachNode()
            return task.done
        
    def SpaceStationDestroy(self, victim: NodePath):
        nodeID = base.render.find(victim)

        base.taskMgr.add(self.SpaceStationShrink, name = "SpaceStationShrink", extraArgs = [nodeID], appendTask = True)

    def SpaceStationShrink(self, nodeID: NodePath, task):
        if task.time < 2.0:
            if nodeID.getBounds().getRadius() > 0:
                scaleSubtraction = 0.5
                nodeID.setScale(nodeID.getScale() - scaleSubtraction)
                temp = 30 * random.random()
                nodeID.setH(nodeID.getH() + temp)
                return task.cont
            
        else:
            nodeID.detachNode()
            return task.done

    def Explode(self, impactPoint):
        self.cntExplode += 1
        tag = 'particles-' + str(self.cntExplode)

        self.explodeIntervals[tag] = LerpFunc(self.ExplodeLight, fromData = 0, toData = 1, duration = 4.0, extraArgs = [impactPoint])
        self.explodeIntervals[tag].start()

    def ExplodeLight(self, t, explosionPosition):
        if t == 1.0 and self.explodeEffect:
            self.explodeEffect.disable()

        elif t == 0:
            self.explodeEffect.start(self.explodeNode)

    def SetParticles(self):
        base.enableParticles()
        self.explodeEffect = ParticleEffect()
        self.explodeEffect.loadConfig("./Assets/Part-Efx/basic_xpld_efx.ptf")
        self.explodeEffect.setScale(20)
        self.explodeNode = base.render.attachNewNode('ExplosionEffects')
           
    def SetKeyBindings(self):
    
        base.accept("space", self.Thrust, [1])
        base.accept("space-up", self.Thrust, [0])
        base.accept("d", self.LeftTurn, [1])
        base.accept("d-up", self.LeftTurn, [0])
        base.accept("a", self.RightTurn, [1])
        base.accept("a-up", self.RightTurn, [0])
        base.accept("w", self.Climb, [1])
        base.accept("w-up", self.Climb, [0])
        base.accept("s", self.Dive, [1])
        base.accept("s-up", self.Dive, [0])
        base.accept("q", self.LeftRoll, [1])
        base.accept("q-up", self.LeftRoll, [0])
        base.accept("e", self.RightRoll, [1])
        base.accept("e-up", self.RightRoll, [0])
        base.accept("f", self.Fire)
        base.accept("arrow_down", self.BackwardBurst, [1])
        base.accept("arrow_up", self.ForwardBurst, [1])
        base.accept("arrow_right", self.RightBurst, [1])
        base.accept("arrow_left", self.LeftBurst, [1])

