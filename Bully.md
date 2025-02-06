![ascii-art.png](ascii-art.png)

# Exercice 3
## 1

L'algorithme de Bully fonctionne comme suit :

Prenons la situation suivante :
* 4 process numérotés de 1 à 4.

2 lance le processus d'éléction. Il envoie à 3 et à 4. Plusieurs solutions :
* 3 et 4 sont morts, 2 ne reçoit aucune réponse, alors 2 broadcast aux inférieurs (1) Victory
* 3 a commencé son process d'élection et attend la réponse de 4. 4 est vivant et broadcast Victory à (1,2,3)

## 2

* Le système est synchrone.
* Les processus peuvent échouer à tout moment, y compris pendant l’exécution de l’algorithme.
* Un processus échoue en s'arrêtant et revient d'un échec en redémarrant.
* Il existe un détecteur d'échec qui détecte les processus ayant échoué.
* La transmission des messages entre les processus est fiable.
* Chaque processus connaît son propre identifiant et adresse de processus, ainsi que ceux de tous les autres processus.

## 3

Pour n processus numérotés de 0 à n-1 (qui est son process id).
Chaque processus peut contacter tous les autres processus.
Chaque processus a trois état : passif, actif et mort
Initialement ils sont passifs.

### Fonction principale exécutée par chaque processus
```Processus(i) :
Si je détecte que le leader est inactif ou que je veux initier une élection :
DémarrerElection()
```

### L'élection
```
DémarrerElection() :
    etat_i = actif;
    Pour j € ]i, n[, 
        send(<élection, i>)

    Si aucun processus supérieur ne répond "Ok" dans un délai donné :
        Je suis le leader :
        
        Pour j € [0, i[, 
            send(<élu, i>)
    
    Sinon :
        Si reçu, attendre un message "Leader"
    Si un leader ne se manifeste pas après un certain temps, redémarrer l'élection
```

### Réception d'un message "Election" pour un process i
```
    RecevoirMessage("élection", de j) :
    Si i > j :
        send("Ok", à j)
    DémarrerElection()
        Sinon :
        Ne rien faire (laisser un processus supérieur gérer l’élection)
```    

### Réception d'un message "Leader" d'un processus i
```
    RecevoirMessage("Leader", de j) :
    leader = j
```



