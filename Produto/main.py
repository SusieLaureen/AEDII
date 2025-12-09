# ===========================================
# main.py — Explorador de Território 2D 
# ===========================================
# Estruturas utilizadas:
#   - Grafo: representação do mapa (labirinto)
#   - Árvore AVL: inventário do jogador
#
# Funcionalidades:
#   - Novo jogo / Carregar / Salvar
#   - Mover-se entre salas conectadas
#   - Coletar itens (AVL)
#   - Ver mapa e inventário
#   - Ver caminho mais curto até o portão (BFS)
# ===========================================
# main.py — Explorador de Território 2D 
# ===========================================

from world import World
from player import Player
from save_load import save_game, load_game
import time
import os

def exibir_comemoração(passos):
    """Exibe uma comemoração visual em ASCII quando o jogador vence."""
    os.system('clear' if os.name == 'posix' else 'cls')  
    
    celebracao = f"""
    
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                                                                          ║
    ║                   🎉🎉🎉 PARABÉNS, EXPLORADOR! 🎉🎉🎉                    ║
    ║                                                                          ║
    ║                   ✨ VOCÊ CONSEGUIU ESCAPAR DO LABIRINTO! ✨            ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    
           ⭐         ⭐         ⭐         ⭐         ⭐
           
        🏆 MISSÃO CUMPRIDA 🏆
        
        ✓ Você encontrou a CHAVE!
        ✓ Desbloqueou o PORTÃO!
        ✓ PASSOS TOTAIS: {passos}
        
           ⭐         ⭐         ⭐         ⭐         ⭐
    
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                   Pressione ENTER para voltar ao menu...               ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """
    
    print(celebracao)
    input()

def menu_principal():
    """Exibe o menu inicial do jogo."""
    print("======================================")
    print("       EXPLORADOR DE TERRITÓRIO 2D    ")
    print("======================================")
    print("1. Novo Jogo")
    print("2. Carregar Jogo")
    print("3. Sair")
    print("======================================")

def main():
    while True:
        menu_principal()
        opc = input("Escolha uma opção: ")

        if opc == "1":
            iniciar_jogo(novo=True)
        elif opc == "2":
            iniciar_jogo(novo=False)
        elif opc == "3":
            print("Saindo do jogo... Até a próxima, explorador!")
            break
        else:
            print("Opção inválida!\n")

def iniciar_jogo(novo=True):
    """Cria o mundo e inicia o loop principal do jogo."""
    world = World()

    if novo:
        player = Player("Jogador", world.start_node)
        print("\n[NOVO JOGO] Um novo explorador entra no labirinto!")
    else:
        pos, inv, steps = load_game()
        
        if not pos:
            print("[ERRO] Nenhum jogo salvo encontrado.")
            return
        player = Player("Jogador", pos)
        player.inventory = inv
        player.step_count = steps # Restaura passos
        print("\n[JOGO CARREGADO] Boa sorte continuando sua jornada!\n")

    print(f"\n📍 Você está na sala: {player.position}")
    print("Objetivo: encontre a CHAVE e use-a no PORTÃO para escapar!\n")

    jogando = True
    while jogando:
        print("======================================")
        print(f"📍 Local atual: {player.position}")
        print(f"👣 Passos: {player.step_count}")
        print("======================================")
        print("1. Mover-se para outra sala")
        print("2. Ver inventário")
        print("3. Ver mapa (debug)")
        print("4. Ver caminho até o portão 🧭")
        print("5. Salvar jogo 💾")
        print("6. Sair do jogo")
        print("======================================")

        escolha = input("Escolha uma opção: ")

        # Mover o jogador
        if escolha == "1":
            vizinhos = world.graph.get_neighbors(player.position)
            if not vizinhos:
                print("[AVISO] Nenhum caminho disponível.")
                continue

            print(f"Salas conectadas: {vizinhos}")
            destino = input("Para qual sala deseja ir? ")

            if destino in vizinhos:
                player.move(destino)
                venceu, msg = world.check_event(player)
                if msg:
                    print(f"\n{msg}\n")
                if venceu:
                    exibir_comemoração(player.step_count)
                    jogando = False
            else:
                print("[ERRO] Caminho inválido!\n")

        # Mostrar inventário
        elif escolha == "2":
            player.show_inventory()

        # Mostrar mapa 
        elif escolha == "3":
            world.show_map()

        # Mostrar caminho até o portão (BFS)
        elif escolha == "4":
            print("\n[🧭] Calculando o caminho mais curto até o portão...\n")
            caminho = world.graph.bfs(player.position, world.exit_node)
            if caminho:
                print("➡️  Caminho sugerido:", " -> ".join(caminho))
            else:
                print("[ERRO] Nenhum caminho encontrado.\n")

        # Salvar jogo
        elif escolha == "5":
            save_game(player)

        # Sair
        elif escolha == "6":
            print("\nEncerrando a exploração... Até a próxima, aventureiro!\n")
            jogando = False

        else:
            print("Opção inválida!\n")

        time.sleep(1)

if __name__ == "__main__":
    main()
