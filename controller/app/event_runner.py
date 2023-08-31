from statemachine import StateMachine
from statemachine import Event
from timer import MockTime
from timer import Timer


def run_events(events):
    mock_time = MockTime()
    mock_time.setup()

    for machine_name, event_name, time_ms in events:
        mock_time.set_current_time_ms(int(time_ms))
        # Timer.check_active_timers()
        machine = StateMachine.get_machine(machine_name)
        if event_name is not None:
            event = machine.get_event(event_name)
            event.trigger()
        Event.trigger_scheduled_events()


    mock_time.tearDown()
