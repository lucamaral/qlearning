### Exercício sobre QLearning para aula de Reinforcement Learning

### Solução
Foi utilizado a ferramenta GYM para criar o environment de acordo com as limitações dispostas no arquivo https://github.com/lucamaral/qlearning/blob/main/enunciado_trabalho_I_v2%20(1).pdf

Basicamente o agente pode se mover em quatro direções, ESQUERDA, DIREITA, CIMA, BAIXO. Cada ação representa um reward de -1. Caso o agente chegar na base sem o objeto, o reward é de -100. Cada ação que o agente tomar que inviabiliza o mesmo a andar no mapa, o reward é de -5.

Hiperparâmetros utilizados:

- num_episodes	200
- alpha	0.3
- gamma	0.9
- epsilon	1.0
- decay_epsilon	0.3

Resultados:

- Execution time 1.221344232559204 (ms)
- Average reward (all episodes): -47.335 
- Average reward (last 10 episodes): -7.0

[!]

#### Instalar o GYM
```
pip install numpy
pip install gym
pip install tabulate
pip install matplotlib.pyplot
```

#### Executar 
```
python exercicioqlearning.py
```
