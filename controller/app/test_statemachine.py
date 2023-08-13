import unittest

from app.statemachine import EventData
from app.statemachine import State
from app.statemachine import Transition
from app.statemachine import StateMachine


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
    Transition(source='A', dest='B', trigger='A2B'),
    Transition(source='B', dest='C', trigger='B2C'),
    Transition(source='C', dest='A', trigger='C2A'),
]

class TestStateMachine(unittest.TestCase):
    def setUp(self):
        pass

    def make_event_data(self):
        machine = TestMachine(states=states, transitions=transitions)
        return EventData(machine=machine)

    def test_callback(self):
        event_data = self.make_event_data()
        event_data.machine.callback('test_func', event_data)
        self.assertTrue(event_data.machine.test)

    def test_state_on_enter(self):
        event_data = self.make_event_data()
        state = State('test_state', on_enter = 'test_func')
        state.enter(event_data)
        self.assertTrue(event_data.machine.test)

    def test_condition(self):
        event_data = self.make_event_data()
        transition = Transition(source=None, dest=None, trigger=None, condition='condition_true')
        self.assertTrue(transition.eval_condition(event_data))
        transition.condition = 'condition_false'
        self.assertFalse(transition.eval_condition(event_data))

    def test_get_state(self):
        event_data = self.make_event_data()
        self.assertEqual(event_data.machine.get_state('A').name, 'A')

    def test_set_state(self):
        event_data = self.make_event_data()
        self.assertEqual(event_data.machine.state, state_A)
        event_data.machine.set_state('B')
        self.assertEqual(event_data.machine.state, state_B)


    def test_get_matched_transitions(self):
        event_data = self.make_event_data()
        self.assertIs(event_data.machine.state, state_A)
        t = event_data.machine.get_matched_transitions(trigger='A2B',
                                                       state=event_data.machine.state,
                                                       event_data=event_data)
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0].dest, 'B')

    def test_trigger_event(self):
        event_data = self.make_event_data()
        self.assertIs(event_data.machine.state, state_A)
        event_data.machine.trigger_event('A2B', event_data)
        self.assertEqual(event_data.machine.state, state_B)


if __name__ == '__main__':
    unittest.main()