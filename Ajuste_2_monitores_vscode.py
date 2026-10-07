import pygetwindow as gw
from screeninfo import get_monitors
import time
import ctypes
from ctypes import wintypes

def obter_altura_util_windows():
    """
    Usa a API do Windows para pegar a área útil da tela, 
    descontando a barra de tarefas.
    """
    user32 = ctypes.windll.user32
    rect = wintypes.RECT()
    # 0x0030 é o código (SPI_GETWORKAREA) que diz ao Windows para retornar a área útil
    user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)
    
    return rect.bottom - rect.top

def expandir_vscode():
    print("Buscando informações dos monitores e da área útil do Windows...")
    monitores = get_monitors()
    
    # Ordena os monitores pela posição X (horizontal) da esquerda para a direita
    monitores.sort(key=lambda m: m.x)
    
    largura_total = sum(m.width for m in monitores)
    altura_maxima = obter_altura_util_windows()
    
    # --- COMPENSAÇÃO DA SOMBRA DO WINDOWS (OFFSET) ---
    # O Windows possui uma borda invisível de aproximadamente 7 pixels.
    offset_borda = 8 
    
    # Subtraímos o offset do X inicial para "empurrar" a borda esquerda para fora da tela
    x_inicial = monitores[0].x - offset_borda
    
    # O topo (Y) não possui a mesma sombra espessa, então mantemos no 0 (ou no Y original)
    y_inicial = monitores[0].y 
    
    # A largura recebe o offset das duas pontas (esquerda e direita)
    largura_ajustada = largura_total + (offset_borda * 2)
    
    # A altura recebe o offset da parte de baixo (onde encosta na barra de tarefas)
    altura_ajustada = altura_maxima + offset_borda
    
    print(f"-> Área de alocação calculada (com offset): {largura_ajustada}x{altura_ajustada}")
    print("Buscando a janela do VS Code...")
    
    janelas_vscode = gw.getWindowsWithTitle('Visual Studio Code')
    
    if not janelas_vscode:
        print("-> VS Code não encontrado. Certifique-se de que ele está aberto.")
        return

    janela = janelas_vscode[0]
    
    if janela.isMaximized:
        janela.restore()
        time.sleep(0.5) 
        
    print("Redimensionando e movendo a janela...")
    janela.moveTo(x_inicial, y_inicial)
    janela.resizeTo(largura_ajustada, altura_ajustada)
    
    print("-> Concluído! O VS Code agora está perfeitamente alinhado, sem bordas vazadas.")

if __name__ == "__main__":
    expandir_vscode()