# 🐼 Sarah's World

Jogo 2D simples feito em Python com [Pygame](https://www.pygame.org/). Pegue o máximo de pandas antes que o tempo acabe!

## 🎮 Como jogar

- Você começa com **10 segundos**.
- A cada panda coletado você ganha **+1 ponto** e **+1 segundo**.
- O panda some e reaparece em outro lugar a cada **2 segundos**, então corre!
- Nos últimos 3 segundos o cronômetro fica **vermelho**.
- Quando o tempo acaba, aparece sua pontuação e o seu **recorde** (high score), que fica guardado enquanto o jogo estiver aberto.

## ⌨️ Controles

| Ação | Teclado | Mouse / Toque |
|---|---|---|
| Mover | Setas ou **W A S D** | Segurar o clique ou o dedo na tela: o personagem vai na direção dele |
| Começar / jogar de novo | Clique | Toque |

## 🛠️ Tecnologias usadas

- Python 3
- Pygame

## ▶️ Como rodar na sua máquina

1. Baixe ou clone o repositório:

```bash
git clone https://github.com/Th1ag0-96/Sarah-s-world.git
cd Sarah-s-world
```

2. Instale a dependência:

```bash
pip install -r requirements.txt
```

3. Rode o jogo:

```bash
python main.py
```

> No Linux e no Mac, se `python` não funcionar, tenta `python3 main.py`.

## 📁 Estrutura do projeto

- `main.py`: código do jogo
- `assets/imagens/`: sprites do personagem, do panda e do título
- `assets/sons/`: música e efeitos sonoros
- `requirements.txt`: bibliotecas necessárias

## 👤 Autor

Feito por Thiago ([@Th1ag0-96](https://github.com/Th1ag0-96)).
