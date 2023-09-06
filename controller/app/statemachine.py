# A basic state machine
from util import default_logger
from collections import deque


class State(object):
    def __init__(self, name, on_enter=None, on_exit=None):
        self.name = name
        self.on_enter = on_enter
        self.on_exit = on_exit

    def enter(self, event_data):
        event_data.machine.callback(self.on_enter, event_data)

    def exit(self, event_data):
        event_data.machine.callback(self.on_exit, event_data)


class Event(object):
    # NB: there is a built-in deque in some micropython builds that takes 2 positional params
    # If you get an error here, then you want to make sure you are using collections-deque from micropython-lib
    event_queue = deque()


    def __init__(self, name, machine, **kwargs):
        self.name = name
        self.machine = machine
        self.kwargs = kwargs

    def _trigger(self):
        # Trigger the event on the statemachine immediately
        self.machine.trigger_event(self)

    def trigger(self):
        # does the same thing as schedule
        self.schedule()

    def schedule(self):
        # put the event in the event queue to be executed on the next call to trigger_scheduled_events()
        self.event_queue.append(self)

    @classmethod
    def trigger_scheduled_events(cls):
        while cls.event_queue:
            event = cls.event_queue.popleft()
            event._trigger()


class MockEvent(Event):
    # Event class for testing.  Does not do anything other than count the
    # number of times that the event has benn triggered
    def __init__(self, name):
        self.trigger_count = 0
        super(MockEvent, self).__init__(name=name, machine=None)

    def _trigger(self):
        pass

    def schedule(self):
        self.trigger_count += 1


class Transition(object):
    def __init__(self, event, source=None, dest=None, before=None, after=None, condition=None):
        self.source = source
        self.dest = dest
        self.event = event.name if isinstance(event, Event) else event
        self.before = before
        self.after = after
        self.condition = condition

    def eval_condition(self, event):
        if self.condition:
            return event.machine.callback(self.condition, event)
        return True

    def execute(self, event):
        machine = event.machine

        if self.eval_condition(event):
            machine.callback(self.before, event)
            if self.source:
                machine.callback(machine.get_state(self.source).on_exit, event)
            if self.dest:
                machine.set_state(self.dest)
                machine.callback(machine.get_state(self.dest).on_enter, event)
            machine.callback(self.after, event)


class StateMachine(object):
    machines = {}

    @classmethod
    def generate_unique_name(cls, basename):
        for n in range(1, 10):
            name = f'{basename}{n}'
            if name not in cls.machines:
                break

        return name

    @classmethod
    def get_machine(cls, machine_name):
        return cls.machines[machine_name]

    def __init__(self, states=None, transitions=None, initial_state=None, name=None, log=None):
        self.name = name if name else self.generate_unique_name(self.__class__.__name__)
        if self.name in self.machines:
            raise ValueError(f'Statemachine name "{self.name}" is not unique')
        self.machines[self.name] = self

        self.log = log if log else default_logger()
        self.states = {}
        self._state = None
        self._transitions = transitions if transitions else []

        if states:
            self.add_states(states)

        # set the initial state
        # if no valid initial state is provided, use the fist state in the list
        if not initial_state and states:
            initial_state = states[0]
        self._state = self.get_state(initial_state)

    @property
    def state(self):
        return self._state

    def get_state(self, state):
        if isinstance(state, State):
            return state
        else:
            return self.states[state]

    def set_state(self, state):
        if not isinstance(state, State):
            state = self.get_state(state)
        self.log.debug(f'{self.name}: {self._state.name} => {state.name}')
        self._state = state

    def get_event(self, event, **kwargs):
        self.get_event_transitions(event)  # will raise exception if there are no matching transitions
        if isinstance(event, Event):
            event.machine = self
            event.kwargs.update(kwargs)
        else:
            event = Event(name=event, machine=self, **kwargs)
        return event

    # get all transitions that are triggered by this event
    def get_event_transitions(self, event):
        if isinstance(event, Event):
            event = event.name
        event_transitions = [t for t in self._transitions if t.event == event]
        if not event_transitions:
            raise ValueError(f'State machine "{self.name}" does not have any transitions with event "{event}"')
        return event_transitions

    # get all transitions triggered but the given event that have the source state matching the
    # current machine state
    def get_matched_transitions(self, event, state):
        state = self.get_state(state)
        if isinstance(event, Event):
            event = event.name
        event_transitions = self.get_event_transitions(event)
        return [t for t in event_transitions if t.source is None or self.get_state(t.source) == state]

    def add_states(self, states):
        for s in states:
            if isinstance(s, State):
                self.states[s.name] = s
            else:
                self.states[s] = State(name=s)

    def trigger_event(self, event, **kwargs):
        event = self.get_event(event, **kwargs)
        self.log.debug(f'{self.name}: event {event.name}')
        transitions = self.get_matched_transitions(event=event, state=self.state)
        for t in transitions:
            t.execute(event)

    def schedule_event(self, event, **kwargs):
        event = self.get_event(event, **kwargs)
        event.schedule()

    @classmethod
    def callback(cls, func, event):
        func = getattr(event.machine, func) if func else None
        return func(event) if func else None

    def save_state(self):
        return dict(
            state=self._state.name
        )

    def load_state(self, state):
        self._state = self.get_state(state['state'])
