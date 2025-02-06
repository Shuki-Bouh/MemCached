import threading
from time import time

class BullyProcess(threading.Thread):
    def __init__(self, process_id, processes):
        super().__init__(target=self.process_messages)
        self.process_id = process_id
        self.active = True
        self.message_queue = []
        self.processes = processes
        self.lock = threading.Lock()
        self.mem_messages = {}
        self.last_clock = time()
        self.clock = 0
        self.leader = None
        self.en_election = False

    def send_message(self, recipient, message):
        with recipient.lock:
            if recipient.active:
                print(f"Process {self.process_id} sends '{message}' to Process {recipient.process_id}")
                recipient.message_queue.append((self, message))
                return True
            else:
                print(f"Process {self.process_id} failed to reach Process {recipient.process_id}")

    def process_messages(self):
        self.last_clock = time()
        while self.active:
            with self.lock:
                if self.message_queue:
                    sender, message = self.message_queue.pop(0)
                    print(f"Process {self.process_id} processes message '{message}' from Process {sender.process_id}")
                    if "Ok" in message:  # On reçoit le fait qu'un process au-dessus peut être élu, on arrête l'élection
                        self.en_election = False
                    elif "election" in message:  # Un process en dessous nous dit qu'il veut être élu
                        self.send_message(sender, "Ok")  # On lui renvoie "Ok" pour lui signifier qu'on peut être élu, puis on lance l'élection
                        if not self.en_election:  # On se met en élection si ce n'est pas déjà fait.
                            self.election()
                    elif "elu" in message:  # Un nouveau leader est élu, on l'enregistre
                        self.clock = 0  # On réinitialise la clock
                        self.leader = sender.process_id  # Le nouveau leader est donc le sender.
                    elif "Alive" in message:  # Le leader envoie Alive, on check qu'on reçoit bien ce message, autrement
                        self.clock = 0  # On lance une nouvelle élection.
                if self.clock > 5 and not self.en_election:  # Si 5 secondes se sont écoulées, on considère le leader comme mort
                    self.election() # On lance une nouvelle élection
                elif self.clock > 5 and not self.en_election:  # On est en élection et on est en attente d'un "Ok", si 5 secondes sont dépassés, on est élu.
                    self.elu()
                if self.leader == self.process_id:
                    self.alive_message()  # Si on est le leader, on envoie un message pour dire qu'on est toujours vivant
                    self.clock = 0
            current_time = time()
            self.clock += current_time - self.last_clock
            self.last_clock = current_time

    def election(self):
        self.en_election = True # On est candidat
        self.clock = 0  # On remet la clock à 0
        for process in self.processes[self.process_id+1:]: # On envoie à tous les process au dessus.
            self.send_message(process, "election")

    def elu(self):
        self.en_election = False  # On n'est plus en élection ...
        self.clock = 0
        self.leader = self.process_id
        for process in self.processes[:self.process_id]:
            self.send_message(process, "elu")

    def alive_message(self):
        for recipient in self.processes:
            if recipient.process_id != self.process_id:
                self.send_message(recipient, "Alive")
