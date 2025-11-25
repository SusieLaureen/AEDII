# ===========================================
# tree.py — Implementação de Árvore AVL
# ===========================================
# Esta estrutura será usada como INVENTÁRIO no jogo Explorador de Território 2D.
# Cada item coletado será armazenado como um nó da árvore.
# A AVL garante que as operações de inserção, busca e remoção sejam O(log n).
# ===========================================

class Node:
    """Classe que representa um nó da árvore AVL."""
    def __init__(self, key, data=None):
        self.key = key            # chave do item 
        self.data = data          # dado associado 
        self.left = None          # filho esquerdo
        self.right = None         # filho direito
        self.height = 1           # altura do nó (usada para balanceamento)


class AVLTree:
    """Classe principal da árvore AVL."""
    def __init__(self):
        self.root = None

    # ===============================
    # Função pública de inserção
    # ===============================
    def insert(self, key, data=None):
        """Insere um novo nó na árvore."""
        self.root = self._insert(self.root, key, data)

    # Função recursiva interna
    def _insert(self, node, key, data):
        # Inserção padrão de árvore binária
        if not node:
            print(f"[AVL] Inserindo item '{key}' no inventário.")
            return Node(key, data)

        if key < node.key:
            node.left = self._insert(node.left, key, data)
        elif key > node.key:
            node.right = self._insert(node.right, key, data)
        else:
            # Atualiza o dado se o item já existir
            print(f"[AVL] Item '{key}' já existe. Atualizando dados.")
            node.data = data
            return node

        # Atualiza altura
        node.height = 1 + max(self._get_height(node.left),
                              self._get_height(node.right))

        # Verifica balanceamento
        balance = self._get_balance(node)

        # Casos de desbalanceamento
        # 1. Esquerda-Esquerda
        if balance > 1 and key < node.left.key:
            return self._rotate_right(node)
        # 2. Direita-Direita
        if balance < -1 and key > node.right.key:
            return self._rotate_left(node)
        # 3. Esquerda-Direita
        if balance > 1 and key > node.left.key:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        # 4. Direita-Esquerda
        if balance < -1 and key < node.right.key:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    # ===============================
    # Função pública de remoção
    # ===============================
    def remove(self, key):
        """Remove um item da árvore."""
        self.root = self._remove(self.root, key)

    def _remove(self, node, key):
        if not node:
            print(f"[AVL] Item '{key}' não encontrado para remoção.")
            return node

        # Busca o nó a remover
        if key < node.key:
            node.left = self._remove(node.left, key)
        elif key > node.key:
            node.right = self._remove(node.right, key)
        else:
            print(f"[AVL] Removendo item '{key}' do inventário.")
            # Caso com 0 ou 1 filho
            if not node.left:
                return node.right
            elif not node.right:
                return node.left

            # Caso com 2 filhos → pega o menor da subárvore direita
            temp = self._get_min_value_node(node.right)
            node.key = temp.key
            node.data = temp.data
            node.right = self._remove(node.right, temp.key)

        # Atualiza altura e rebalanceia
        if not node:
            return node

        node.height = 1 + max(self._get_height(node.left),
                              self._get_height(node.right))

        balance = self._get_balance(node)

        # Casos de rebalanceamento
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._rotate_right(node)
        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._rotate_left(node)
        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    # ===============================
    # Busca
    # ===============================
    def search(self, key):
        """Retorna o nó com a chave especificada."""
        return self._search(self.root, key)

    def _search(self, node, key):
        if not node or node.key == key:
            return node
        if key < node.key:
            return self._search(node.left, key)
        return self._search(node.right, key)

    # ===============================
    # Travessia (Em-Order)
    # ===============================
    def inorder(self):
        """Exibe os itens em ordem alfabética."""
        print("\n[Inventário AVL] Itens armazenados:")
        self._inorder(self.root)
        print()

    def _inorder(self, node):
        if node:
            self._inorder(node.left)
            print(f" - {node.key}: {node.data}")
            self._inorder(node.right)

    # ===============================
    # Funções auxiliares internas
    # ===============================
    def _get_height(self, node):
        return node.height if node else 0

    def _get_balance(self, node):
        return self._get_height(node.left) - self._get_height(node.right) if node else 0

    def _get_min_value_node(self, node):
        current = node
        while current.left:
            current = current.left
        return current

    # ===============================
    # Rotações
    # ===============================
    def _rotate_left(self, x):
        y = x.right
        T2 = y.left

        y.left = x
        x.right = T2

        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))

        return y

    def _rotate_right(self, y):
        x = y.left
        T2 = x.right

        x.right = y
        y.left = T2

        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))

        return x
