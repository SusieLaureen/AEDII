# ===========================================
# save_load.py — Sistema de salvamento do jogo
# ===========================================
# Responsável por gravar e restaurar o estado do jogo:
# - posição do jogador
# - itens do inventário (AVL)
# Tudo salvo em um arquivo .txt (pasta /data).
# ===========================================

import os
from tree import AVLTree

SAVE_FILE = os.path.join("data", "save.txt")

# ===============================
# Funções principais
# ===============================

def save_game(player):
    """Salva posição, inventário e PASSOS."""
    os.makedirs("data", exist_ok=True)

    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        f.write(f"posicao={player.position}\n")
        f.write(f"passos={player.step_count}\n") 

        items = []
        _collect_items(player.inventory.root, items)
        f.write("inventario=" + ",".join(items) + "\n")

    print(f"\n💾 [SALVAR] Jogo salvo com sucesso!")

def load_game():
    """Carrega o progresso e retorna (posicao, inventario, passos)."""
    if not os.path.exists(SAVE_FILE):
        return None, None, 0

    position = None
    step_count = 0
    inventory_items = []

    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("posicao="):
                position = line.split("=")[1]
            elif line.startswith("passos="): 
                try:
                    step_count = int(line.split("=")[1])
                except:
                    step_count = 0
            elif line.startswith("inventario="):
                val = line.split("=")[1]
                if val:
                    inventory_items = val.split(",")

    inventory = AVLTree()
    for item in inventory_items:
        inventory.insert(item, "Item recuperado.")

    return position, inventory, step_count 

def _collect_items(node, result):
    if not node: return
    _collect_items(node.left, result)
    result.append(node.key)
    _collect_items(node.right, result)
