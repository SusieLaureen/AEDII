# 1. Escopo Geral
Desenvolver um sistema de exploração de território 2D no qual o jogador se move por um mapa de regiões interconectadas (grafo), enquanto cada região mantém informações armazenadas e organizadas por uma árvore AVL (por exemplo, recursos, inimigos ou itens encontrados).

---
## 1.1 Escopo Específico

### 🎲 Estrutura de Dados
#### a) Grafo (Mapa do Mundo)
- Cada nó representa uma região/território.
- Cada aresta representa um caminho entre regiões.
- O grafo pode ser não direcionado e ponderado (peso = custo ou dificuldade do caminho).

Deve permitir:-Adicionar/remover regiões e conexões; -Buscar caminhos (BFS/DFS/Dijkstra); -Obter regiões vizinhas.

#### b) Árvore AVL (Dados Internos de Cada Região)
Cada região possui sua própria árvore AVL armazenando elementos do território, por exemplo:
- Recursos (madeira, minério, água, etc.)
- Criaturas
- Itens coletáveis

Deve permitir:-Inserir, remover e buscar elementos com balanceamento;-Listar os elementos em ordem (in-order); -Consultar rapidamente o item mais valioso/mais raro.

### 🎮 Mecânica de Jogo (Lógica Principal)

#### Movimentação do Jogador:
O jogador começa em uma região e pode se mover para regiões conectadas no grafo.
Cada movimento pode consumir energia ou tempo (peso da aresta).

#### Exploração:
- Ao entrar em uma região, o jogador pode:
- Visualizar os recursos (dados da AVL);
- Coletar ou remover um item (remoção na AVL);
- Adicionar novos itens descobertos (inserção na AVL).

#### Objetivo:
Explorar o máximo de regiões possíveis, coletando recursos ou completando uma missão (ex: encontrar um artefato).

#### Interface (Visualização 2D Simples)

- Pode ser feita com Pygame, Tkinter Canvas ou matplotlib interactive.
- O mapa é exibido como nós conectados por linhas (grafo visual).
- O jogador é um ícone que se move de nó em nó.
- Cada vez que entra em um nó, uma janela mostra os itens da AVL.

#### Arquitetura e Organização do Código

| Módulo         | Responsabilidade                                     |
| -------------- | ---------------------------------------------------- |
| `grafo.py`     | Implementa o grafo e suas operações                  |
| `avl_tree.py`  | Implementa a árvore AVL e operações de balanceamento |
| `regiao.py`    | Representa uma região (nó do grafo) com sua AVL      |
| `jogador.py`   | Armazena informações e posição do jogador            |
| `jogo.py`      | Controla a lógica principal (movimento, exploração)  |
| `interface.py` | Renderiza o mapa e interação 2D                      |

---
## 1.2 Escopo Negativo

- O app não terá integração com redes sociais externas
- Não serão implementadas funcionalidades de inteligência artificial voltadas à previsão de comportamentos, estados emocionais ou padrões de uso com base em dados históricos dos usuários
- Não será desenvolvida uma versão web do sistema


# 2. Resultados Esperados

- Algoritmo funcional disponível no GitHub
- Interface intuitiva para o usuário

# 3. Requisitos técnicos (Código)
- VS Code
- Python 3
- Programação orientada a objetos
- Estruturas de dados manuais (AVL implementada do zero)
