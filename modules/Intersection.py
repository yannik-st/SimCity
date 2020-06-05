#
# Intersection.py
#
#
from modules.Block import Block
from modules.IntersectionBlock import IntersectionBlock
from random import randrange

class Intersection:
    #
    # Intersection class
    #

    # constructor
    def __init__(self, name=None, N_connections=4, missing_dir=None):
        if name is not None:
            setattr(self, 'name', name)
        self.streets = []
        self.north_greenRatio = 0.5
        self.intersectionTime = 60
        self.N_connections = N_connections
        self.directions = None
        self.intersectionEntranceBlocks = None
        self.intersectionExitBlocks = None
        self.toggleShift = 0  # e[0, intersectionTime] - toggle shift determines how long the traffic light will wait for the first toggle
        self.missing_dir = missing_dir

        self._init_intersection_directions()
        self._init_intersectionEntranceBlocks()
        self._init_intersectionExitBlocks()
        self._init_intersectionBlocks()
    # sets up all the nextBlocks of the IntersectionBlocks (-> "intersectionEntranceBlocks"), the nextBlocks will be
    # set in a dictionary with keys: left straight and right, representing the turns a car can perform at an inters.
    def _init_intersection_directions(self):
        directions = ['north', 'east', 'south', 'west']
        if self.N_connections == 3:
            if self.missing_dir:
                directions.remove(self.missing_dir)
            else:
                directions.pop(randrange(0, 4))
        self.directions = directions

    # intersectionEntryBlocks represent the end of a road and the entrance of an Intersection.
    # Those blocks are the only "IntersectionBlock" objects, they have to be special, because
    # they have more than one "nextBlock"
    def _init_intersectionEntranceBlocks(self):
        self.intersectionEntranceBlocks = {     # todo: BlockType und relatedIntersection wurden zu testzwecken eingeführt und sind eventuell unnötig
            'north': IntersectionBlock(True, blockType='roadEnd', relatedIntersection=self),
            'east': IntersectionBlock(False, blockType='roadEnd', relatedIntersection=self),
            'south': IntersectionBlock(True, blockType='roadEnd', relatedIntersection=self),
            'west': IntersectionBlock(False, blockType='roadEnd', relatedIntersection=self)
        }
        if self.N_connections == 3:
            missingDir = ['north', 'east', 'south', 'west']
            # find missing direction
            for direction in self.directions:
                missingDir.remove(direction)  # todo: this object will be collected by garbage collection, right?
            self.intersectionEntranceBlocks.pop(missingDir[0], None)

    # intersectionExitBlocks represent the entrance of a road and the exit of an Intersection.
    # They are normal "Block" objects
    def _init_intersectionExitBlocks(self):
        self.intersectionExitBlocks = {  # todo: if direction exists...
            'north': Block(blockType='roadEntrance', relatedIntersection=self),
            'east': Block(blockType='roadEntrance', relatedIntersection=self),
            'south': Block(blockType='roadEntrance', relatedIntersection=self),
            'west': Block(blockType='roadEntrance', relatedIntersection=self)
        }
        if self.N_connections == 3:
            missingDir = ['north', 'east', 'south', 'west']
            # find missing direction
            for direction in self.directions:
                missingDir.remove(direction)  # todo: this object will be collected by garbage collection, right?
            self.intersectionExitBlocks[missingDir[0]] = None

    def _init_intersectionBlocks(self):
        # first find out which direction is missing, if we are in a 3-way-intersection
        missingDir = ''
        if self.N_connections == 3:
            missingDir = ['north', 'east', 'south', 'west']
            for direction in self.directions:
                missingDir.remove(
                    direction)  # todo: this object will be collected by garbage collection, right?
            missingDir = missingDir[0]

        for entranceDirection, entranceBlock in self.intersectionEntranceBlocks.items():
            nextBlocks = {'left': None, 'straight': None, 'right': None}
            if entranceDirection == 'north':
                nextBlocks['left'] = self.intersectionExitBlocks['east']
                nextBlocks['straight'] = self.intersectionExitBlocks['south']
                nextBlocks['right'] = self.intersectionExitBlocks['west']
                if missingDir == 'east':
                    nextBlocks.pop('left', None)
                if missingDir == 'south':
                    nextBlocks.pop('straight', None)
                if missingDir == 'west':
                    nextBlocks.pop('right', None)

            if entranceDirection == 'east':
                nextBlocks['left'] = self.intersectionExitBlocks['south']
                nextBlocks['straight'] = self.intersectionExitBlocks['west']
                nextBlocks['right'] = self.intersectionExitBlocks['north']
                if missingDir == 'north':
                    nextBlocks.pop('right', None)
                if missingDir == 'south':
                    nextBlocks.pop('left', None)
                if missingDir == 'west':
                    nextBlocks.pop('straight', None)

            if entranceDirection == 'south':
                nextBlocks['left'] = self.intersectionExitBlocks['west']
                nextBlocks['straight'] = self.intersectionExitBlocks['north']
                nextBlocks['right'] = self.intersectionExitBlocks['east']
                if missingDir == 'north':
                    nextBlocks.pop('straight', None)
                if missingDir == 'east':
                    nextBlocks.pop('right', None)
                if missingDir == 'west':
                    nextBlocks.pop('left', None)

            if entranceDirection == 'west':
                nextBlocks['left'] = self.intersectionExitBlocks['north']
                nextBlocks['straight'] = self.intersectionExitBlocks['east']
                nextBlocks['right'] = self.intersectionExitBlocks['south']
                if missingDir == 'north':
                    nextBlocks.pop('left', None)
                if missingDir == 'east':
                    nextBlocks.pop('straight', None)
                if missingDir == 'south':
                    nextBlocks.pop('right', None)

            entranceBlock.set_nextBlock(nextBlocks)
        self.intersectionExitBlocks.pop(missingDir, None)

    def addStreet(self, street, direction):
        if hasattr(self, direction):
            raise Exception('Intersection contains already a street in "{}"'.format(direction))
        else:
            # this block sets lane[0] as the "right hand side"-lane
            if not street.isConnected:  # the street is not connected to an intersection yet
                street.lanes[0].set_intersectionEntranceBlock(self.intersectionEntranceBlocks[direction])
                street.lanes[1].set_intersectionExitBlock(self.intersectionExitBlocks[direction])
                street.isConnected = True
            else:  # the street is already connected to an intersection
                street.lanes[1].set_intersectionEntranceBlock(self.intersectionEntranceBlocks[direction])
                street.lanes[0].set_intersectionExitBlock(self.intersectionExitBlocks[direction])
            self.streets.append(street)
            setattr(self, direction, street)

    def set_greenRatio(self, north_greenRatio):     # todo: greenRatio von jew. diagonalen intersectionBlocks muss gleich sein, die restl. sind 1-greenRatio.
            pass

    def toggle_lights(self):
        for direction, iBlock in self.intersectionEntranceBlocks.items():
            iBlock.toggle_light()

    def processCars(self,):     # todo: difference between "==" and "is"? does it matter? I randomly make use of both here...

        missingDir = ''
        if self.N_connections == 3:
            missingDir = ['north', 'east', 'south', 'west']
            for direction in self.directions:
                missingDir.remove(direction)  # todo: this object will be collected by garbage collection, right?
            missingDir = missingDir[0]

        for direction, iBlock in self.intersectionEntranceBlocks.items():
            if not iBlock.car:  # entrancBlock has no car
                continue
            if not iBlock.isGreen:  # traffic light is red
                iBlock.car.increment_idleTime()
                continue
            # traffic light is green
            if iBlock.nextBlock[iBlock.car.nextTurn].car:  # nextBlock of entranceBlock is occupied
                iBlock.car.increment_idleTime()
                continue

            # traffic light is green and there is no care in nextBlock
            # ...now we want to turn left..
            if iBlock.car.nextTurn == 'left':
                if direction == 'north':    # todo: before continuing we have to make sure ...[south] does exist!
                    if missingDir is not 'south':
                        if self.intersectionEntranceBlocks['south'].car:    # opposite side has a car
                            if self.intersectionEntranceBlocks['south'].car.nextTurn is not 'left':  # car on opposite side goes straight or right -> we can't go
                                iBlock.car.increment_idleTime()
                                continue

                elif direction == 'east':
                    if missingDir is not 'west':
                        if self.intersectionEntranceBlocks['west'].car:     # opposite side has a car
                            if self.intersectionEntranceBlocks['west'].car.nextTurn is not 'left':  # car on opposite side goes straight or right -> we can't go
                                iBlock.car.increment_idleTime()
                                continue

                elif direction == 'south':
                    if missingDir is not 'north':
                        if self.intersectionEntranceBlocks['north'].car:    # opposite side has a car
                            if self.intersectionEntranceBlocks['north'].car.nextTurn is not 'left':  # car on opposite side goes straight or right -> we can't go
                                iBlock.car.increment_idleTime()
                                continue

                elif direction == 'west':
                    if missingDir is not 'east':
                        if self.intersectionEntranceBlocks['east'].car:     # opposite side has a car
                            if self.intersectionEntranceBlocks['east'].car.nextTurn is not 'left':  # car on opposite side goes straight or right -> we can't go
                                iBlock.car.increment_idleTime()
                                continue

            # either we didn't intend to turn left or the opposite side doesn't exist or didn't have a car or opposite car also turns left -> we can go
            iBlock.car.moveToNextBlock()

    def checkDirection(self, direction):
        if hasattr(self, direction):
            return False
        else:
            return True

    def __len__(self):
        return len(self.streets)

    # string representation for class data
    def __str__(self):
        s = 'Intersection: '

        if hasattr(self, 'name'):
            s += self.name + ', '
        s += 'contains ' + str(self.__len__()) + ' streets ('

        containsName = False
        for st in self.streets:
            if hasattr(st, 'name'):
                s += st.name + ', '
                containsName = True

        if containsName:
            s = s[:-2]

        s += ').'
        return s
