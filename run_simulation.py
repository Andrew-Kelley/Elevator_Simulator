from collections import deque
import json
from request import Request
from elevator import Elevator, VisibleState
from constants import UP, DOWN

class Event:
    def __init__(self, request, time):
        """
        Arguments:
            request   of type Request
            time      the non-negative integer saying on which clock tick (or turn) this request is made"""
        assert isinstance(request, Request)
        self.request = request

        assert type(time) is int, "the clock tick must be an integer"
        assert time >= 0, f"time was {time}"
        self.time = time

    def __repr__(self):
        return f'For time {self.time}, reques: ' + self.request.__repr__()


class Simulation:
    def __init__(self, elevator):
        self.event_queue = deque()
        self.current_time = 0  # basically the "turn number"/"clock tick" this simulation is on
        # I'm not totally happy with putting current_time in this class
        # self.command_queue = deque()  # this includes commands from the future (i.e. a later clock tick)
        self.elevator = elevator
        self.simulate_for_time = 0

    def run_sim(self):
        """return a list of strings representing the transcript"""
        while self.event_queue:
            event = self.event_queue.popleft()
            self.simulate_for_time = event.time  # overwritten repeatedly (intentionally)
            self.elevator.add_passenger_request(event.request)

        self.simulate_for_time += 3*self.elevator.num_floors  # in case you have to go to the top floor

        clock_tick = self.elevator.advance_time_and_return_visible_state
        visible_states = [clock_tick() for _ in range(self.simulate_for_time)]

        # not implemented: write to file instead
        for state in visible_states:
            print(state)
        return visible_states


    def add_events_to_queue(self, events):
        """events must be inserted in order (with respect to time)"""
        for event in events:
            request = event.request
            assert 0 <= request.this_floor
            assert request.this_floor < self.elevator.num_floors

            # the events should lbe inserted in order
            assert self.current_time <= event.time
            if self.event_queue:
                assert self.event_queue[-1].time <= event.time

            self.event_queue.append(event)


def load_from_file(file_name):
    """Return a list of Events as specified in file_name"""
    print(file_name)
    with open(file_name) as f:
        info_from_file = json.load(f)

    processed_info = {'num_floors': info_from_file['num_floors'],
                      'floor_names': info_from_file['floor_names']}
    events = []
    for event in info_from_file['events']:
        this_floor = event['this_floor']
        where_to = event['where_to']
        assert this_floor != where_to
        if this_floor < where_to:
            direction = UP
        else:
            direction = DOWN
        events.append(Event(Request(this_floor, direction, where_to), time=event['time']))
    processed_info['events'] = events
    return processed_info


def write_transcript(file_name, transcript):
    """Open file_name and write to it all the elements of the transcript"""
    pass  # not implemented


def main(file_name):
    setup_info = load_from_file(file_name)
    elevator = Elevator(setup_info['num_floors'], setup_info['floor_names'])
    sim = Simulation(elevator)
    sim.add_events_to_queue(setup_info['events'])
    return sim.run_sim()


def test_not_stationary():
    file_name = './example_input/example4.json'
    setup_info = load_from_file(file_name)
    elevator = Elevator(setup_info['num_floors'], setup_info['floor_names'])
    sim = Simulation(elevator)
    sim.add_events_to_queue(setup_info['events'])
    states = sim.run_sim()

    last_state = states[-1]
    count_equal = 0
    for state in states:
        if state == last_state:
            count_equal += 1

    assert count_equal < 10


if __name__ == '__main__':
    file_name = './example_input/example4.json'
    main(file_name)

    # the following is the only test I kept, normally I strongly prefer to write more tests:
    # test_not_stationary()
