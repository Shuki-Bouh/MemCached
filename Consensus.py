import threading
from time import time
from random import randint

class Process(threading.Thread):
    clock_max = 5
    def __init__(self, process_id, processes):
        super().__init__(target=self.process_messages)
        self.process_id = process_id
        self.active = True
        self.message_queue = []
        self.processes = processes
        self.lock = threading.Lock()
        self.nombre = randint(0, 101)

    def send_message(self, recipient, message):
        with recipient.lock:
            if recipient.active:
                print(f"Process {self.process_id} sends '{message}' to Process {recipient.process_id}")
                recipient.message_queue.append((self, message))
                return True
            else:
                print(f"Process {self.process_id} failed to reach Process {recipient.process_id}")

    def process_messages(self):
        """Ici, on envoie à tous les process notre nombre. Chacun va le comparer au sien, s'il est supérieur, il
        broadcast ce nouveau nombre. Cela garanti que si le broadcast a été interrompu, le nombre sera de nouveau broadcast.

        Avec ce fonctionnement on vérifie :
            - Accord : Ils finiront par être d'accord sur la valeur la plus haute
            - Intégrité : Par défaut le nombre qu'ils possèdent est un nombre qui a été proposé, donc la valeur d'accord aura été proposé par au moins l'un d'eux
            - Validité : Ils vont tous finir par broadcast la valeur la plus haute, celle de l'accord
            - Terminaison : une fois qu'ils ont tous atteint la valeur max, ils arrêtent de broadcast et le programme s'arrête."""
        self.broadcast_message()
        while self.active:
            with self.lock:
                if self.message_queue:
                    sender, message = self.message_queue.pop(0)
                    if int(message) > self.nombre:
                        self.nombre = int(message)
                        self.broadcast_message()
                        print(f"Je suis {self.process_id} et le consensus peut être : {self.nombre}")

    def broadcast_message(self):
        for recipient in self.processes:
            if recipient.process_id != self.process_id:
                self.send_message(recipient, str(self.nombre))


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


    simulate()