import threading
import time
import random

class Process(threading.Thread):
    def __init__(self, process_id, processes):
        super().__init__(target=self.process_messages)
        self.process_id = process_id
        self.active = True
        self.message_queue = []
        self.processes = processes
        self.lock = threading.Lock()
        self.mem_messages = {}

    def send_message(self, recipient, message):
        with recipient.lock:
            if recipient.active:
                print(f"Process {self.process_id} sends '{message}' to Process {recipient.process_id}")
                recipient.message_queue.append((self, message))
                return True
            else:
                print(f"Process {self.process_id} failed to reach Process {recipient.process_id}")

    def process_messages(self):
        while self.active:
            with self.lock:
                if self.message_queue:
                    sender, message = self.message_queue.pop(0)
                    print(f"Process {self.process_id} processes message '{message}' from Process {sender.process_id}")
                    if "broadcast" in message and message not in self.mem_messages:
                        print(f"Broadcast : {self.process_id}")
                        self.broadcast_message()
                        self.mem_messages[message] = sender


                    """elif message == "XXX":
                        pass # TODO
                        self.coordinator = new_coordinator
                        print(f"Process {self.process_id} updates coordinator to Process {new_coordinator}")"""

    def broadcast_message(self):
        for recipient in self.processes:
            if recipient.process_id != self.process_id:
                self.send_message(recipient, "broadcast")



if __name__ == "__main__":
    def simulate():
        num_processes = 5
        processes = []

        for i in range(1, num_processes + 1):
            p = Process(i, processes)
            processes.append(p)

        # Start all processes
        for p in processes:
            p.start()

        # Simulate failure of a process
        #failed_process = random.choice(processes)
        #failed_process.active = False
        #print(f"Process {failed_process.process_id} has failed.")

        # Trigger an action on a random process
        starter = random.choice([p for p in processes if p.active])
        starter.active = False # to be implemented
        starter.broadcast_message()
        starter.active = True
        # Allow processes to process messages
        time.sleep(5)  # Allow time for message processing

        # Stop all threads
        for p in processes:
            p.active = False
        for p in processes:
            p.join()

    simulate()