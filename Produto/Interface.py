# Interface.py 
# -------------------------------------------------------------------

import pygame
import sys
from world import World
from player import Player

# Tenta importar o save_load
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
        self.visited_tiles = set() 
        self.message = "Use WASD ou Setas para mover!"
        self.message_timer = 180
        self.event_log = [] 
        self.game_over = False
        self.victory_timer = 0

        self.reveal_area()

    def reveal_area(self):
        """Revela tiles ao redor do jogador."""
        coords = node_to_coord(self.player.position, self.world)
        if coords:
            cx, cy = coords
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                        if self.world.map_grid[ny][nx] != "#":
                            self.visited_tiles.add((nx, ny))

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
            # Movimento Válido 
            self.player.move(target_node)
            
            self.reveal_area()
            self.highlight_path = [] 
            
            # Eventos do Backend
            venceu, msg = self.world.check_event(self.player)
            if msg: self.set_message(msg)
            if venceu:
                self.game_over = True
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
        if self.game_over: return

        # Movimentação WASD / Setas
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

        # Outros comandos
        if event.key == pygame.K_c:
            path = self.graph.bfs(self.player.position, self.world.exit_node)
            if path:
                self.highlight_path = path
                self.set_message("Dica Ativada (Caminho Ótimo)")
            else:
                self.set_message("Sem caminho possível.")

        elif event.key == pygame.K_v:
            # DFS: Mostra a "Varredura" completa (mostra por onde o algoritmo tenta ir)
            path = self.graph.dfs(self.player.position)
            if path:
                self.highlight_path = path
                self.set_message("Visualizando DFS (Varredura)")
            else:
                self.set_message("Erro no DFS")
        # ----------------------------------

        elif event.key == pygame.K_F5:
            self.do_save()
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

        # 2. Dica (Highlight)
        if self.highlight_path:
            s = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
            s.fill(PATH_HIGHLIGHT)
            for node in self.highlight_path:
                coord = node_to_coord(node, self.world)
                if coord:
                    self.screen.blit(s, (coord[0]*CELL, coord[1]*CELL))

        # 3. Entidades
        # Nós Intermediários
        for v in self.graph.adj.keys():
            if v not in self.world.room_positions:
                c = node_to_coord(v, self.world)
                if c:
                    cx, cy = c[0]*CELL + CELL//2, c[1]*CELL + CELL//2
                    pygame.draw.rect(self.screen, INTERMEDIATE_NODE, (cx-3, cy-3, 6, 6))

        # Salas Especiais
        for name, pos in self.world.room_positions.items():
            cx, cy = pos[0]*CELL + CELL//2, pos[1]*CELL + CELL//2
            if name in self.world.chest_contents:  
                    if name in self.world.chest_rooms:
                        color = CHEST_CLOSED
                    else:
                        color = CHEST_OPEN
                    pygame.draw.rect(self.screen, color, (cx-10, cy-10, 20, 20), border_radius=4)

            elif name == "Portão":
                color = EXIT_OPEN if self.player.has_item("Chave") else EXIT_LOCKED
                pygame.draw.circle(self.screen, color, (cx, cy), 12, width=3)
                draw_text(self.screen, "SAÍDA", cx-15, cy-25, font=FONT_SMALL, color=color)
            elif name == "Entrada":
                pygame.draw.circle(self.screen, (100, 100, 100), (cx, cy), 8)

        # 4. Jogador
        pc = node_to_coord(self.player.position, self.world)
        if pc:
            px, py = pc[0]*CELL + CELL//2, pc[1]*CELL + CELL//2
            glow = pygame.Surface((CELL*3, CELL*3), pygame.SRCALPHA)
            pygame.draw.circle(glow, PLAYER_GLOW, (CELL*1.5, CELL*1.5), CELL)
            self.screen.blit(glow, (px-CELL*1.5, py-CELL*1.5), special_flags=pygame.BLEND_ADD)
            pygame.draw.circle(self.screen, PLAYER_COLOR, (px, py), 9)

        # 5. Neblina
        fog_surf = pygame.Surface((GRID_W*CELL, GRID_H*CELL), pygame.SRCALPHA)
        for y in range(GRID_H):
            for x in range(GRID_W):
                if (x, y) not in self.visited_tiles and self.world.map_grid[y][x] != "#":
                    pygame.draw.rect(fog_surf, FOG_COLOR, (x*CELL, y*CELL, CELL, CELL))
        self.screen.blit(fog_surf, (0,0))

        # 6. UI
        self.draw_sidebar()

        if self.game_over:
            self.draw_victory_screen()

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
            "C : Dica (BFS)",
            "V : Varredura (DFS)",
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

    def draw_victory_screen(self):
        self.victory_timer += 1
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220)) 
        self.screen.blit(overlay, (0,0))
        
        center_x = SCREEN_W // 2
        
        cols = [(255,215,0), (255,100,100), (100,255,100)]
        c = cols[(self.victory_timer // 10) % 3]
        
        txt = FONT_VICTORY.render("VITÓRIA!", True, c)
        self.screen.blit(txt, txt.get_rect(center=(center_x, SCREEN_H//2 - 60)))
        
        sub = FONT.render("Você escapou do labirinto!", True, (255, 255, 255))
        self.screen.blit(sub, sub.get_rect(center=(center_x, SCREEN_H//2 - 10)))

        # Estatísticas Finais
        items_count = 0
        def count_inv(node):
            nonlocal items_count
            if node:
                items_count += 1
                count_inv(node.left)
                count_inv(node.right)
        count_inv(self.player.inventory.root)

        stats_y = SCREEN_H // 2 + 40
        draw_text(self.screen, f"Passos Totais: {self.player.step_count}", center_x - 60, stats_y, FONT, (100, 255, 255))
        draw_text(self.screen, f"Itens Coletados: {items_count}", center_x - 60, stats_y + 25, FONT, (255, 215, 0))

        info = FONT_SMALL.render("Pressione ESC para sair", True, (150, 150, 150))
        import random
        random.seed(self.victory_timer // 5)

        for _ in range(25): 
            sx = random.randint(0, SCREEN_W)
            sy = random.randint(0, SCREEN_H)
            pygame.draw.circle(self.screen, (255, 255, 200), (sx, sy), 3)
        self.screen.blit(info, info.get_rect(center=(center_x, SCREEN_H - 40)))

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