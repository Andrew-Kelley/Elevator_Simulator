from enum import Enum
from request import Request
from constants import UP, DOWN, MAX_NUM_FLOORS


# In Java, I would seriously consider make this a private class inside Elevator:
class State(Enum):
    GOING_UP = 0
    GOING_DOWN = 1
    WAITING = 4


class VisibleState:
    """What is visible from the outside world"""
    def __init__(self, floor, action):
        self.floor = floor
        self.action = action

    def __repr__(self):
        return f"At Floor {self.floor}, {self.action}"

    def __eq__(self, other):
        return self.floor == other.floor and self.action == other.action


class Elevator:
    """This represents a discrete-time elevator with infinite capacity.

    A regular client of this class (i.e. a simulator) should call only the following functions:
        __init__
        add_passenger_request
        advance_time_and_return_visible_state
    """

    def __init__(self, num_floors, floor_names):
        """floor_names is how to handle having a basement or ground level or multiple basement levels

        Internally, the floors are 0-indexed, meaning the bottom level is 0 (and not, say -3)"""
        assert type(num_floors) is int
        assert 2 <= num_floors,  'there is no point in having an elevator with fewer than 2 floors'
        assert num_floors <= MAX_NUM_FLOORS, f"num_floors: {num_floors}, exceeds bound: {MAX_NUM_FLOORS}"
        self.num_floors = num_floors
        # self.doors_opened = False

        self.floor_names = list(floor_names)
        assert len(self.floor_names)

        # the following records the floors passengers push to go to once inside the elevator:
        self.passenger_drop_off_at_floor = [False for _ in range(self.num_floors)]

        # The following is for up/down buttons people push to get the elevator to come to them.
        # It keeps track of each passenger's information (i.e. where they want to go)
        self.updown_buttons_outside = [{UP: [], DOWN: []} for _ in range(self.num_floors)]

        self.state = State.WAITING
        self.current_floor = 0 # always start a simulation at the bottom floor

        # This class assumes that the elevator can move up or down one floor per clock tick:

    def advance_time_and_return_visible_state(self):
        floor_at_start = self.floor_names[self.current_floor]
        if self.should_open_doors():
            self.open_doors()
            action = 'opening doors'

        else:
            # self.doors_opened = False
            action = self.move_elevator_if_needed()

        state = VisibleState(floor=floor_at_start, action=action)
        return state

    def add_passenger_request(self, request):
        """Push an up or down button outside elevator and record what such a passenger then wants to do"""
        assert isinstance(request, Request)
        # Assume, for simplicity, that people always push the up/down arrow outside before entering the elevator
        self.updown_buttons_outside[request.this_floor][request.direction].append(request)

    def must_drop_someone_off_here(self):
        return self.passenger_drop_off_at_floor[self.current_floor]

    def must_drop_someone_off_below(self):
        """Return True if someone inside needs to be dropped off at a lower floor"""
        lower_floors = self.passenger_drop_off_at_floor[:self.current_floor]  # could be an empty list
        return any([floor for floor in lower_floors])

    def must_drop_someone_off_above(self):
        """Return True if someone inside needs to be dropped off at a higher floor"""
        higher_floors = self.passenger_drop_off_at_floor[self.current_floor + 1:]  # could be an empty list
        return any([floor for floor in higher_floors])

    def open_doors(self):
        """Let anyone in or out and possibly change the state"""
        # self.doors_opened = True
        self.passenger_drop_off_at_floor[self.current_floor] = False  # we just dropped them off (if needed)
        # Assume people only enter the elevator if it's going the right direction (or if the elevator is waiting)
        self.let_passengers_in()

    def should_open_doors(self):
        # if self.doors_opened:
        #     return False
        if self.must_drop_someone_off_here():
            return True
        if self.state == State.GOING_UP:
            if self.people_are_waiting_here_to_go(UP):
                return True
            elif not self.need_to_go_up():
                return self.people_are_waiting_here_to_go(DOWN)
        elif self.state == State.GOING_DOWN:
            if self.people_are_waiting_here_to_go(DOWN):
                return True
            elif not self.need_to_go_down():
                return self.people_are_waiting_here_to_go(UP)
        else:
            return self.people_are_waiting_here()

    def people_are_waiting_above(self):
        """Return True if there are people on a higher floor waiting to be picked up"""
        buttons_on_higher_floors = self.updown_buttons_outside[self.current_floor+1:]
        waiting_to_go_up = any(button[UP] for button in buttons_on_higher_floors)
        waiting_to_go_down = any(button[DOWN] for button in buttons_on_higher_floors)
        return waiting_to_go_up or waiting_to_go_down

    def people_are_waiting_below(self):
        """Return True if there are people on a lower floor waiting to be picked up"""
        buttons_on_lower_floors = self.updown_buttons_outside[:self.current_floor]
        waiting_to_go_up = any(button[UP] for button in buttons_on_lower_floors)
        waiting_to_go_down = any(button[DOWN] for button in buttons_on_lower_floors)
        return waiting_to_go_up or waiting_to_go_down

    def people_are_waiting_here(self):
        return self.people_waiting_here_to_go(UP) or self.people_are_waiting_here_to_go(DOWN)

    def people_are_waiting_here_to_go(self, direction):
        return len(self.people_waiting_here_to_go(direction)) > 0

    def people_waiting_here_to_go(self, direction):
        return self.updown_buttons_outside[self.current_floor][direction]

    def need_to_go_up(self):
        return self.must_drop_someone_off_above() or self.people_are_waiting_above()

    def need_to_go_down(self):
        return self.must_drop_someone_off_below() or self.people_are_waiting_below()

    def let_passengers_in_going(self, direction):
        # we are assuming infinite capacity of the elevator
        for request in self.updown_buttons_outside[self.current_floor][direction]:
            self.passenger_drop_off_at_floor[request.where_to] = True
        self.updown_buttons_outside[self.current_floor][direction] = []

    def let_passengers_in(self):
        """push the buttons inside elevator (which floors to go to)"""
        if self.state == State.GOING_UP or self.state == State.WAITING:
            self.let_passengers_in_going(UP)
            if self.need_to_go_up():
                self.state = State.GOING_UP
            else:
                # in particular, no one entered
                self.let_passengers_in_going(DOWN)
                if self.need_to_go_down():
                    self.state = State.GOING_DOWN
                else:
                    self.state = State.WAITING
        else:
            self.let_passengers_in_going(DOWN)  # no need to change state
            if not self.need_to_go_down():
                # in particular, no one entered
                self.let_passengers_in_going(UP)
                if self.need_to_go_up():
                    self.state = State.GOING_UP
                else:
                    self.state = State.WAITING

    def go_up_one_floor(self):
        self.current_floor += 1
        assert self.current_floor < self.num_floors
        return 'going up'

    def go_down_one_floor(self):
        self.current_floor -= 1
        assert self.current_floor >= 0
        return 'going down'

    def move_elevator_if_needed(self):
        """If needed, move elevator up or down, and if needed, change the state

        Return a string saying whether it went up or down or did nothing"""
        if self.state == State.GOING_UP or self.state == State.WAITING:
            if self.need_to_go_up():
                # going up has precedence
                return self.go_up_one_floor()
            elif self.need_to_go_down():
                self.state = State.GOING_DOWN
                return self.go_down_one_floor()
            else:
                self.state = State.WAITING
        elif self.state == State.GOING_DOWN:
            if self.need_to_go_down():
                return self.go_down_one_floor()
            elif self.need_to_go_up():
                self.state = State.GOING_UP
                return self.go_up_one_floor()
            else:
                self.state = State.WAITING
        return 'waiting'

