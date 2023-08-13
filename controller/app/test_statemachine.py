import unittest

from statemachine import Event
from statemachine import State
from statemachine import Transition
from statemachine import StateMachine


class TestMachine (StateMachine):
    def __init__(self, **kwargs):
        self.test = False
        super(TestMachine, self).__init__(**kwargs)

    def test_func(self, event_data):
        self.test = True
    def test_condition(self, event_data):
        return self.test
    def condition_true(self, event_data):
        return True
    def condition_false(self, event_data):
        return False

state_A = State('A')
state_B = State('B')
state_C = State('C')

states = [state_A, state_B, state_C]

transitions = [
    Transition(source='A', dest='B', event='A2B'),
    Transition(source='B', dest='C', event='B2C'),
    Transition(source='C', dest='A', event='C2A'),
]

class TestStateMachine(unittest.TestCase):
    def setUp(self):
        pass

    def make_event(self, name='test'):
        machine = TestMachine(states=states, transitions=transitions)
        return Event(name=name, machine=machine)

    def test_callback(self):
        event = self.make_event('test')
        event.machine.callback('test_func', event)
        self.assertTrue(event.machine.test)

    def test_state_on_enter(self):
        event = self.make_event('test')
        state = State('test_state', on_enter='test_func')
        state.enter(event)
        self.assertTrue(event.machine.test)

    def test_condition(self):
        event = self.make_event('test')
        transition = Transition(source=None, dest=None, event=None, condition='condition_true')
        self.assertTrue(transition.eval_condition(event))
        transition.condition = 'condition_false'
        self.assertFalse(transition.eval_condition(event))

    def test_get_state(self):
        event = self.make_event('test')
        self.assertEqual(event.machine.get_state('A').name, 'A')

    def test_set_state(self):
        machine = TestMachine(states=states, transitions=transitions)
        self.assertEqual(machine.state, state_A)
        machine.set_state('B')
        self.assertEqual(machine.state, state_B)

    def test_get_matched_transitions(self):
        machine = TestMachine(states=states, transitions=transitions)
        self.assertIs(machine.state, state_A)
        t = machine.get_matched_transitions(event='A2B', state=machine.state)
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0].dest, 'B')

    def test_trigger_event(self):
        machine = TestMachine(states=states, transitions=transitions)
        self.assertIs(machine.state, state_A)
        machine.trigger_event('A2B')
        self.assertEqual(machine.state, state_B)

    def test_event_trigger(self):
        event = self.make_event('A2B')
        event.trigger()
        self.assertEqual(event.machine.state, state_B)

if __name__ == '__main__':
    unittest.main()