# ===========================================
# world.py — Geração do mundo 15×15 
# ===========================================

from graph import Graph
import random

class World:
    """Representa o mundo (labirinto) do jogo."""

    def __init__(self):
        self.graph = Graph()
        self.start_node = "Entrada"
        self.exit_node = "Portão"

        self.chest_rooms = []        # nomes dos baús
        self.chest_contents = {}     # item que cada baú contém
        self.key_room = None         # baú que contém a chave

        # Mapa 15×15
        self.map_grid = self._generate_map()

        # Detectar salas especiais
        self.room_positions = self._assign_rooms()

        # Montar grafo baseado no layout
        self._build_graph()

        # Garantir distribuição fixa dos itens
        self._assign_items()

    # ===============================================================
    # 1. Mapa Fixo 15×15
    # ===============================================================
    def _generate_map(self):
        """
        # = parede
        . = caminho
        P = Entrada
        B = Baú
        E = Portão
        """

        raw = [
            "###############",
            "#P#.......#..B#", 
            "#.#.#####.###.#",
            "#.......#...#.#",
            "#.#####.###.#.#",
            "#.#...#...#...#", 
            "#.#.#####.#####",
            "#.......#.....#", 
            "#######.#####.#",
            "#B....#.....#.#", 
            "#.###.#####.#.#",
            "#...#...#B..#.#",
            "###.###.###.#.#",
            "#............E#", 
            "###############",
        ]

        return [list(row) for row in raw]

    # ===============================================================
    # 2. Detectar salas reais (Entrada, Baús, Portão)
    # ===============================================================
    def _assign_rooms(self):
        rooms = {}
        baus_encontrados = 0

        for y in range(15):
            for x in range(15):
                cell = self.map_grid[y][x]

                if cell == "P":
                    rooms["Entrada"] = (x, y)

                elif cell == "E":
                    rooms["Portão"] = (x, y)

                elif cell == "B":
                    baus_encontrados += 1
                    nome = f"Baú{baus_encontrados}"
                    rooms[nome] = (x, y)
                    self.chest_rooms.append(nome)

        return rooms

    # ===============================================================
    # 3. Gerar grafo com corredores intermediários
    # ===============================================================
    def _build_graph(self):
        # (A) Criar vértices das salas
        for sala in self.room_positions:
            self.graph.add_vertex(sala)

        intermediarios = {}

        def add_inter(x, y):
            name = f"N{x}_{y}"
            if name not in intermediarios:
                intermediarios[name] = (x, y)
                self.graph.add_vertex(name)
            return name

        def walkable(x, y):
            if 0 <= x < 15 and 0 <= y < 15:
                return self.map_grid[y][x] in (".", "P", "B", "E")
            return False

        for y in range(15):
            for x in range(15):
                if not walkable(x, y):
                    continue

                sala = None
                for nome, pos in self.room_positions.items():
                    if pos == (x, y):
                        sala = nome
                        break

                if not sala:
                    sala = add_inter(x, y)

                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nx, ny = x + dx, y + dy
                    if walkable(nx, ny):
                        viz = None
                        for nome, pos in self.room_positions.items():
                            if pos == (nx, ny):
                                viz = nome
                                break
                        if not viz:
                            viz = add_inter(nx, ny)

                        self.graph.add_edge(sala, viz)

    # ===============================================================
    # 4. Distribuir os itens corretamente pelos 3 baús
    # ===============================================================
    def _assign_items(self):
        """
        Garante exatamente:
        - 1 baú tem CHAVE
        - 1 baú tem POÇÃO
        - 1 baú tem TESOURO
        """

        if len(self.chest_rooms) < 3:
            print("[ALERTA] Existem menos de 3 baús no mapa!")
            self.key_room = self.chest_rooms[0]
            self.chest_contents[self.key_room] = "Chave"
            for outro in self.chest_rooms[1:]:
                self.chest_contents[outro] = random.choice(["Poção", "Tesouro"])
            return

        baus = self.chest_rooms.copy()
        random.shuffle(baus)

        # Definir baú da chave
        self.key_room = baus[0]
        self.chest_contents[self.key_room] = "Chave"

        # Outros itens fixos
        outros_itens = ["Poção", "Tesouro"]
        random.shuffle(outros_itens)

        self.chest_contents[baus[1]] = outros_itens[0]
        self.chest_contents[baus[2]] = outros_itens[1]

    # ===============================================================
    # 5. Eventos ao entrar em sala
    # ===============================================================
    def check_event(self, player):
        sala = player.position

        # ----- BAÚ -----
        if sala in self.chest_rooms:
            conteudo = self.chest_contents.get(sala, None)

            self.chest_rooms.remove(sala)

            if conteudo == "Chave":
                player.open_chest("Chave", "Abre o portão final")
                return False, "Você encontrou a CHAVE!"

            elif conteudo in ("Poção", "Tesouro"):
                player.open_chest(conteudo, "Item encontrado no baú.")
                return False, f"Você encontrou: {conteudo}"

            else:
                return False, "O baú está vazio."

        # ----- PORTÃO -----
        if sala == self.exit_node:
            if player.has_item("Chave"):
                return True, "🏆 Você usou a chave e escapou!"
            else:
                return False, "Você precisa da CHAVE para abrir o portão."

        return False, None

    # ===============================================================
    def show_map(self):
        self.graph.show()
