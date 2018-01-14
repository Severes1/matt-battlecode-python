import battlecode as bc
import random
import sys
import traceback

import os
print(os.getcwd())

print("pystarting")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
directions = list(bc.Direction)

EARTH = bc.Planet.Earth
MARS = bc.Planet.Mars

print("pystarted")

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
random.seed(1234)

# let's start off with some research!
# we can queue as much as we want.
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)

def common_logic():
    print("Matt: {}".format(len(gc.my_units())))

def unload_garrison(unit):
    """
    Unloads the most recently loaded robot in the given direction
    Default: random direction
    :type unit: bc.UnitType.Factory or bc.UnitType.Rocket
    :rtype: None
    """
    garrison = unit.structure_garrison()
    if len(garrison) > 0:
        d = random.choice(directions) # TODO shouldn't be random
        if gc.can_unload(unit.id, d):
            gc.unload(unit.id, d)
    
def earth_logic():
    # walk through our units:

    for unit in gc.my_units():

        # first, factory logic
        if unit.unit_type == bc.UnitType.Factory:
            unload_garrison(unit)
            if gc.can_produce_robot(unit.id, bc.UnitType.Knight):
                gc.produce_robot(unit.id, bc.UnitType.Knight)
                print('produced a knight!')
                continue

        # first, let's look for nearby blueprints to work on
        location = unit.location
        if location.is_on_map(): # TODO only falsified if unit is in rocket
            nearby = gc.sense_nearby_units(location.map_location(), 2)
            for other in nearby:
                if (unit.unit_type == bc.UnitType.Worker
                    and gc.can_build(unit.id, other.id)
                ):
                    gc.build(unit.id, other.id)
                    print('built a factory!')
                    # move onto the next unit
                    continue
                if (other.team != my_team
                    and gc.is_attack_ready(unit.id)
                    and gc.can_attack(unit.id, other.id)
                ):
                    print('attacked a thing!')
                    gc.attack(unit.id, other.id)
                    continue
                
                if unit.unit_type == bc.UnitType.Rocket:
                    if gc.can_load(unit.id, other.id):
                        print("Loading!")
                        gc.load(unit.id, other.id)

        if unit.unit_type == bc.UnitType.Rocket:
            destination = bc.MapLocation(MARS,
                                         random.randrange(100),
                                         random.randrange(100))
            if (len(unit.structure_garrison()) > 0
                and gc.can_launch_rocket(unit.id, destination)
            ):
                print("LAUNCH! {}".format(unit.id))
                gc.launch_rocket(unit.id, destination)

        # okay, there weren't any dudes around
        # pick a random direction:
        d = random.choice(directions)
        try_build(unit.id, bc.UnitType.Factory, d)
        try_build(unit.id, bc.UnitType.Rocket, d)
        try_move(unit.id, d)

def try_build(unit_id, structure_type, direction):
    """
    Attempt to build the given structure type in the given direction
    :type unit_id: int
    :type structure_type: bc.UnitType
    :rtype: None
    """
    if (gc.karbonite() > structure_type.blueprint_cost()
        and gc.can_blueprint(unit_id, structure_type, direction)):
        gc.blueprint(unit_id, structure_type, direction)
        
def try_move(unit_id, direction):
    """
    Attempts a move in the given direction. Returns true if succeeds
    :type unit_id: int
    :type direction: Direction
    :rtype: boolean
    """
    if gc.is_move_ready(unit_id) and gc.can_move(unit_id, direction):
        gc.move_robot(unit_id, direction)
        return True
    else:
        return False

def mars_logic():
    print("I'm Mars!")
    for unit in gc.my_units():
        if unit.unit_type == bc.UnitType.Rocket:
            unload_garrison(unit)
        else: # Definitely not a structure
            d = random.choice(directions)
            try_move(unit.id, d)

def end_turn():    
    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()

### Setup:
my_team = gc.team()
my_planet = gc.planet()
if my_planet == EARTH:
    planet_specific_logic = earth_logic
else:
    planet_specific_logic = mars_logic

# Main Loop
while True:
    print('pyround:', gc.round())
    # frequent try/catches are a good idea
    try:
        common_logic()
        planet_specific_logic()
        end_turn()
    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()
