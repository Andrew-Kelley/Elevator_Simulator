from constants import UP, DOWN, DIRECTION_TO_STR


class Request:
    def __init__(self, this_floor, direction, where_to):
        """This represents a request (from outside the elevator) to go up or down
        An instance also includes where the passenger wants to go.

        arguments:
            this_floor   the floor from which the up/down arrow button was pressed
                         this should be a number between 0 and num_floors-1 (inclusive)
            direction    whether it is to go up or down
            where_to     which floors the people would like to go to
            time         the non-negative integer saying on which clock tick (or turn) this request is made
        """
        assert type(this_floor) is int, 'the current level must be an int'
        self.this_floor = this_floor

        assert direction in (UP, DOWN), f"direction must be '{UP}' (for up) or '{DOWN}' (for down)"
        self.direction = direction

        # for floor in where_to:
        assert type(where_to) is int, f'the floor must be an int. Got type(floor): {type(where_to)}'
        if self.direction == UP:
            assert where_to >= self.this_floor
        else:
            assert self.direction == DOWN
            assert where_to <= self.this_floor
        self.where_to = where_to

    def __repr__(self):
        direction = DIRECTION_TO_STR[self.direction]
        return f"on floor {self.this_floor}, direction {direction}, where_to {self.where_to}"
