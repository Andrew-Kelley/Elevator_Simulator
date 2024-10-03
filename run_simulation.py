from os import walk, path
from collections import deque
import json

from request import Request
from elevator import Elevator
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
        return f'For time {self.time}, request: ' + self.request.__repr__()


class Simulation:
    def __init__(self, elevator, debug_mode=False):
        self.event_queue = deque()
        # I'm not totally happy with putting current_time in this class
        # self.command_queue = deque()  # this includes commands from the future (i.e. a later clock tick)
        self.elevator = elevator
        self.simulate_for_time = 0
        self.debug_mode = debug_mode

    def run_sim(self):
        """return a list of VisibleState instances representing the transcript"""
        visible_states = []
        time_for_simulation = self.calc_time_to_simulate_for()  # a bound on the number of clock ticks
        clock_tick = self.elevator.advance_time_and_return_visible_state
        event = self.event_queue.popleft()
        for current_time in range(time_for_simulation):
            # current_time is the "turn number"/"clock tick" this simulation is on
            while event is not None and event.time == current_time:
                self.elevator.add_passenger_request(event.request)
                if self.event_queue:
                    event = self.event_queue.popleft()
                else:
                    event = None

            state = clock_tick()
            visible_states.append(state)
            if self.debug_mode:
                print(f"Time {current_time}, {state}")

            if event is None and state.action == 'waiting':
                # then there is nothing left to simulate
                break

        return visible_states

    def calc_time_to_simulate_for(self):
        last_event = self.event_queue[-1]
        return last_event.time + 3*self.elevator.num_floors + 10


    def add_events_to_queue(self, events):
        """events must be inserted in order (with respect to time)"""
        time = 0
        for event in events:
            request = event.request
            assert 0 <= request.this_floor
            assert request.this_floor < self.elevator.num_floors

            # the events should be inserted in order
            assert time <= event.time
            time = event.time
            self.event_queue.append(event)


def load_from_file(file_name):
    """Return a list of Events as specified in file_name"""
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


def main(file_name, debug_mode=False):
    setup_info = load_from_file(file_name)
    if debug_mode:
        print(setup_info)
    elevator = Elevator(setup_info['num_floors'], setup_info['floor_names'])
    sim = Simulation(elevator, debug_mode)
    sim.add_events_to_queue(setup_info['events'])
    return sim.run_sim()


def test_not_stationary():
    file_name = './example_input/example4.json'
    states = main(file_name)

    last_state = states[-1]
    count_equal = 0
    for state in states:
        if state == last_state:
            count_equal += 1

    assert count_equal < 10


def test_event_insertion():
    """Check that events are not added all at once"""
    file_name = './example_input/example5.json'
    states = main(file_name)
    assert len(states) > 15  # this ensures that the second event happens after the first one


def run_all_examples():
    rel_path = './example_input'
    for (dirpath, dirnames, filenames) in walk(rel_path):
        for file in filenames:
            if '.json' in file:
                print('using file', file)
                main(path.join(rel_path, file), debug_mode=True)


if __name__ == '__main__':
    test_not_stationary()
    test_event_insertion()
    print('all tests pass')

    file_name = './example_input/example5.json'
    main(file_name, debug_mode=True)

    # run_all_examples()
