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

        self.chest_rooms = []       
        self.all_chests_backup = [] # nomes dos baús
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
        Tenta gerar um mapa válido. Se gerar um mapa impossível (sem saída),
        tenta novamente até conseguir.
        """
        attempt = 1
        while True:
            # 1. Gera um layout candidato
            grid = self._create_candidate_layout()
            
            # 2. Verifica se é possível ir do Início (0,0) ao Fim (14,14)
            if self._is_solvable(grid):
                return grid
            
            attempt += 1
            # Segurança para não travar loop infinito 
            if attempt > 100:
                print("ERRO CRÍTICO: Não foi possível gerar mapa aleatório. Usando fallback.")
                return self._create_fallback_map()

    def _create_candidate_layout(self):
        """Gera a matriz 15x15 com paredes aleatórias ."""
        width, height = 15, 15
        grid = [['.' for _ in range(width)] for _ in range(height)]
        
        # Marca Entrada e Saída
        grid[0][0] = "P"
        grid[14][14] = "E"
        
        import random
        # Paredes aleatórias
        for y in range(height):
            for x in range(width):
                # Protege a área de start e end para não bloquear de cara
                if (x, y) in [(0,0), (14,14), (0,1), (1,0), (14,13), (13,14)]:
                    continue
                
                # 25% de chance de parede 
                if random.random() < 0.25: 
                    grid[y][x] = "#"
        
        # Distribui 6 Baús em posições livres
        count_baus = 0
        while count_baus < 6:
            rx = random.randint(0, 14)
            ry = random.randint(0, 14)
            if grid[ry][rx] == ".":
                grid[ry][rx] = "B"
                count_baus += 1
                
        return grid

    def _is_solvable(self, grid):
        """
        Verifica se é possível ir do Início (P) para a Saída (E)
        E tambem se todos os baús (B) são acessíveis.
        """
        start = (0, 0)
        # Encontra coordenadas de todos os baús e da saída
        targets = []
        rows = len(grid)
        cols = len(grid[0])
        
        for y in range(rows):
            for x in range(cols):
                if grid[y][x] == "E":
                    targets.append((x, y)) # Saída é obrigatória
                elif grid[y][x] == "B":
                    targets.append((x, y)) # Baús são obrigatórios
        
        # BFS para encontrar tudo que é alcançável
        queue = [start]
        visited = set()
        visited.add(start)
        reachable_targets = 0
        
        while queue:
            cx, cy = queue.pop(0)
            
            # Se chegamos em um alvo (Exit ou Bau), contamos
            if (cx, cy) in targets:
                reachable_targets += 1
                # Se já achou todos, pode parar cedo
                if reachable_targets == len(targets):
                    return True

            # Vizinhos
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < cols and 0 <= ny < rows:
                    if (nx, ny) not in visited and grid[ny][nx] != "#":
                        visited.add((nx, ny))
                        queue.append((nx, ny))
        
        # Só retorna True se achou TODOS os alvos 
        return reachable_targets == len(targets)

    def _create_fallback_map(self):
        """Retorna o mapa fixo original caso o aleatório falhe (segurança)."""
        raw = [
            "###############",
            "#P........#..B#",
            "#.#######.###.#",
            "#.......#...#.#",
            "#.#######.###.#",
            "#.#...#.......#",
            "#.#.#####.#####",
            "#.......#.....#",
            "#######.#####.#",
            "#B..#...#...#B#",
            "#.###.#####.#.#",
            "#...#...#B..#.#",
            "###.###.###.#.#",
            "#.....B......E#",
            "###############"
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
                    nome = f"Bau_{baus_encontrados}"
                    rooms[nome] = (x, y)
                    self.chest_rooms.append(nome)
        self.all_chests_backup = list(self.chest_rooms)
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
    # ==============================================================

    def _assign_items(self):
        """Distribui itens ÚNICOS: Chave (Fixa) + 5 Aleatórios sem repetição."""
        if not self.chest_rooms: return

        import random
        baus = self.chest_rooms.copy()
        random.shuffle(baus)
        
        # 1. Garante a Chave no primeiro baú da lista embaralhada
        self.key_room = baus[0]
        self.chest_contents[self.key_room] = "Chave"
        
        # 2. Pool de itens possíveis 
        pool_de_itens = [
            "Poção Azul", "Poção Vermelha", "Ouro", "Diamante", 
            "Rubi", "Esmeralda", "Pergaminho", "Cálice", 
            "Anel", "Colar", "Coroa", "Espada Velha"
        ]
        
        qtd_para_preencher = len(baus) - 1
        
        # 3. Seleciona itens aleatorios e unicos do pool
        if qtd_para_preencher > 0:
            itens_escolhidos = random.sample(pool_de_itens, qtd_para_preencher)
            
            # Preenche os baús restantes
            for i, sala in enumerate(baus[1:]):
                self.chest_contents[sala] = itens_escolhidos[i]

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

            elif conteudo: # 
                player.open_chest(conteudo, "Item encontrado.")
                return False, f"Você encontrou: {conteudo}"
        # -----------------------
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
