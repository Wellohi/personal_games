from datetime import datetime
import asyncio
import random
import sys
import os
from collections import deque

# Cores ANSI
G = "\033[92m"  # Green
R = "\033[91m"  # Red
B = "\033[94m"  # Blue
Y = "\033[93m"  # Yellow
C = "\033[96m"  # Cyan
M = "\033[95m"  # Magenta
O = "\033[90m"  # Orange
RESET = "\033[0m"

# --- BANCO DE DADOS DE SIMULAÇÃO ---
PRODUTOS = [
    "CONSÓRCIO", "CRÉDITO", "RENDA", "VIGÊNCIA", "PREVIDÊNCIA", "VISTORIA", "CONTEMPLAÇÃO", "CRÉDITO RURAL", "FINANCIAMENTO",
    "SEGUROS", "", "", "", "", "", "", "", "", "", "", "", ""
]

PROCESSES = [
    f"PROCESSING {B}'IMOVISL'{RESET}",
    f"PROCESSING {Y}'VEICULOS'{RESET}",
    f"PROCESSING {R}'CONTEMPLADOS'{RESET}",
    f"PROCESSING {C}'POS-CONTEMPLADOS'{RESET}",
    f"PROCESSING {B}'INADIMPLENTES'{RESET}",
    f"PROCESSING {C}'DOCUMENTACOES PENDENTES'{RESET}",
    f"PROCESSING {Y}'SUPERAVITARIOS'{RESET}",
    f"PROCESSING {C}'DEFICITARIOS'{RESET}",
    f"PROCESSING {C}'NEUTROS'{RESET}",
    f"PROCESSING {R}'FISCALIZACOES'{RESET}",
    f"PROCESSING {Y}'NEGADOS'{RESET}",
    f"PROCESSING {G}'APROVADOS'{RESET}",
    f"PROCESSING {Y}'RESSARCIMENTOS'{RESET}",
    f"PROCESSING {C}'PAGAMENTOS'{RESET}",
    f"PROCESSING {B}'BENEFICIARIO'{RESET}",
    f"PROCESSING {G}'DOACOES'{RESET}",
    f"PROCESSING {C}'CONSORCIADOS'{RESET}",
    f"PROCESSING {M}'COOPERATIVAS'{RESET}",
    f"PROCESSING {M}'CREDITOS'{RESET}",
    f"PROCESSING {R}'COLABORADORES'{RESET}",
    f"PROCESSING {B}'PENDENCIAS'{RESET}",
    f"PROCESSING {R}'RESOLUCOES'{RESET}",
]

STATUS = [
    (f"{G}DONE{RESET}", 0.5),
    (f"{B}PROC{RESET}", 0.3),
    (f"{Y}WARN{RESET}", 0.1),
    (f"{R}FAIL{RESET}", 0.05),
    (f"{M}SYNC{RESET}", 0.05),
    (f"{G}NOT FOUND{RESET}", 0.5),
    (f"{B}SEARCHING...{RESET}", 0.3),
    (f"{Y}WARNING{RESET}", 0.1),
    (f"{R}DEFAULT{RESET}", 0.05),
    (f"{M}NOT SINCRONIZED{RESET}", 0.05)
]

# Buffer que mantém EXATAMENTE as últimas 100 linhas
terminal_buffer = deque(maxlen=100)
# Lock para evitar que múltiplas tarefas limpem a tela ao mesmo tempo
render_lock = asyncio.Lock()

def clear_terminal():
    """Limpa o terminal de forma eficiente conforme o SO."""
    os.system('cls' if os.name == 'nt' else 'clear')

async def simulate_data_pipeline(worker_id):
    """Simula o pipeline de Data Science rodando no terminal com controle de buffer."""
    while True:
        proc = random.choice(PROCESSES)
        status_text, _ = random.choices([s[0] for s in STATUS], weights=[s[1] for s in STATUS])[0], None
        
        rows = random.randint(1000, 89520)
        loc = random.choice(PRODUTOS)
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        mem_usage = f"{random.uniform(1.5, 500):.1f}MB"
        
        log_line = (
            f"[{timestamp}] [{C}{loc:15}{RESET}] "
            f"Rows: {rows} | Mem: {mem_usage:>7} | " 
            f"{proc:50} ... [{status_text}]" 
        )
        
        # Lógica de Atualização do Terminal
        async with render_lock:
            terminal_buffer.append(log_line)
            clear_terminal()
            # Reimprime o cabeçalho e o conteúdo do buffer
            print(f"{G}=== MONITORING BUFFER (MAX 100 LINES) ==={RESET}")
            print("\n".join(terminal_buffer))
        
        await asyncio.sleep(random.uniform(0.05, 2))

async def main():
    # Cabeçalho de inicialização
    clear_terminal()
    header = f"""
{G}================================================================================
                    CCS - PRODUTOS DE CONSÓRCIO E COBRANÇA 
================================================================================{RESET}
{Y}INITIALIZING PATH:{RESET} {os_path_sim()}
{Y}WORK PLANS ACTIVE:{RESET} 08, 10, 13, 14, 17
{M}BUFFER LIMIT:{RESET} 100 Lines (Memory-Safe Mode)
    """
    print(header)
    await asyncio.sleep(1.5)
    
    tasks = [simulate_data_pipeline(i) for i in range(6)]
    await asyncio.gather(*tasks)

def os_path_sim():
    try: return os.path.join(os.getcwd(), '..', 'data', 'raw')
    except: return "/data/raw/IP013.csv"

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{R}[TERMINATED]{RESET} Cleanup: Memory flushed. Buffer cleared.")
        sys.exit()