#!/usr/bin/python

# Copyright Lane Kolbly <lane@rscheme.org>
# (Heavily) based on Konquest r1274042.

import string, random, sys, math, re

#
# A formatter for the UI
#

class UIFormatter:
    def __init__(self, currentPlayer):
        self.currentPlayer = currentPlayer
        self.playerSymbols = None
        pass

    def printMap(self, map):
        # Let's generate some symbols for each player
        if not self.playerSymbols:
            self.playerSymbols = {}
            planets = map.planetList()
            players = []
            for planet in planets:
                if planet.owner not in players and planet.owner is not None:
                    players.append(planet.owner)
                pass
            symbols = "*+#=-@%%"
            cnt = 1
            for player in players:
                self.playerSymbols[player.name] = symbols[cnt]
                cnt += 1
            pass

        sys.stdout.write("|")
        for row in map.grid:
            for sector in row:
                sys.stdout.write("===")
            break
        sys.stdout.write("|\n")

        for row in map.grid:
            sys.stdout.write("|")
            for sector in row:
                planet = sector.planet
                if not planet:
                    sys.stdout.write("   ")
                else:
                    if not planet.owner:
                        sys.stdout.write(" %s%s" % ("*", planet.name.upper()))
                    else:
                        sys.stdout.write(" %s%s" % (self.playerSymbols[planet.owner.name], planet.name.upper()))
                    """
                    if planet.owner == self.currentPlayer:
                        sys.stdout.write(" %s " % (planet.name.upper()))
                    else:
                        sys.stdout.write(" %s " % (planet.name.lower()))
                        """
            sys.stdout.write("|\n")

        sys.stdout.write("|")
        for row in map.grid:
            for sector in row:
                sys.stdout.write("===")
            break
        sys.stdout.write("|\n")

    def planetStats(self, planet):
        print "|============================="
        print "|Name:            %s" % planet.name
        if not planet.owner:
            print "|Owner:           Neutral"
        else:
            print "|Owner:           %s" % planet.owner.name
        print "|Production:      %s" % planet.production
        print "|Kill Percentage: %.04s" % planet.killP
        print "|Fleet size:      %s" % planet.homeFleet.shipcnt
        print "|=============================\n"

    def attackFleetStats(self):
        for fleet in self.currentPlayer.attackFleets:
            print "Source: %s" % fleet.srcPlanet.name
            print "Destination: %s" % fleet.destPlanet.name
            print "Number of ships: %s" % fleet.shipcnt
            print "Arrival turn: %s" % fleet.arrivalTm
            print ""

class PlayerAI:
    def __init__(self, game, player):
        self.game = game
        self.player = player

        self.minShips = 10
        self.shipCountFactor = 2
        self.level = "medium"

        if self.level == "medium":
            self.minShips = 10
            self.shipCountFactor = 2

    def go(self):
        planets = self.game.map.planetList()
        target = None
        for planet in planets:
            if planet.owner == self.player:
                hasAttack = False
                ships = int(math.floor(planet.homeFleet.shipcnt))
                if ships >= self.minShips:
                    minDistance = 100
                    for attackPlanet in planets:
                        if attackPlanet.owner == self.player:
                            pass
                        else:
                            skip = False
                            dist = self.game.map.distance(planet, attackPlanet)
                            if dist < minDistance and attackPlanet.homeFleet.shipcnt < ships:
                                fleets = self.player.attackFleets
                                for fleet in fleets:
                                    if fleet.destPlanet == attackPlanet:
                                        skip = True
                                        break
                                    pass
                                if skip:
                                    continue
                                target = attackPlanet
                                hasAttack = True
                                minDistance = dist
                                pass
                            pass
                        pass
                    if hasAttack:
                        self.game.attack(planet, target, ships)
                        pass
                    else:
                        minDistance = 100000000.0
                        shipsToSend = 0
                        hasDestination = False
                        for attackPlanet in planets:
                            skip = False
                            dist = self.game.map.distance(planet, attackPlanet)
                            homeShips = int(math.floor(planet.homeFleet.shipcnt * 0.5))
                            if dist < minDistance and attackPlanet.owner == self.player and attackPlanet.homeFleet.shipcnt < homeShips:
                                for fleet in self.player.attackFleets:
                                    if fleet.destPlanet == attackPlanet:
                                        skip = True
                                        pass
                                    pass
                                if skip:
                                    continue
                                shipsToSend = int(math.floor(float(planet.homeFleet.shipcnt - attackPlanet.homeFleet.shipcnt)/self.shipCountFactor))
                                target = attackPlanet
                                hasDestination = True
                                minDistance = dist
                                pass
                            pass
                        if hasDestination:
                            self.game.attack(planet, target, shipsToSend)
                        pass
                    pass
                pass
        pass

class PlayerUI:
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.formatter = UIFormatter(player)
        pass

    def cmdLaunch(self, args):
        # e.g. l a 15 | c & b 10 | c will send 15 from a to c and 10 from
        # b to c.
        command = " ".join(args)
        #match = re.match(r"(?:launch|l)(?:\s*(?:from)?\s+(\w)\s+(\d*)\s*(?: to |\|)\s*(\w)\s*(?:and|&)?)+", command)
        #groups = match.groups()
        #print groups
        for i in re.findall(r"\s*(?:from)?\s+(\w)\s+(\d*)\s*(?: to |\|)\s*(\w)\s*(?:and|&)?", command):#range(len(groups)/3):
            #print i
            #continue
            #nships = groups[1]
            #src = groups[0]
            #dest = groups[2]
            nships = int(i[1])
            src = i[0]
            dest = i[2]

            destPlanet = self.game.map.getPlanet(dest)
            srcPlanet = self.game.map.getPlanet(src)
            if srcPlanet and destPlanet:
                print nships, srcPlanet.homeFleet.shipcnt
                if srcPlanet.owner != self.player:
                    print "You don't own planet %s"%src
                elif nships > srcPlanet.homeFleet.shipcnt:
                    print "There are only %s ships on %s, but you requested %s ships." % (srcPlanet.homeFleet.shipcnt, src, nships)
                else:
                    self.game.attack(srcPlanet, destPlanet, nships)
                    print "Launching %s ships from %s to %s"%(nships, src, dest)
            elif not srcPlanet:
                print "Couldn't find planet %s..."%src
            elif not destPlanet:
                print "Couldn't find planet %s..."%dest
            pass
        pass

    def go(self):
        while 1:
            rawCmd = raw_input(">")

            # Split on spaces
            args = rawCmd.split(" ")

            # Launch attack fleet.
            if args[0] == "l" or args[0] == "launch":
                self.cmdLaunch(args)
                """

                # e.g. l a d c 10 Launches 10 ships from a and 10 ships from d
                # to c.

                if len(args) <= 1:
                    print "You need at least 3 arguments with this command."
                    pass
                elif len(args) < 4:
                    print "You need at least 3 arguments with this command."
                    continue
                else:
                    cnt = 1
                    srcPlanets = []
                    while cnt < len(args)-1:
                        srcPlanetNum = int(args[cnt])
                        cnt += 1
                        srcPlanetName = args[cnt]
                        cnt += 1
                        srcPlanets.append((srcPlanetName, srcPlanetNum))

                    destPlanet = self.game.map.getPlanet(args[cnt])
                    for name,num in srcPlanets:
                        srcPlanet = self.game.map.getPlanet(name)
                        if srcPlanet:
                            if srcPlanet.owner != self.player:
                                print "Ummm... You don't own planet %s" % name
                            elif num > srcPlanet.homeFleet.shipcnt:
                                print "There are only %s ships on %s, but you requested %s ships." % (srcPlanet.homeFleet.shipcnt, name, num)
                            else:
                                self.game.attack(srcPlanet, destPlanet, num)
                        else:
                            print "Couldn't find planet %s..."%name
                    pass

                #srcPlanet = self.game.map.getPlanet("A")
                #destPlanet = self.game.map.getPlanet("B")
                #nships = 10
                #self.game.attack(srcPlanet, destPlanet, nships)
                pass
                """

            # Print stats about the fleets
            if args[0] == "fleets" or args[0] == "fl":
                self.formatter.attackFleetStats()
                pass

            if args[0] == "info" or args[0] == "i":
                if len(args) <= 1:
                    print "Which planet do you want information on?"
                    continue
                planet = self.game.map.getPlanet(args[1])
                if not planet:
                    print "Could not find planet %s"%args[1]
                    continue
                self.formatter.planetStats(self.game.map.getPlanet(args[1]))

            # Move to the next turn
            if args[0] == "done" or args[0] == "d":
                break

            if args[0] == "map":
                self.formatter.printMap(self.game.map)
                pass

            if args[0][0] == "h" or args[0] == "?":
                print "You need help... Oh well. To be implemented."
                print ""
                print "Se la vi."
                print "But, before you go, here's some things that can be said:"
                print """
|========================|
|Conquest-CLI Help Pages |
|     Version 1.0        |
|     Lane Kolbly        |
|========================|

Welcome to ConquestCLI. Note that this is simply a Python, command-line take on
the KDE Konquest. In short, the premise of the game is to take over the galaxy
by launching your ships against the enemy planets.

Here's a quick list of commands, before we go more in-depth:
launch (abbr. "l")
  Launches some fleets. In the game, all ships travel in fleets. This command
  launches one or more fleets. Here are some examples:
    > launch from a 15 to c and from b 20 to c
  This command launches a fleet of 15 from A to C, and a fleet of 20 from B
  to C. Note that if one of the fleets is invalid, for instance if you have
  only 10 ships on planet B, then all of the other fleets will still be
  launched. Note that this command can be extensively abbreviated:
    > l a 15 | c & b 20 | c
  This command has the same effect as the first one.

fleets (abbr. "fl")
  Prints a list of the fleets that are currently underway.

info (abbr. "i")
  When passed the name of a planet, prints the statistics for that planet:
    > info a
  Returns:
    |=============================
    |Name:            A
    |Owner:           player1
    |Production:      10
    |Kill Percentage: 0.4
    |Fleet size:      0
    |=============================
  The information is fairly self-explanatory.

done (abbr. "d")
  Finishes this player's turn.

map (no abbreviation)
  Prints out a map of the galaxy:
    > map
  Returns:
    |==============================|
    |       *G                     |
    |                      +A      |
    |                              |
    |                              |
    |                              |
    |          *H                  |
    |    #B       *D               |
    |                *E    *C      |
    |                              |
    |    *I                *F      |
    |==============================|

  Each planet is represented by a symbol, with a letter to the side of it. Each
  player is given their own symbol, and neutral is given the symbol "*".

"""

            # Quit
            if args[0] == "q":
                break
            pass
        pass

#
# Ripped from map.cc
#

class Map:
    def __init__(self, rows, cols):
        self.nrows = rows
        self.ncols = cols

        self.grid = []
        for i in range(rows):
            col = []
            for j in range(cols):
                col.append(Sector(j, i))
            self.grid.append(col)

    def generateKillPercentage(self):
        return 0.30 + random.random()*0.60

    def generatePlanetProduction(self):
        return 5 + int(random.random()*10)

    def addPlanet(self, sector, owner, production, killP):
        Planet(self.uniquePlanetName(), sector, owner, production, killP)

    def addPlayerPlanetSomewhere(self, owner):
        sector = self.findRandomFreeSector()
        if not sector:
            return None
        return Planet(self.uniquePlanetName(), sector, owner)

    def addNeutralPlanetSomewhere(self):
        sector = self.findRandomFreeSector()
        if not sector:
            return None
        prod = self.generatePlanetProduction()
        killP = self.generateKillPercentage()
        return Planet(self.uniquePlanetName(), sector, None, prod, killP)

    def uniquePlanetName(self):
        s = 0
        planetList = self.planetList()
        while 1:
            isValid = True
            for p in planetList:
                if p.name == string.uppercase[s]:
                    s += 1
                    isValid = False
                    break
            if isValid:
                break
            pass
        return string.uppercase[s]

    def populateMap(self, playerList, nNeutralPlanets):
        for p in playerList:
            self.addPlayerPlanetSomewhere(p)

        for i in range(nNeutralPlanets):
            self.addNeutralPlanetSomewhere()

    def findRandomFreeSector(self):
        freeSectors = []
        for col in self.grid:
            for sector in col:
                if sector.planet is None:
                    freeSectors.append(sector)
        return random.choice(freeSectors)

    def planetList(self):
        planetList = []
        for col in self.grid:
            for sector in col:
                if sector.planet is not None:
                    planetList.append(sector.planet)
        return planetList

    def getPlanet(self, name):
        planets = self.planetList()
        for planet in planets:
            if planet.name == name.upper():
                return planet
        return None

    def distance(self, p1, p2):
        dx = p1.sector.x - p2.sector.x
        dy = p1.sector.y - p2.sector.y
        return math.sqrt(dx*dx + dy*dy)

#
# Ripped from sector.cc
#

class Sector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.planet = None

    def setPlanet(self, planet):
        self.planet = planet

    def removePlanet(self):
        self.planet = None

    def childPlanetUpdate(self):
        if not self.planet:
            return
        self.planet.turn()

#
# Ripped from planet.cc
#

class Planet:
    def __init__(self, name, sector, owner=None, production=10, killP=0.400):
        self.name = name
        self.sector = sector
        self.owner = owner
        self.production = production
        self.originalProduction = production
        self.killP = killP
        self.homeFleet = DefenseFleet(self, 0)
        self.justConquered = False
        sector.setPlanet(self)

    def __del__(self):
        self.sector.removePlanet(self)

    def conquer(self, attackFleet):
        self.owner = attackFleet.owner
        self.owner.planetsConquered += 1
        self.homeFleet.become(attackFleet)
        self.production = self.originalProduction
        self.justConquered = True

    def turn(self, options):
        if options.ProductionAfterConquer or not self.justConquered:
            if not self.owner:
                self.homeFleet.addShips(options.NeutralsProduction)
            else:
                self.homeFleet.addShips(self.production)
                self.owner.shipsBuilt += self.production

            if options.CumulativeProduction:
                self.production += 1

#
# Ripped from fleet.cc
#

class Fleet:
    def __init__(self, shipcnt):
        self.shipcnt = shipcnt

    def removeShips(self, nships):
        self.shipcnt -= nships

    def addShips(self, nships):
        self.shipcnt += nships

class AttackFleet(Fleet):
    def __init__(self, srcPlanet, destPlanet, shipcnt, arrivalTm):
        Fleet.__init__(self, shipcnt)
        self.owner = srcPlanet.owner
        self.srcPlanet = srcPlanet
        self.destPlanet = destPlanet
        self.arrivalTm = arrivalTm

class DefenseFleet(Fleet):
    def __init__(self, homePlanet, shipcnt):
        Fleet.__init__(self, shipcnt)
        self.homePlanet = homePlanet

    # Friendlies landing on friendly soil
    def absorb(self, attackFleet):
        self.shipcnt += attackFleet.shipcnt

    # Friendlies taking over enemies
    def become(self, attackFleet):
        self.shipcnt = attackFleet.shipcnt

    def spawnAttackFleet(self, destPlanet, shipcnt, arrivalTm):
        fleet = AttackFleet(self.homePlanet, destPlanet, shipcnt, arrivalTm)
        self.removeShips(shipcnt)
        return fleet

#
# Ripped from player.cpp
#

class Player:
    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.shipsBuilt = 0
        self.planetsConquered = 0
        self.fleetsLaunched = 0
        self.enemyFleetsDestroyed = 0
        self.enemyShipsDestroyed = 0
        self.attackFleets = []

    def addAttackFleet(self, fleet):
        self.attackFleets.append(fleet)
        self.fleetsLaunched += 1

#
# Ripped from game.cpp
#

class Game:
    def __init__(self, options):
        self.turnCounter = 0
        self.map = Map(options.MapWidth, options.MapHeight)
        self.players = []
        self.currentPlayer = None
        self.options = options

    def generateKillPercentage(self):
        return 0.30 + random.getDouble()*0.60

    def generatePlanetProduction(self):
        return 5 + int(random.getDouble()*10)

    def attack(self, srcPlanet, destPlanet, shipcnt, standingOrder=False):
        arrival = int(math.ceil(self.map.distance(srcPlanet, destPlanet))) + self.turnCounter
        fleet = srcPlanet.homeFleet.spawnAttackFleet(destPlanet, shipcnt, arrival)
        if fleet:
            self.currentPlayer.addAttackFleet(fleet)

    def setPlayers(self, players):
        self.players = players

    def doFleetArrival(self, attackFleet):
        # Check validity of landfall
        if attackFleet.arrivalTm != self.turnCounter:
            return False

        # Decide if we must merge fleets or attack.
        if attackFleet.owner == attackFleet.destPlanet.owner:
            attackFleet.destPlanet.homeFleet.absorb(attackFleet)
        else:
            attacker = attackFleet
            attackerPlanet = attacker.srcPlanet
            defenderPlanet = attacker.destPlanet
            defender = defenderPlanet.homeFleet

            haveVictor = False
            planetHolds = True

            while not haveVictor:
                attackerRoll = random.random()
                defenderRoll = random.random()
                if attackerPlanet.killP == 0 and defenderPlanet.killP == 0:
                    if attackerRoll < defenderRoll:
                        self.makeKill(defender, attackerPlanet.owner)
                    else:
                        self.makeKill(attacker, defenderPlanet.owner)

                if defenderRoll < defenderPlanet.killP:
                    self.makeKill(attacker, defenderPlanet.owner)

                if attacker.shipcnt <= 0:
                    haveVictor = True
                    planetHolds = True
                    continue

                if attackerRoll < attackerPlanet.killP:
                    self.makeKill(defender, attackerPlanet.owner)

                if defender.shipcnt <= 0:
                    haveVictor = True
                    planetHolds = False
                    continue

            if planetHolds:
                print "Planet %s holds!" % (defenderPlanet.name)
            else:
                print "Planet %s falls!" % (defenderPlanet.name)

            if planetHolds:
                if defenderPlanet.owner:
                    defenderPlanet.owner.enemyFleetsDestroyed += 1
            else:
                if attacker.owner:
                    attacker.owner.enemyFleetsDestroyed += 1
                defenderPlanet.conquer(attacker)
        return True

    def makeKill(self, fleet, player):
        fleet.removeShips(1)
        if player:
            player.enemyShipsDestroyed += 1

    def turn(self):
        self.turnCounter += 1

        # Production!
        planetList = self.map.planetList()
        for planet in planetList:
            planet.turn(self.options)

        # See which fleets have made landfall
        for player in self.players:
            finishedFleets = []
            for fleet in player.attackFleets:
                #print "%s %s" % (fleet.arrivalTm, self.turnCounter)
                if fleet.arrivalTm <= self.turnCounter:
                    self.doFleetArrival(fleet)
                    #print "Fleet has made landfall!"
                    finishedFleets.append(fleet)
                pass
            for fleet in finishedFleets:
                player.attackFleets.remove(fleet)

        print "\nIt is now turn %s" % self.turnCounter
        pass

#
# A derived class for options...
#

class Options:
    def __init__(self):
        self.ProductionAfterConquer = True
        self.NeutralsProduction = 5
        self.CumulativeProduction = True
        self.MapWidth = 10
        self.MapHeight = 10
        self.MinNeutrals = 2
        self.MaxNeutrals = 10
        self.nAIPlayers = 2
        self.username = "Human 1"

    def askUserOpt(self, text, default):
        s = raw_input("%s [%s]: " % (text, default))
        if s:
            return s
        return default

    def askUser(self):
        self.username = self.askUserOpt("Your name", "Human 1")
        self.nAIPlayers = int(self.askUserOpt("Number of AI Players", 2))
        self.MapWidth = int(self.askUserOpt("Map Width", 10))
        self.MapHeight = int(self.askUserOpt("Map Height", 10))
        self.MinNeutrals = int(self.askUserOpt("Min Neutral Planets", 2))
        self.MaxNeutrals = int(self.askUserOpt("Max Neutral Planets", 10))
        pass

#
# Some final logic to tie everything together.
#

def main():
    options = Options()
    options.askUser()
    game = Game(options)

    humanPlayer = Player(game, options.username)

    # Two players, for quick debugging
    #print "Creating players 1 and 2..."
    #player1 = Player(game, "player1")
    #player2 = Player(game, "player2")
    #game.players = [player1, player2]

    game.players = []
    for i in range(options.nAIPlayers):
        game.players.append(Player(game, "Computer %s"%(i+1)))

    formatter = UIFormatter(humanPlayer)

    print "Creating home planets for players..."
    #game.map.addPlayerPlanetSomewhere(player1)
    #game.map.addPlayerPlanetSomewhere(player2)
    game.map.addPlayerPlanetSomewhere(humanPlayer)
    for i in range(options.nAIPlayers):
        game.map.addPlayerPlanetSomewhere(game.players[i])

    print "Creating neutral planets..."
    for i in range(random.randint(options.MinNeutrals, options.MaxNeutrals)):
        game.map.addNeutralPlanetSomewhere()

    formatter.printMap(game.map)

    # Print out the stats of all planets
    for planet in game.map.planetList():
        formatter.planetStats(planet)

    #ui1 = PlayerUI(game, player1)
    #ui2 = PlayerAI(game, player2)
    ui1 = PlayerUI(game, humanPlayer)
    ais = []
    for i in range(options.nAIPlayers):
        ais.append(PlayerAI(game, game.players[i]))

    # Now enter the UI
    while 1:
        #game.currentPlayer = player1
        game.currentPlayer = humanPlayer

        print "It is now your turn."
        ui1.go()
        #print "It is now player2's turn."
        #ui2.go()
        for i in range(options.nAIPlayers):
            print "It is now Computer %s's turn."%(i+1)
            ais[i].go()
        game.turn()

main()
