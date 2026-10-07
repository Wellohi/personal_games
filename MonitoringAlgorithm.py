import psutil
import time
import os
from collections import deque
from datetime import datetime
import asyncio
import random
import sys
import os

# Cores ANSI
B = "\033[94m"          # Blue
C = "\033[96m"          # Cyan
G = "\033[92m"          # Green
M = "\033[95m"          # Magenta
O = "\033[38;5;208m"    # Laranja
R = "\033[91m"          # Red
Y = "\033[93m"          # Yellow
W = "\033[97m"          # White

# --------------------------------------------------------------
# # Tons básicos adicionais
# K  = "\033[90m"   # Bright Black (Cinza escuro)
# W  = "\033[97m"   # Bright White (Branco intenso)

# # Cores de fundo
# BG_R = "\033[41m"  # Fundo Vermelho
# BG_G = "\033[42m"  # Fundo Verde
# BG_Y = "\033[43m"  # Fundo Amarelo
# BG_B = "\033[44m"  # Fundo Azul
# BG_M = "\033[45m"  # Fundo Magenta
# BG_C = "\033[46m"  # Fundo Ciano
# BG_W = "\033[47m"  # Fundo Branco

# ORANGE = "\033[38;5;208m"  # Laranja
# PINK   = "\033[38;5;213m"  # Rosa
# PURPLE = "\033[38;5;141m"  # Roxo claro
# GOLD   = "\033[38;5;220m"  # Dourado
# LIME   = "\033[38;5;118m"  # Verde limão
# TEAL   = "\033[38;5;37m"   # Verde-azulado
# NAVY   = "\033[38;5;18m"   # Azul marinho
# BROWN  = "\033[38;5;94m"   # Marrom
# CORAL  = "\033[38;5;209m"  # Coral
# SILVER = "\033[38;5;250m"  # Prata
# --------------------------------------------------------------

def monitor_sistema():
    # Inicializa o deque com limite máximo de 50 itens
    historico = deque(maxlen=50)

    print(f"Iniciando monitoramento... Coletando dados iniciais.{M}")
    
    # Captura os contadores de rede iniciais para base de cálculo 
    last_net_io = psutil.net_io_counters()
    last_time = time.time()

    try:
        while True:
            # Pausa exatamente 1 segundo antes da próxima coleta
            time.sleep(1)

            current_time = time.time()
            time_delta = current_time - last_time

            # Coleta as métricas estáticas (CPU, Memória, Disco)
            timestamp = datetime.now().strftime("%H:%M:%S")
            cpu_usage = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/') # Monitora a partição principal

            # Calcula a velocidade de rede (Upload/Download em KB/s)
            current_net_io = psutil.net_io_counters()
            upload_speed = (current_net_io.bytes_sent - last_net_io.bytes_sent) / time_delta / 1024
            download_speed = (current_net_io.bytes_recv - last_net_io.bytes_recv) / time_delta / 1024

            # Atualiza os contadores para o próximo ciclo
            last_net_io = current_net_io
            last_time = current_time

            # Salva o registro atual no histórico
            historico.append({
                "hora": timestamp,
                "cpu": cpu_usage,
                "mem": memory.percent,
                "disk": disk.percent,
                "up": upload_speed,
                "down": download_speed
            })

            # Limpa o terminal (Compatível com Windows 'nt' ou Linux/Mac 'clear')
            os.system('cls' if os.name == 'nt' else 'clear')

            # Imprime o cabeçalho formatado
            print(f"{B}{'Hora':<10} | {R} {'CPU (%)':<8}| {G}{'Memória (%)':<12} | {Y}{'Disco (%)':<10} | {W}{'Up (KB/s)':<12} | {O}{'Down (KB/s)':<12}")
            print("-" * 75)

            # Itera sobre o histórico imprimindo os dados formatados
            for registro in historico:
                print(f"{B}{registro['hora']:<10} | {R} {registro['cpu']:<8.1f} | {G}{registro['mem']:<12.1f} | {Y}{registro['disk']:<10.1f} | {W}{registro['up']:<12.2f} | {O}{registro['down']:<12.2f}")

    except KeyboardInterrupt:
        print("\nMonitoramento encerrado pelo usuário.")

if __name__ == "__main__":
    monitor_sistema()