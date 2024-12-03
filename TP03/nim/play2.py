from nim2 import train, play_ais

ai1 = train(10000)  # IA entrenada con 10,000 partidas
ai2 = train(10)     # IA entrenada con 10 partidas

play_ais(ai1, ai2)
