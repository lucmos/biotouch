import time


class Chrono:
    def __init__(self, initial_message, new_line = False,final_message="done"):
        self.initial_message = initial_message
        self.final_message = final_message
        self.current_milli_time = lambda: int(round(time.time() * 1000))
        self.start_time = self.current_milli_time()

        print(initial_message, end="\n" if new_line else "", flush=True)

    def end(self, message=None):
        if message:
            print("\t{}, {} (in {} millis)".format(self.final_message, message, self.current_milli_time() - self.start_time))
        else:
            print("\t{} (in {} millis)".format(self.final_message, self.current_milli_time() - self.start_time))



