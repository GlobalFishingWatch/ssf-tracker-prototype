from statemachine import StateMachine
from statemachine import Event
from timer import MockTime


def run_events(events):
    mock_time = MockTime()
    mock_time.setup()

    for machine_name, event_name, time_ms in events:
        machine = StateMachine.get_machine(machine_name)
        event = machine.get_event(event_name)
        mock_time.set_current_time_ms(int(time_ms))
        event.trigger()
        Event.trigger_scheduled_events()

    mock_time.tearDown()
