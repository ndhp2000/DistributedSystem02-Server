import signal


def exit_gracefully(signal_no, stack_frame):
    raise SystemExit


def register_exit_signal():
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

