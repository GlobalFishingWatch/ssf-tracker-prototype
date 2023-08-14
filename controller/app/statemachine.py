# A basic state machine
import logging


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
    def __init__(self, name, machine, **kwargs):
        self.name = name
        self.machine = machine
        self.kwargs = kwargs

    def trigger(self):
        self.machine.trigger_event(self)


class Transition(object):
    def __init__(self, source, dest, event, before=None, after=None, condition=None):
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
        source = machine.get_state(self.source)
        dest = machine.get_state(self.dest)

        if self.eval_condition(event):
            machine.callback(self.before, event)
            machine.callback(source.on_exit, event)
            machine.set_state(dest)
            machine.callback(dest.on_enter, event)
            machine.callback(self.after, event)


class StateMachine(object):
    def __init__(self, states=None, transitions=None, initial_state=None, name=None, log=None):
        self.name = name if name else self.__class__.__name__
        self.log = log if log else logging.getLogger('root')
        self.states = {}
        self._state = None
        self.transitions = transitions if transitions else []

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
        if isinstance(event, Event):
            event.machine = self
            event.kwargs.update(kwargs)
        else:
            event = Event(name=event, machine=self, **kwargs)
        return event

    def get_matched_transitions(self, event, state):
        state = self.get_state(state)
        if isinstance(event, Event):
            event = event.name
        return [t for t in self.transitions if t.event == event and self.get_state(t.source) == state]

    def add_states(self, states):
        for s in states:
            if isinstance(s, State):
                self.states[s.name] = s
            else:
                self.states[s] = State(name=s)

    def trigger_event(self, event, **kwargs):
        event = self.get_event(event, **kwargs)
        transitions = self.get_matched_transitions(event=event, state=self.state)
        for t in transitions:
            t.execute(event)

    @classmethod
    def callback(cls, func, event):
        func = getattr(event.machine, func) if func else None
        return func(event) if func else None
