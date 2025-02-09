from pymemcache.client.base import Client
import pickle
import threading
from time import time, sleep

client = Client(('localhost', 11211))

# Dans cet exemple, seul le leader envoi des messages "Alive". Lorsqu'il n'y en a plus, les différents process
# commencent une élection

class Process(threading.Thread):
    clock_max = 5
    def __init__(self, process_id):
        super().__init__(target=self.process_life)
        self.process_id = process_id
        self.active = True
        self.last_clock = time()
        self.clock = 0
        self.leader = None
        self.en_election = False
        self.en_attente_de_leader = False
        self.previous_alive = 0
        self.count_alive = 0

    def process_life(self):
        self.last_clock = time()
        while self.active:
            if self.en_attente_de_leader: # Donc on a arrêté notre élection et on attend le message du grand leader
                leader = client.get("Elu")
                if leader is not None:
                    leader = pickle.loads(leader)
                    leader = int(leader)
                    if leader != self.leader: # On regarde si le leader a changé (sinon le message n'a pas encore été mis à jour)
                        self.leader = leader # On peut enfin mettre à jour le leader
                        self.en_attente_de_leader = False  # On reprend l'activité normale
                        self.count_alive = 0
                        self.previous_alive = 0
                        self.clock = 0
            else:
                if self.leader == self.process_id:
                    self.count_alive += 1  # On rappelle qu'on est vivant
                    client.set("Alive", str(self.count_alive))
                    self.clock = 0
                elif client.get("Alive") is not None:
                    if int(pickle.loads(client.get("Alive"))) > self.previous_alive: # Si cette condition n'est pas vérifiée,
                        self.clock = 0  # cela signifie que le leader ne met plus à jour le Alive message donc il est probablement mort.
                if self.clock > Process.clock_max and not self.en_election:  # Si 5 secondes se sont écoulées, on considère le leader comme mort
                    self.election() # On lance une nouvelle élection
                current_time = time()
                self.clock += current_time - self.last_clock
                self.last_clock = current_time
            sleep(1)

    def election(self):
        self.en_election = True # On est candidat
        self.clock = 0  # On remet la clock à 0
        msg = client.get("Election")
        if msg is not None: # Si quelqu'un est déjà en train de se faire élire, on abandonne
            self.en_election = False
            self.en_attente_de_leader = True # On attend qu'il soit réellement élu
            return
        else:
            client.set("Election", pickle.dumps(str(self.process_id)))  # Si on est le premier, on dit qu'on est éligible
            sleep(Process.clock_max) # On attend longtemps ---> au cas où d'autres gens aient écrit après nous
            id = int(pickle.loads(client.get("Election")))
            if id == self.process_id:  # Si le message n'a pas changé, on est le leader, on prévient tout le monde
                self.leader = self.process_id
                self.en_election = False  # On n'est plus en élection ...
                self.clock = 0
                client.set("Elu", pickle.dumps(str(self.process_id)))
                client.delete("Election")  # Plus personne n'est en élection
                self.previous_alive = 0 # On se réinitialise
                self.count_alive = 0

if __name__ == "__main__":
    client.flush_all()
    def simulate():
        num_processes = 5
        processes = []

        for i in range(1, num_processes + 1):
            p = Process(i)
            processes.append(p)

        # Start all processes
        for p in processes:
            p.start()


    simulate()