

# constants instead of an enum to use as an index
UP = 0
DOWN = 1


# (Mostly-serious comment) - Having lots of floors requires special design considerations
# (for efficiency) that I am assuming is out of scope of this simulation. The limit below
# could be increased if desired.
MAX_NUM_FLOORS = 20