# A basic state machine


class State(object):
    def __init__(self, name, on_enter=None, on_exit=None):
        self.name = name
        self.on_enter = on_enter
        self.on_exit = on_exit

    def enter(self, event_data):
        event_data.machine.callback(self.on_enter, event_data)

    def exit(self, event_data):
        event_data.machine.callback(self.on_exit, event_data)

class EventData(object):
    def __init__(self, machine):
        self.machine = machine
        pass

class Transition(object):
    def __init__(self, source, dest, trigger, before=None, after=None, condition=None):
        self.source = source
        self.dest = dest
        self.trigger = trigger
        self.before = before
        self.after = after
        self.condition = condition

    def eval_condition(self, event_data):
        if self.condition:
            return event_data.machine.callback(self.condition, event_data)
        return True

    def execute(self, event_data):
        machine = event_data.machine
        source = machine.get_state(self.source)
        dest = machine.get_state(self.dest)

        if self.eval_condition(event_data):
            machine.callback(self.before, event_data)
            machine.callback(source.on_exit, event_data)
            machine.set_state(dest)
            machine.callback(dest.on_enter, event_data)
            machine.callback(self.after, event_data)


class StateMachine(object):
    def __init__(self, states=None, transitions=None, initial_state=None):
        self.states = {}
        self._state = None
        self.transitions = transitions if transitions else []

        if states:
            self.add_states(states)

        # set the initial state
        # if no valid initial state is provided, use the fist state in the list
        if not initial_state and states:
            initial_state = states[0]
        self.set_state(initial_state)

    @property
    def state(self):
        return self._state

    def get_state(self, state):
        if isinstance(state, State):
            return state
        else:
            return self.states.get(state, None)

    def set_state(self, state):
        if not isinstance(state, State):
            state = self.get_state(state)
        self._state = state

    def get_matched_transitions(self, trigger, state, event_data):
        state = self.get_state(state)
        return [t for t in self.transitions if t.trigger == trigger and self.get_state(t.source) == state]

    def add_states(self, states):
        for s in states:
            if isinstance(s, State):
                self.states[s.name] = s
            else:
                self.states[s] = State(name=s)

    def trigger_event(self, event, event_data):
        event_data.machine = self
        transitions = self.get_matched_transitions(trigger=event, state=self.state, event_data=event_data)
        for t in transitions:
            t.execute(event_data)


    @classmethod
    def callback(cls, func, event_data):
        func = cls.resolve_callable(func, event_data)
        return func(event_data) if func else None

    @staticmethod
    def resolve_callable(func, event_data):
        """ Converts a to a callable member of a state machine.
            If func is not a string it will be returned unaltered.
        Args:
            func (str or callable): Property name, method name or a path to a callable
        Returns:
            callable function resolved from string or func
        """

        return getattr(event_data.machine, func) if func else None
        # if isinstance(func, string_types):
        #     try:
        #         func = getattr(event_data.model, func)
        #         if not callable(func):  # if a property or some other not callable attribute was passed
        #             def func_wrapper(*_, **__):  # properties cannot process parameters
        #                 return func
        #             return func_wrapper
        #     except AttributeError:
        #         try:
        #             module_name, func_name = func.rsplit('.', 1)
        #             module = __import__(module_name)
        #             for submodule_name in module_name.split('.')[1:]:
        #                 module = getattr(module, submodule_name)
        #             func = getattr(module, func_name)
        #         except (ImportError, AttributeError, ValueError):
        #             raise AttributeError("Callable with name '%s' could neither be retrieved from the passed "
        #                                  "model nor imported from a module." % func)
        # return func
