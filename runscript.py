from threading import Thread
from time import sleep
from src.models import Utilities as Utils
from src.controllers import ApplicationController as App
from src.views import Logger
from src.models import Emails
import pid
import os, pwd
import traceback


is_active = True


def start(timer, user):
    timer.start()
    user.start()
    join(timer, user)


def join(timer, user):
    timer.join()
    user.join()


def countdown(count):
    global is_active
    while is_active:
        m, s = divmod(count, 60)
        min_sec_format = "{:02d}:{:02d}".format(m, s)
        print(min_sec_format, end="\r")
        sleep(1)
        count -= 1
        if count < 0:
            is_active = False
            auto_run_program()
            break


def await_user_input():
    global is_active
    while is_active:
        input("")
        is_active = False
        manual_run_program()
        break


def manual_run_program():
    print("\n -- Manual run initiated -- \n")
    user_in = input("\n Enter number of weeks or 'p' for preview: ")
    try:
        user_in = int(user_in)
        start_date = Utils.set_search_start_date(user_in)
        App.run_application(start_date)
    except:
        if user_in == "p" or user_in == "P":
            user_in = int(input("\n Enter number of weeks for preview: "))
            start_date = Utils.set_search_start_date(user_in)
            App.run_preview(start_date)


def auto_run_program():
    print("\n >> Automatic run initiated \n")
    start_date = Utils.set_search_start_date(14)
    App.run_application(start_date)


if __name__ == "__main__":
    global LOGGER
    try:
        LOGGER = Logger.init_logger(__name__)
        LOGGER.info("Launching application")
        pidfile = None
        try:
            username = pwd.getpwuid(os.getuid()).pw_name
            pid_file_name = "runscript.py.pid"
            pid_dir = f"/home/{username}/tmp/"
            pid_file_path = os.path.join(pid_dir, pid_file_name)

            # Manual overrun. Without this, PidFile will create a new pidfile even if one exists but that process isn't running
            # We want to raise an exception in this case because it means an ungraceful crash happened
            if os.path.isfile(pid_file_path):
                pid_number = str(open(pid_file_path, "r").readline().strip())
                try:
                    # Don't actually kill process, just check if it's there
                    os.kill(int(pid_number), 0)
                except ProcessLookupError:
                    # Process is terminated
                    raise Exception(
                        f"PID File found but no process to claim that PID. This program has previously had an ungraceful crash. PID File location: {pid_file_path}"
                    )

            pidfile = pid.PidFile(
                piddir=pid_dir,
                pidname=pid_file_name,
                register_atexit=False,
                register_term_signal_handler=None,
            )
            with pidfile:
                print("\n -- PRESS ENTER FOR MANUAL RUN -- \n")
                timer = Thread(target=countdown, args=(5,), daemon=True)
                user = Thread(target=await_user_input, daemon=True)
                start(timer, user)
        except pid.PidFileError as e:
            pid_fname = pidfile.filename
            pid_number = str(open(pid_fname, "r").readline().strip())
            msg = f"An instance of this program is already running with PID {pid_number}. The locking file is at {pid_fname}"
            LOGGER.critical(msg)
            raise pid.PidFileAlreadyLockedError(msg)

    except Exception as e:
        trace_back = traceback.format_exc()
        message = Emails.create_alert_message(trace_back)
        Emails.send_alert_email(message)
        raise e
