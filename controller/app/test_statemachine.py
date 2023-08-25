import unittest

from statemachine import Event
from statemachine import State
from statemachine import Transition
from statemachine import StateMachine
from event_runner import run_events


class TestMachine (StateMachine):
    state_A = State('A')
    state_B = State('B')
    state_C = State('C')

    states = [state_A, state_B, state_C]

    transitions = [
        Transition(source='A', dest='B', event='A2B'),
        Transition(source='B', dest='C', event='B2C'),
        Transition(source='C', dest='A', event='C2A'),
        Transition(event='test', after='test_func')
    ]

    def __init__(self, **kwargs):
        self.test = False
        super(TestMachine, self).__init__(states=self.states, transitions=self.transitions, **kwargs)

    def test_func(self, event):
        self.test = True

    def test_condition(self, event):
        return self.test

    def condition_true(self, event):
        return True

    def condition_false(self, event):
        return False


class TestStateMachine(unittest.TestCase):

    def setUp(self):
        self.machine = TestMachine(name='TestMachine')
        self.test_event = self.make_event('test')

    def tearDown(self):
        StateMachine.machines.pop('TestMachine')

    def make_event(self, name='test'):
        return Event(name=name, machine=self.machine)

    def test_callback(self):
        self.test_event.machine.callback('test_func', self.test_event)
        self.assertTrue(self.machine.test)

    def test_state_on_enter(self):
        state = State('test_state', on_enter='test_func')
        state.enter(self.test_event)
        self.assertTrue(self.machine.test)

    def test_condition(self):
        transition = Transition(source=None, dest=None, event=None, condition='condition_true')
        self.assertTrue(transition.eval_condition(self.test_event))
        transition.condition = 'condition_false'
        self.assertFalse(transition.eval_condition(self.test_event))

    def test_get_state(self):
        self.assertEqual(self.machine.get_state('A').name, 'A')

    def test_set_state(self):
        self.assertEqual(self.machine.state, TestMachine.state_A)
        self.machine.set_state('B')
        self.assertEqual(self.machine.state, TestMachine.state_B)

    def test_get_matched_transitions(self):
        self.assertIs(self.machine.state, TestMachine.state_A)
        t = self.machine.get_matched_transitions(event='A2B', state=self.machine.state)
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0].dest, 'B')

    def test_trigger_event(self):
        self.assertIs(self.machine.state, TestMachine.state_A)
        self.machine.trigger_event('A2B')
        self.assertEqual(self.machine.state, TestMachine.state_B)

    def test_event_trigger(self):
        event = self.make_event('A2B')
        event._trigger()
        self.assertEqual(event.machine.state, TestMachine.state_B)

    def test_generate_unique_name(self):
        self.assertEqual(self.machine.generate_unique_name('Unique'), 'Unique1')
        StateMachine.machines['Unique1'] = None
        self.assertEqual(self.machine.generate_unique_name('Unique'), 'Unique2')

    def test_name(self):
        self.assertEqual(self.machine.name, 'TestMachine')

    @unittest.skipUnless(hasattr(unittest.TestCase, 'assertLogs'), "Can't use assertLogs in micropython")
    def test_logging(self):
        # we don't have assertLogs in micropython, so skip this test
        with self.assertLogs('root', level='DEBUG') as cm:
            self.machine.set_state('B')
        self.assertEqual(cm.output, ['DEBUG:root:TestMachine: A => B'])

    def test_any_state_transition(self):
        self.assertFalse(self.machine.test)
        self.test_event._trigger()
        self.assertTrue(self.machine.test)

    def test_invalid_event(self):
        with self.assertRaises(ValueError):
            self.machine.trigger_event('invalid')

    def test_run_events(self):
        events = [
            ('TestMachine', 'A2B', 10),
            ('TestMachine', 'B2C', 20),
        ]
        run_events(events)
        self.assertEqual(self.machine.state.name, 'C')


if __name__ == '__main__':
    unittest.main()
