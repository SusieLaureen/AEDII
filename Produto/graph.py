# ===========================================
# graph.py — Implementação completa de Grafo
# ===========================================
# Usado como MAPA no jogo Explorador de Território 2D.
# Cada vértice é uma sala; cada aresta é um caminho entre salas.
# ===========================================

from collections import deque

class Graph:
    """Classe que representa um grafo não ponderado e não direcionado."""
    
    def __init__(self):
        self.adj = {}  # { vértice: [vizinhos] }

    # ===============================
    # Inserção de vértice
    # ===============================
    def add_vertex(self, v):
        if v not in self.adj:
            self.adj[v] = []
            print(f"[GRAFO] Sala '{v}' adicionada ao mapa.")
        else:
            print(f"[GRAFO] Sala '{v}' já existe.")

    # ===============================
    # Inserção de aresta
    # ===============================
    def add_edge(self, v1, v2):
        if v1 not in self.adj:
            self.add_vertex(v1)
        if v2 not in self.adj:
            self.add_vertex(v2)

        if v2 not in self.adj[v1]:
            self.adj[v1].append(v2)
        if v1 not in self.adj[v2]:
            self.adj[v2].append(v1)
        
        print(f"[GRAFO] Conectadas salas '{v1}' <-> '{v2}'")

    # ===============================
    # Remoção de vértice
    # ===============================
    def remove_vertex(self, v):
        if v in self.adj:
            for vizinhos in self.adj.values():
                if v in vizinhos:
                    vizinhos.remove(v)
            del self.adj[v]
            print(f"[GRAFO] Sala '{v}' removida do mapa.")
        else:
            print(f"[GRAFO] Sala '{v}' não encontrada.")

    # ===============================
    # Remoção de aresta
    # ===============================
    def remove_edge(self, v1, v2):
        if v1 in self.adj and v2 in self.adj[v1]:
            self.adj[v1].remove(v2)
        if v2 in self.adj and v1 in self.adj[v2]:
            self.adj[v2].remove(v1)
        print(f"[GRAFO] Caminho removido entre '{v1}' e '{v2}'.")

    # ===============================
    # Consulta de vizinhos
    # ===============================
    def get_neighbors(self, v):
        return self.adj.get(v, [])

    # ===============================
    # Exibição do mapa
    # ===============================
    def show(self):
        print("\n[GRAFO] Mapa atual do labirinto:")
        for v, vizinhos in self.adj.items():
            print(f"  {v} -> {vizinhos}")
        print()

    # ===============================
    # BFS — Busca em Largura
    # ===============================
    def bfs(self, start, goal):
        """
        Retorna o caminho mais curto entre 'start' e 'goal'.
        Se não houver caminho, retorna [].
        """
        if start not in self.adj or goal not in self.adj:
            print("[BFS] Um dos vértices não existe no mapa.")
            return []

        visitados = set()
        fila = deque([(start, [start])])  # (nó_atual, caminho_até_agora)

        while fila:
            atual, caminho = fila.popleft()

            if atual == goal:
                print(f"[BFS] Caminho encontrado: {caminho}")
                return caminho

            visitados.add(atual)
            for vizinho in self.adj[atual]:
                if vizinho not in visitados:
                    fila.append((vizinho, caminho + [vizinho]))

        print("[BFS] Nenhum caminho encontrado.")
        return []

    # ===============================
    # DFS — Busca em Profundidade
    # ===============================
    def dfs(self, start, visitados=None):
        """
        Percorre o grafo a partir de 'start' usando DFS.
        Retorna a ordem dos vértices visitados.
        """
        if visitados is None:
            visitados = set()

        if start not in self.adj:
            print("[DFS] Vértice inicial inexistente.")
            return []

        visitados.add(start)
        ordem = [start]

        for vizinho in self.adj[start]:
            if vizinho not in visitados:
                ordem.extend(self.dfs(vizinho, visitados))

        return ordem

    def get_collection_path(self, start_node, items_nodes, exit_node):
            """
            Calcula a rota aproximada para pegar todos os itens e depois sair.
            Usa lógica 'Vizinho Mais Próximo': Onde estou -> Item mais perto -> Próximo -> Saída.
            """
            full_path = []
            current_pos = start_node
            to_collect = list(items_nodes) 
            
            while to_collect:
                closest_item = None
                shortest_dist = float('inf')
                path_segment = []

                for item in to_collect:
                    path = self.bfs(current_pos, item)
                    if path and len(path) < shortest_dist:
                        shortest_dist = len(path)
                        closest_item = item
                        path_segment = path

                if closest_item:
                    if full_path:
                        full_path.extend(path_segment[1:])
                    else:
                        full_path.extend(path_segment)
                    
                    current_pos = closest_item
                    to_collect.remove(closest_item)
                else:
                    break
            
            path_exit = self.bfs(current_pos, exit_node)
            if path_exit:
                if full_path:
                    full_path.extend(path_exit[1:])
                else:
                    full_path.extend(path_exit)
                    
            return full_path
