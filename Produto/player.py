# ===========================================
# player.py — Classe do Jogador 
# ===========================================

from tree import AVLTree

class Player:
    """Representa o jogador do jogo Explorador de Território."""

    def __init__(self, name, start_position):
        self.name = name
        self.position = start_position  # posição atual 
        self.inventory = AVLTree()      # inventário como árvore AVL
        self.step_count = 0    
        self.history = [start_position]        

    # ===============================
    # Movimento
    # ===============================
    def move(self, new_position):
        """Move o jogador para uma nova sala."""
        # Atualiza a posição
        self.position = new_position
        self.step_count += 1
        self.history.append(new_position)
    # ===============================
    # Gerenciamento do inventário
    # ===============================
    def add_item(self, item, description=None):
        """Adiciona um item ao inventário."""
        self.inventory.insert(item, description)

    def remove_item(self, item):
        """Remove um item do inventário."""
        self.inventory.remove(item)

    def has_item(self, item):
        """Verifica se o jogador possui determinado item."""
        node = self.inventory.search(item)
        return node is not None

    def show_inventory(self):
        """Mostra o inventário atual (útil para o modo texto)."""
        self.inventory.inorder()

    # ===============================
    # Interação com o ambiente
    # ===============================
    def open_chest(self, item_name, description=None):
        """Simula abrir um baú e coletar o item."""
        self.add_item(item_name, description)
