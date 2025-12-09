# Interface.py 
# -------------------------------------------------------------------

import pygame
import sys
import math
from world import World
from player import Player

try:
    from save_load import save_game, load_game
    HAS_SAVE_SYSTEM = True
except ImportError:
    HAS_SAVE_SYSTEM = False

# -------- Configurações Visuais --------
CELL = 40
GRID_W = 15
GRID_H = 15
SIDEBAR_W = 300
SCREEN_W = CELL * GRID_W + SIDEBAR_W
SCREEN_H = CELL * GRID_H
FPS = 60

# Cores
BG = (18, 18, 22)
WALL_COLOR = (20, 23, 30)
GROUND_COLOR = (38, 46, 57)
GRID_LINE_COLOR = (28, 34, 44)
FOG_COLOR = (10, 10, 12, 230)

PLAYER_COLOR = (0, 190, 255)
PLAYER_GLOW = (0, 150, 255, 60)
CHEST_CLOSED = (183, 102, 205)
CHEST_OPEN = (110, 90, 120)
EXIT_LOCKED = (245, 188, 75)
EXIT_OPEN = (140, 230, 150)
INTERMEDIATE_NODE = (60, 70, 80)

PATH_HIGHLIGHT = (255, 215, 0, 120)

TEXT_COLOR = (235, 235, 240)
SIDEBAR_BG = (30, 30, 40)
SIDEBAR_BORDER = (80, 80, 95)

# Inicialização
pygame.init()
FONT = pygame.font.SysFont("arial", 16)
FONT_SMALL = pygame.font.SysFont("arial", 12)
FONT_TITLE = pygame.font.SysFont("arial", 22, bold=True)
FONT_VICTORY = pygame.font.SysFont("arial", 40, bold=True)

# -------- Funções Auxiliares --------

def draw_text(surf, txt, x, y, font=FONT, color=TEXT_COLOR):
    img = font.render(txt, True, color)
    surf.blit(img, (x, y))

def node_to_coord(name, world):
    """Converte nome do nó para (x, y) no grid."""
    if name in world.room_positions:
        return world.room_positions[name]
    if name.startswith("N"): 
        try:
            parts = name[1:].split("_")
            return int(parts[0]), int(parts[1])
        except:
            return None
    return None

def coord_to_node_at(gx, gy, world):
    """Retorna o nome do nó na posição (gx, gy) do grid."""
    for name, pos in world.room_positions.items():
        if pos == (gx, gy):
            return name
    if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
        if world.map_grid[gy][gx] in (".", "P", "B", "E"):
            return f"N{gx}_{gy}"
    return None

def draw_arrow_line(surface, color, start, end, width=3):
    """Desenha uma linha com uma seta na ponta indicando direção."""
    
    pygame.draw.line(surface, color, start, end, width)
    
    rotation = math.degrees(math.atan2(start[1] - end[1], end[0] - start[0])) + 90

    arrow_len = 10
    angle = math.radians(rotation)
    
    tip = (end[0] - math.sin(angle) * 5, 
           end[1] - math.cos(angle) * 5)
    
    side_len = 8
    angle1 = math.radians(rotation - 150)
    angle2 = math.radians(rotation + 150)
    
    p1 = (tip[0] + math.sin(angle1) * side_len, tip[1] + math.cos(angle1) * side_len)
    p2 = (tip[0] + math.sin(angle2) * side_len, tip[1] + math.cos(angle2) * side_len)
    
    pygame.draw.polygon(surface, color, [tip, p1, p2])
# -------- Classe Principal --------

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Explorador de Território 2D - Final")
        self.clock = pygame.time.Clock()

        # Backend
        self.world = World()
        self.player = Player("Explorador", self.world.start_node)
        self.graph = self.world.graph

        # Estado Visual
        self.highlight_path = [] 
        self.message = "Use WASD ou Setas para mover!"
        self.message_timer = 180
        self.event_log = [] 
        self.game_over = False
        self.victory_timer = 0
        self.show_comparison = False  
        self.machine_path_cache = []

    def set_message(self, txt):
        self.message = txt
        self.message_timer = 180
        self.event_log.append(txt)
        if len(self.event_log) > 6:
            self.event_log.pop(0)

    # --- Lógica de Movimento ---
    def try_move_player(self, target_node):
        """Tenta mover o jogador para o nó alvo."""
        if not target_node: return

        current = self.player.position
        neighbors = self.graph.get_neighbors(current)

        if target_node in neighbors:
            self.player.move(target_node)
            self.highlight_path = [] 
            
            venceu, msg = self.world.check_event(self.player)
            if msg: self.set_message(msg)
            if venceu:
                self.game_over = True
                self.machine_path_cache = self.calculate_machine_best_route(from_current_state=False)
                self.set_message("VITÓRIA!")
        else:
            if target_node == current:
                self.set_message("Você já está aqui.")
            else:
                self.set_message("Parede ou caminho bloqueado!")

    # --- Lógica de Save/Load ---
    def do_save(self):
        if HAS_SAVE_SYSTEM:
            save_game(self.player)
            self.set_message("Jogo Salvo!")
        else:
            self.set_message("Erro: save_load.py ausente")

    def do_load(self):
        if HAS_SAVE_SYSTEM:
            # Agora recebe 3 valores
            pos, inv, steps = load_game()
            if pos:
                self.world = World() 
                self.player = Player("Explorador", pos)
                self.player.inventory = inv
                self.player.step_count = steps # Restaura passos
                
                self.graph = self.world.graph
                self.reveal_area()
                self.highlight_path = []
                self.set_message("Jogo Carregado!")
            else:
                self.set_message("Nenhum save encontrado.")
        else:
            self.set_message("Erro: save_load.py ausente")

    # --- Input ---
    def handle_click(self, mx, my):
        if self.game_over: return
        if mx > GRID_W * CELL: return
        
        gx, gy = mx // CELL, my // CELL
        target = coord_to_node_at(gx, gy, self.world)
        self.try_move_player(target)

    def handle_keys(self, event):
        # -------------------------------------------------
        # 1. COMANDOS DE FIM DE JOGO (Vitória/Game Over)
        # -------------------------------------------------
        if self.game_over:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            
            elif event.key == pygame.K_c:
                self.show_comparison = not self.show_comparison
            # --------------------------------
                
            return 

        # -------------------------------------------------
        # 2. MOVIMENTAÇÃO 
        # -------------------------------------------------
        dx, dy = 0, 0
        if event.key in [pygame.K_UP, pygame.K_w]: dy = -1
        elif event.key in [pygame.K_DOWN, pygame.K_s]: dy = 1
        elif event.key in [pygame.K_LEFT, pygame.K_a]: dx = -1
        elif event.key in [pygame.K_RIGHT, pygame.K_d]: dx = 1
        
        if dx != 0 or dy != 0:
            current_coord = node_to_coord(self.player.position, self.world)
            if current_coord:
                cx, cy = current_coord
                target_node = coord_to_node_at(cx + dx, cy + dy, self.world)
                self.try_move_player(target_node)
            return

        # -------------------------------------------------
        # 3. FERRAMENTAS E DEBUG
        # -------------------------------------------------
        
        # B: BFS (Caminho mais curto APENAS para a saída)
        if event.key == pygame.K_b:
            path = self.graph.bfs(self.player.position, self.world.exit_node)
            if path:
                self.highlight_path = path
                self.set_message("Dica Ativada (BFS Simples)")
            else:
                self.set_message("Sem caminho possível.")

        # V: DFS (Varredura - Visualizar algoritmo)
       # elif event.key == pygame.K_v:
       #     path = self.graph.dfs(self.player.position)
       #     if path:
       #         self.highlight_path = path
       #         self.set_message("Visualizando DFS (Varredura)")
       #     else:
       #         self.set_message("Erro no DFS")
        
        # H: Hint Avançado (Rota Ótima da Máquina: Coletar tudo -> Sair)
        elif event.key == pygame.K_h:
            path = self.calculate_machine_best_route(from_current_state=True)
            if path:
                self.highlight_path = path
                self.set_message("Rota Ótima (Coletar tudo -> Sair)")
            else:
                self.set_message("Não consigo calcular rota completa.")

        # -------------------------------------------------
        # 4. SISTEMA (Save / Load)
        # -------------------------------------------------
        elif event.key == pygame.K_F5:
            self.do_save()
            
        elif event.key == pygame.K_F9:
            self.do_load()

    # --- Renderização ---
    def draw(self):
        self.screen.fill(BG)
        
        # 1. Grid
        for y in range(GRID_H):
            for x in range(GRID_W):
                rect = (x*CELL, y*CELL, CELL, CELL)
                color = WALL_COLOR if self.world.map_grid[y][x] == "#" else GROUND_COLOR
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, GRID_LINE_COLOR, rect, 1)

        # 2. Dica 
        if self.highlight_path:
            # A. PREPARAÇÃO
            coords = []
            for node in self.highlight_path:
                c = node_to_coord(node, self.world)
                if c: coords.append(c)
            
            # B. FUNDO (Marca o território percorrido)
            s = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
            s.fill((255, 215, 0, 50)) 
            
            for cx, cy in coords:
                self.screen.blit(s, (cx*CELL, cy*CELL))
                pygame.draw.rect(self.screen, (255, 215, 0), (cx*CELL, cy*CELL, CELL, CELL), 1)

           # C. SETAS 
            if len(coords) > 1:
                COLORS = [
                    (0, 255, 255),   # 1. Ciano
                    (255, 140, 0),   # 2. Laranja
                    (255, 0, 255),   # 3. Magenta
                    (50, 255, 50),   # 4. Verde
                    (255, 255, 0),   # 5. Amarelo
                    (255, 255, 255)  # 6. Branco
                ]
                
                color_idx = 0
                current_layer_history = set()
                current_layer_history.add(tuple(coords[0]))
                
                tile_visit_counts = {}
                
                total_points = len(coords)
                
                for i in range(total_points - 1):
                    curr = coords[i]
                    next_p = coords[i+1]
                 
                    if tuple(next_p) in current_layer_history:
                        color_idx = (color_idx + 1) % len(COLORS)
                        current_layer_history.clear() 
                    
                    current_layer_history.add(tuple(next_p))
                    
                    tile_key = (curr[0], curr[1])
                    pass_count = tile_visit_counts.get(tile_key, 0)
                    tile_visit_counts[tile_key] = pass_count + 1
                    
                    dx = next_p[0] - curr[0]
                    dy = next_p[1] - curr[1]
                    
                    center_x = curr[0]*CELL + CELL//2
                    center_y = curr[1]*CELL + CELL//2
                    
                    forward_shift = 9
                    
                    if pass_count == 0: side_shift = 0
                    elif pass_count % 2 == 1: side_shift = 5
                    else: side_shift = -5
                    
                    cx = center_x + (dx * forward_shift) + (dy * side_shift)
                    cy = center_y + (dy * forward_shift) + (dx * side_shift)
                    
                    size = 5
                    if dx == 1:   points = [(cx+size, cy), (cx-size, cy-size), (cx-size, cy+size)]
                    elif dx == -1: points = [(cx-size, cy), (cx+size, cy-size), (cx+size, cy+size)]
                    elif dy == 1:  points = [(cx, cy+size), (cx-size, cy-size), (cx+size, cy-size)]
                    elif dy == -1: points = [(cx, cy-size), (cx-size, cy+size), (cx+size, cy+size)]
                    else: continue

                    current_color = COLORS[color_idx]
                    
                    pygame.draw.polygon(self.screen, current_color, points)
                    pygame.draw.polygon(self.screen, (0,0,0), points, 1)

            # D. DESTINO
            if coords:
                end_x, end_y = coords[-1]
                pygame.draw.circle(self.screen, (255, 50, 50), 
                                 (end_x*CELL + CELL//2, end_y*CELL + CELL//2), 6)
        # 3. Entidades (Baús e Saída)
        for name, pos in self.world.room_positions.items():
            cx, cy = pos[0]*CELL + CELL//2, pos[1]*CELL + CELL//2
            
            # Baús
            if name.startswith("Bau"): 
                if name in self.world.chest_rooms:
                    color = CHEST_CLOSED
                else:
                    color = CHEST_OPEN
                
                pygame.draw.rect(self.screen, color, (cx-10, cy-10, 20, 20), border_radius=4)
            
            # Saída
            elif name == "Portão":
                color = EXIT_OPEN if self.player.has_item("Chave") else EXIT_LOCKED
                pygame.draw.circle(self.screen, color, (cx, cy), 12, width=3)
                draw_text(self.screen, "SAÍDA", cx-15, cy-25, FONT_SMALL, color=color)
                
            # Entrada
            elif name == "Entrada":
                pygame.draw.circle(self.screen, (100, 100, 100), (cx, cy), 8)

        # 4. Jogador (Quadrado)
        pc = node_to_coord(self.player.position, self.world)
        if pc:
            rect = (pc[0] * CELL, pc[1] * CELL, CELL, CELL)
            pygame.draw.rect(self.screen, PLAYER_COLOR, rect)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)

        # 6. Sidebar (Menu lateral)
        self.draw_sidebar()

        if self.game_over:
            if self.show_comparison:
                self.draw_comparison_screen()
            else:
                self.draw_victory_screen()
        # --------------------------------------

        pygame.display.flip()

    def draw_sidebar(self):
        # Fundo
        rect = (GRID_W*CELL, 0, SIDEBAR_W, SCREEN_H)
        pygame.draw.rect(self.screen, SIDEBAR_BG, rect)
        pygame.draw.line(self.screen, SIDEBAR_BORDER, (GRID_W*CELL, 0), (GRID_W*CELL, SCREEN_H), 2)
        
        x = GRID_W*CELL + 20
        y = 20
        
        draw_text(self.screen, "EXPLORADOR 2D", x, y, FONT_TITLE)
        y += 30
        draw_text(self.screen, f"Local: {self.player.position}", x, y, FONT_SMALL)
        y += 20
        # Exibe os passos do jogador
        draw_text(self.screen, f"Passos: {self.player.step_count}", x, y, FONT, (255, 255, 0))
        y += 30
        
        # Inventário
        draw_text(self.screen, "INVENTÁRIO (AVL)", x, y, FONT, (100, 200, 255))
        y += 20
        items = []
        def collect(node):
            if node:
                collect(node.left)
                items.append(node.key)
                collect(node.right)
        collect(self.player.inventory.root)
        
        if not items:
            draw_text(self.screen, "- Vazio", x, y, color=(150,150,150))
            y += 20
        else:
            for item in items:
                col = (255, 215, 0) if item == "Chave" else TEXT_COLOR
                draw_text(self.screen, f"- {item}", x, y, color=col)
                y += 20
        
        # Menu de Controles
        y = SCREEN_H - 220
        draw_text(self.screen, "CONTROLES", x, y, FONT, (200, 200, 100))
        y += 25
        controls = [
            "WSAD / Setas : Mover",
            "B : Dica (BFS)",
           # "V : Varredura (DFS)",
            "H : Rota Ótima (Coletar Tudo)",
            "F5 : Salvar",
            "F9 : Carregar"
        ]
        for c in controls:
            draw_text(self.screen, c, x, y, FONT_SMALL, (180, 180, 180))
            y += 18

        # Mensagens
        y = SCREEN_H - 80
        if self.message_timer > 0:
            self.message_timer -= 1
            draw_text(self.screen, f"> {self.message}", x, y, color=(255, 100, 100))

    def calculate_machine_best_route(self, from_current_state=False):
        """
        Calcula a rota da máquina.
    
        """
        
        if from_current_state:
            start = self.player.position
            baus_para_pegar = list(self.world.chest_rooms) 
        else:
            start = self.world.start_node 
            baus_para_pegar = list(self.world.all_chests_backup) 
        
        saida = self.world.exit_node
        
        if hasattr(self.graph, 'get_collection_path'):
            rota = self.graph.get_collection_path(start, baus_para_pegar, saida)
            return rota
        
        return []
    
    def draw_comparison_screen(self):
        """Desenha a tela dividida com dois mini-mapas."""
        self.screen.fill((10, 10, 15)) 
        
        # Título
        draw_text(self.screen, "ANÁLISE DE DESEMPENHO", SCREEN_W//2 - 100, 30, FONT_TITLE, (255, 255, 255))
        
        mini_cell = 20
        margin_x = 50
        start_y = 100
        
        # --- LADO ESQUERDO: JOGADOR ---
        draw_text(self.screen, "SUA ROTA", margin_x, start_y - 30, FONT, (0, 190, 255))
        player_path_list = self.player.history 
        
        self.draw_mini_map(margin_x, start_y, mini_cell, player_path_list, (0, 190, 255), is_list=True)
        # -----------------
        
        # Estatísticas Jogador
        stats_y = start_y + (15 * mini_cell) + 20
        draw_text(self.screen, f"Passos: {self.player.step_count}", margin_x, stats_y, FONT_SMALL)
        
        
        # --- LADO DIREITO: MÁQUINA ---
        machine_x = margin_x + (15 * mini_cell) + 100
        draw_text(self.screen, "ROTA OTIMIZADA (IA)", machine_x, start_y - 30, FONT, (255, 215, 0))
        
        machine_path_list = self.machine_path_cache
        self.draw_mini_map(machine_x, start_y, mini_cell, machine_path_list, (255, 215, 0), is_list=True)
        
        # Estatísticas Máquina
        passos_ia = len(machine_path_list) if machine_path_list else 0
        draw_text(self.screen, f"Passos Ideais: {passos_ia}", machine_x, stats_y, FONT_SMALL, (255, 215, 0))
        
        # Diferença
        diff = self.player.step_count - passos_ia
        color_diff = (100, 255, 100) if diff <= 5 else (255, 100, 100)
        draw_text(self.screen, f"Diferença: {diff} passos", SCREEN_W//2 - 60, stats_y + 40, FONT, color_diff)
        
        # Rodapé
        draw_text(self.screen, "Pressione 'C' para voltar | ESC para sair", SCREEN_W//2 - 120, SCREEN_H - 40, FONT_SMALL, (150, 150, 150))

    def draw_mini_map(self, offset_x, offset_y, cell_size, path_data, base_color, is_list=False):
        """Mini-mapa com lógica de Cores por Camada ."""
        
        # 1. Desenha o Grid 
        for y in range(15):
            for x in range(15):
                rect = (offset_x + x*cell_size, offset_y + y*cell_size, cell_size, cell_size)
                char = self.world.map_grid[y][x]
                
                if char == "#": color = (30, 30, 40)
                elif char == "E": color = (80, 40, 40)
                elif char == "P": color = (40, 40, 80)
                else: color = (15, 15, 20)
                
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (25, 25, 30), rect, 1)

        # 2. Desenha o Caminho
        if is_list: 
            coords = []
            for node in path_data:
                if isinstance(node, tuple): coords.append(node)
                else:
                    c = node_to_coord(node, self.world)
                    if c: coords.append(c)
            
            if len(coords) > 1:
                COLORS = [
                    (0, 255, 255),   # 1. Ciano
                    (255, 140, 0),   # 2. Laranja
                    (255, 0, 255),   # 3. Magenta
                    (50, 255, 50),   # 4. Verde
                    (255, 255, 0),   # 5. Amarelo
                    (255, 255, 255)  # 6. Branco
                ]
                
                color_idx = 0
                current_layer_history = set()
                current_layer_history.add(tuple(coords[0]))
                
                tile_visit_counts = {}
                total_points = len(coords)
                
                for i in range(total_points - 1):
                    curr = coords[i]
                    next_p = coords[i+1]
                    
                    if tuple(next_p) in current_layer_history:
                        color_idx = (color_idx + 1) % len(COLORS)
                        current_layer_history.clear()
                    
                    current_layer_history.add(tuple(next_p))
                    
                    tile_key = (curr[0], curr[1])
                    pass_count = tile_visit_counts.get(tile_key, 0)
                    tile_visit_counts[tile_key] = pass_count + 1
                    
                    dx = next_p[0] - curr[0]
                    dy = next_p[1] - curr[1]
                    
                    center_x = offset_x + curr[0]*cell_size + cell_size//2
                    center_y = offset_y + curr[1]*cell_size + cell_size//2
                    
                    forward_shift = cell_size // 2 - 2  
                    
                    if pass_count == 0: side_shift = 0
                    elif pass_count % 2 == 1: side_shift = 3  
                    else: side_shift = -3
                    
                    cx = center_x + (dx * forward_shift) + (dy * side_shift)
                    cy = center_y + (dy * forward_shift) + (dx * side_shift)
                
                    size = 3 
                    
                    if dx == 1:   points = [(cx+size, cy), (cx-size, cy-size), (cx-size, cy+size)]
                    elif dx == -1: points = [(cx-size, cy), (cx+size, cy-size), (cx+size, cy+size)]
                    elif dy == 1:  points = [(cx, cy+size), (cx-size, cy-size), (cx+size, cy-size)]
                    elif dy == -1: points = [(cx, cy-size), (cx-size, cy+size), (cx+size, cy+size)]
                    else: continue

                    current_color = COLORS[color_idx]
                    
                    pygame.draw.polygon(self.screen, current_color, points)

                # Ponto Final 
                last = coords[-1]
                lx = offset_x + last[0]*cell_size + cell_size//2
                ly = offset_y + last[1]*cell_size + cell_size//2
                pygame.draw.circle(self.screen, (255, 50, 50), (lx, ly), 3)

        else: 
            for (tile_x, tile_y) in path_data:
                 rect = (offset_x + tile_x*cell_size, offset_y + tile_y*cell_size, cell_size, cell_size)
                 pygame.draw.rect(self.screen, base_color, rect)
                 pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)

    def draw_victory_screen(self):


        self.victory_timer += 1
        
        # 1. Fundo Escurecido
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220)) 
        self.screen.blit(overlay, (0,0))
        
        center_x = SCREEN_W // 2
        
        # 2. Título
        cols = [(255,215,0), (255,100,100), (100,255,100)]
        c = cols[(self.victory_timer // 10) % 3]
        
        txt = FONT_VICTORY.render("VITÓRIA!", True, c)
        self.screen.blit(txt, txt.get_rect(center=(center_x, SCREEN_H//2 - 110)))
        
        sub = FONT.render("Você escapou do labirinto!", True, (255, 255, 255))
        self.screen.blit(sub, sub.get_rect(center=(center_x, SCREEN_H//2 - 60)))

        # 3. Estatísticas do Jogador (Contagem de Itens)
        player_items_count = 0
        def count_inv(node):
            nonlocal player_items_count
            if node:
                player_items_count += 1
                count_inv(node.left)
                count_inv(node.right)
        count_inv(self.player.inventory.root)
        
        # Total de baús possíveis (Máquina sempre pega tudo)
        total_items_possible = len(self.world.all_chests_backup)
        
        # 4. Cálculos da Máquina
        rota_maquina = self.machine_path_cache if self.machine_path_cache else self.calculate_machine_best_route()
        passos_maquina = len(rota_maquina) if rota_maquina else 0
        
        # 5. Avaliação Inteligente
        if player_items_count < total_items_possible:
            avaliacao = "Exploração Incompleta!"
            cor_av = (255, 165, 0) # Laranja
        else:
            # Se pegou tudo, compara os passos
            diff = self.player.step_count - passos_maquina
            if diff <= 5:
                avaliacao = "PERFEITO! (100% + Rota Ótima)"
                cor_av = (100, 255, 100)
            elif diff < 20:
                avaliacao = "Muito bom! (100% Coletado)"
                cor_av = (255, 255, 100)
            else:
                avaliacao = "Eficiência Baixa..."
                cor_av = (255, 100, 100)

        # 6. Renderização das Estatísticas
        stats_y = SCREEN_H // 2 
        
        # --- BLOCO 1: JOGADOR ---
        draw_text(self.screen, "--- SEU DESEMPENHO ---", center_x - 90, stats_y, FONT_SMALL, (0, 200, 255))
        draw_text(self.screen, f"Passos: {self.player.step_count}", center_x - 80, stats_y + 20, FONT, (200, 255, 255))
        
        # Cor condicional para itens do jogador
        col_item = (100, 255, 100) if player_items_count == total_items_possible else (255, 100, 100)
        draw_text(self.screen, f"Itens: {player_items_count} / {total_items_possible}", center_x - 80, stats_y + 45, FONT, col_item)
        
        # --- BLOCO 2: MÁQUINA (IA) ---
        stats_y += 85
        draw_text(self.screen, "--- DESEMPENHO IDEAL (IA) ---", center_x - 90, stats_y, FONT_SMALL, (255, 215, 0))
        draw_text(self.screen, f"Passos: {passos_maquina}", center_x - 80, stats_y + 20, FONT, (255, 255, 200))
        draw_text(self.screen, f"Itens: {total_items_possible} / {total_items_possible} (100%)", center_x - 80, stats_y + 45, FONT, (255, 215, 0))
        
        # --- BLOCO 3: CONCLUSÃO ---
        stats_y += 80
        draw_text(self.screen, f"Resultado: {avaliacao}", center_x - 80, stats_y, FONT, cor_av)
        
        # 7. Rodapé (Teclas)
        info2 = FONT_SMALL.render("[ TECLA 'C' ] COMPARAR ROTAS VISUALMENTE", True, (0, 255, 255))
        self.screen.blit(info2, info2.get_rect(center=(center_x, SCREEN_H - 70)))
        
        info = FONT_SMALL.render("Pressione ESC para sair", True, (150, 150, 150))
        self.screen.blit(info, info.get_rect(center=(center_x, SCREEN_H - 40)))

        # 8. Efeito de Confete
        import random
        random.seed(self.victory_timer // 5)
        for _ in range(25): 
            sx = random.randint(0, SCREEN_W)
            sy = random.randint(0, SCREEN_H)
            pygame.draw.circle(self.screen, (255, 255, 200), (sx, sy), 2)
   
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos[0], event.pos[1])
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: running = False
                    else: self.handle_keys(event)
            
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()
