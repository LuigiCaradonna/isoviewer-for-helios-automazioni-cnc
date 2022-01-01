import threading


class ResettableTimer(threading.Thread):
    def __init__(self, timeout=3, sleep_chunk=0.25, callback=None, *args):
        threading.Thread.__init__(self)

        self.timeout = timeout
        self.sleep_chunk = sleep_chunk
        if callback == None:
            self.callback = None
        else:
            self.callback = callback
        self.callback_args = args

        self.terminate_event = threading.Event()
        self.start_event = threading.Event()
        self.reset_event = threading.Event()
        self.count = self.timeout/self.sleep_chunk

    def run(self):
        print('Run timer...')
        while not self.terminate_event.is_set():
            print('While loop')
            while self.count > 0 and self.start_event.is_set():
                print(self.count)
                # Wait for a small chunk of timeout
                if self.reset_event.wait(self.sleep_chunk):
                    self.reset_event.clear()
                    # Reset the timeout
                    self.count = self.timeout/self.sleep_chunk
                self.count -= 1
            if self.count <= 0:
                # Stop the timer
                self.stop_timer()
                self.terminate()
                print('Timeout: calling function...')
                self.callback(*self.callback_args)

        print('Exit while loop')

    def start_timer(self):
        self.start_event.set()
        self.terminate_event.clear()
        print('Start timer...')

    def stop_timer(self):
        self.start_event.clear()
        self.count = self.timeout / self.sleep_chunk
        print('Stop timer...')

    def restart_timer(self):
        # Reset only if timer is running. otherwise start timer afresh
        if self.start_event.is_set():
            self.reset_event.set()
            print('Reset timer...')
        else:
            self.start_event.set()
            print('Restart timer...')

    def terminate(self):
        self.terminate_event.set()
        print('Terminate timer...')
