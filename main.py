import pygame
import os
import sys
import neat
import math
import matplotlib.pyplot as plt
import threading
import numpy as np
from random import randint
import time

pistaRandom = randint(0, 1)
grandezzaSchermo = 1920
altezzaSchermo = 1080
schermo = pygame.display.set_mode((grandezzaSchermo, altezzaSchermo))
fitnessChart = []
genomiChart = []
chartIndex = 0

# carico la foto della pista
pista = pygame.image.load(os.path.join("Foto", "pista2.png"))
if pistaRandom == 1:
    pista = pygame.image.load(os.path.join("Foto", "pista2.png"))
    grandezzaSchermo = 1920
    altezzaSchermo = 1080
    schermo = pygame.display.set_mode((grandezzaSchermo, altezzaSchermo))
if pistaRandom == 0:
    pista = pygame.image.load(os.path.join("Foto", "pista.png"))
    grandezzaSchermo = 1244
    altezzaSchermo = 1016
    schermo = pygame.display.set_mode((grandezzaSchermo, altezzaSchermo))


class thread(threading.Thread):
    def __init__(self, thread_name, thread_ID):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID

    def run(self):
        x = np.linspace(1, 1000, 5000)
        y = np.random.randint(1, 1000, 5000)
        plt.ion()
        figure = plt.figure()
        ax = figure.add_subplot(100)
        line1, = ax.plot(x, y)
        line2, = ax.plot(x, y)
        plt.title("Genomi vs fitness", fontsize=20)
        plt.xlabel("Fitness")
        plt.ylabel("Genomi")
        x1 = []
        y1 = []
        while True:
            if len(fitnessChart) > 0:
                y1.append(genomiChart[len(genomiChart)-1])
                x1.append(fitnessChart[len(fitnessChart)-1])
                y = genomiChart[len(genomiChart)-1]
                x = fitnessChart[len(fitnessChart)-1]
                
                line1.set_xdata(x)
                line2.set_ydata(y)
                figure.canvas.draw()
                figure.canvas.flush_events()
                time.sleep(0.1)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    break


thread1 = thread("Thread 2", 1000)
thread1.start()


class Macchina(pygame.sprite.Sprite):
    # costruttore, il parametro self è una variabile reference all'istanza della classe corrente
    def __init__(self):
        super().__init__()
        self.immagineOriginale = pygame.image.load(
            os.path.join("Foto", "macchina.png"))
        self.image = self.immagineOriginale
        self.rect = self.image.get_rect(center=(490, 820))
        self.velocita = pygame.math.Vector2(0.8, 0)
        self.angolo = 0
        self.velocitaRotazione = 5
        self.direzione = 0  # -1 sinistra, 1 destra, 0 avanti dritto
        self.vivo = True
        self.datiRadar = []  # lista che tiene tutti i dati raccolti dai radar

    # funzione che si occupa di aggiornare la macchina
    def update(self):
        self.datiRadar.clear()  # aggiorno ogni volta la lista con i dati nuovi
        self.guida()
        self.ruota()
        # per 5 volte (5 radar differenti)
        for angoloRadar in (-60, -30, 0, 30, 60):
            self.radar(angoloRadar)
        self.collisione()
        self.dati()

    def guida(self):
        self.rect.center += self.velocita*6

    def collisione(self):
        lunghezza = 40  # distanza dal centro della macchina al punto di collisione
        puntoCollisioneDestra = [int(self.rect.center[0] + math.cos(math.radians(self.angolo + 18)) * lunghezza),
                                 int(self.rect.center[1] - math.sin(math.radians(self.angolo + 18)) * lunghezza)]
        puntoCollisioneSinistra = [int(self.rect.center[0] + math.cos(math.radians(self.angolo - 18)) * lunghezza),
                                   int(self.rect.center[1] - math.sin(math.radians(self.angolo - 18)) * lunghezza)]

        # morte da collisione controlla il colore nei punti di collisione (se è verde se fuori dalla pista)
        if schermo.get_at(puntoCollisioneDestra) == pygame.Color(2, 105, 31, 255) \
                or schermo.get_at(puntoCollisioneSinistra) == pygame.Color(2, 105, 31, 255):
            self.vivo = False

        # punti di collisione
        pygame.draw.circle(schermo, (0, 255, 255, 0), puntoCollisioneDestra, 4)
        pygame.draw.circle(schermo, (0, 255, 255, 0),
                           puntoCollisioneSinistra, 4)

    def ruota(self):
        if self.direzione == 1:
            self.angolo -= self.velocitaRotazione
            self.velocita.rotate_ip(self.velocitaRotazione)

        if self.direzione == -1:
            self.angolo += self.velocitaRotazione
            self.velocita.rotate_ip(-self.velocitaRotazione)

        self.image = pygame.transform.rotozoom(
            self.immagineOriginale, self.angolo, 0.1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def radar(self, angoloRadar):
        lunghezza = 0  # lunghezza del radar
        # x e y della macchina
        x = int(self.rect.center[0])
        y = int(self.rect.center[1])

        # while che va finche non il radar non trova l'erba
        while not schermo.get_at((x, y)) == pygame.Color(2, 105, 31, 255) and lunghezza < 200:
            lunghezza += 1
            # calcola il punto di fine del radar
            x = int(
                self.rect.center[0]+math.cos(math.radians(self.angolo+angoloRadar))*lunghezza)
            y = int(
                self.rect.center[1]-math.sin(math.radians(self.angolo+angoloRadar))*lunghezza)

        # disegna il radar
        pygame.draw.line(schermo, (255, 255, 255, 255),
                         self.rect.center, (x, y), 1)
        pygame.draw.circle(schermo, (0, 255, 0, 0), (x, y), 3)

        # distanza tra la macchina e ogni radar
        distanza = int(math.sqrt(math.pow(self.rect.center[0] - x, 2)
                                 + math.pow(self.rect.center[1] - y, 2)))

        self.datiRadar.append([angoloRadar, distanza])  # aggiorno i dati

    def dati(self):
        input = [0, 0, 0, 0, 0]
        # leggo gli input dei radar
        for i, radar in enumerate(self.datiRadar):
            input[i] = int(radar[1])
        return input  # ritorno gli input che mi serviranno per fare il training alla IA


def rimuovi(indice):
    # rimuove la macchina che va fuori dalla strada
    macchine.pop(indice)
    ge.pop(indice)
    reteNeurale.pop(indice)


# metodo con il loop principale che calcola il fitness del genoma (quanto in pratica sta in vita)
def gioca(genomi, configura):
    global macchine, ge, reteNeurale

    macchine = []
    ge = []
    reteNeurale = []

    for idGenoma, genoma in genomi:
        # inserisce le macchine nella lista
        macchine.append(pygame.sprite.GroupSingle(Macchina()))
        genomiChart.append(len(macchine))
        ge.append(genoma)  # inserisce i genomi nella lista
        net = neat.nn.FeedForwardNetwork.create(
            genoma, configura)  # crea la rete neurale
        reteNeurale.append(net)  # inserisce la rete neurale nella lista
        genoma.fitness = 0  # fitness iniziale

    continua = True
    while continua:

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exc_info()

        schermo.blit(pista, (0, 0))  # aggiorno la finestra di pygame

        # se non ci sono più macchine ferma il ciclo
        if len(macchine) == 0:
            break

        # più la macchina va avanti più il fitness aumenta
        for i, macchina in enumerate(macchine):
            ge[i].fitness += 1
            genomiChart.append(i)
            fitnessChart.append(ge[i].fitness)
            # rimuove la macchina che non è sulla strada

            if not macchina.sprite.vivo:
                rimuovi(i)
                genomiChart.pop()
                print("macchina "+str(i)+": morta")

        # controllo gli output della rete neurale (se la macchina guida a destra o a sinistra o va dritta)
        for i, macchina in enumerate(macchine):
            # prende in input i dati generati dai radar
            output = reteNeurale[i].activate(macchina.sprite.dati())
            # l'output sarà una lista tra 1 e -1
            if output[0] > 0.7:  # destra
                macchina.sprite.direzione = 1
            if output[1] > 0.7:  # sinistra
                macchina.sprite.direzione = -1
            if output[0] <= 0.7 and output[1] <= 0.7:  # avanti dritto
                macchina.sprite.direzione = 0

        # aggiorna tutte le macchine
        for macchina in macchine:
            macchina.draw(schermo)
            macchina.update()
        pygame.display.update()


# setup della rete neurale NEAT
def run(config_path):  # destinazione del file di configurazione
    global popolazione
    config = neat.config.Config(  # configurazione di default
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    # passa la popolazione definita nel file a questa variabile
    popolazione = neat.Population(config)

    popolazione.add_reporter(neat.StdOutReporter(True))
    # da le statistiche per ogni generazione di macchine fatta
    stats = neat.StatisticsReporter()

    popolazione.add_reporter(stats)

    # numero di popolazione e metodo principale
    popolazione.run(gioca, 50)


if __name__ == '__main__':  # esegue l'intero programma
    local_dir = os.path.dirname(__file__)
    # prende la destinazione del file
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
