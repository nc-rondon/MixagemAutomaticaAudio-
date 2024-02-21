import pyaudio
import numpy as np

# Parâmetros do Stream
CHUNK = 1024 * 3  # Tamanho do buffer de áudio
FORMAT = pyaudio.paInt16  # Formato de dados do áudio
CHANNELS = 1  # Número de canais (mono)
RATE = 100000  # Frequência de amostragem

# Limites de intensidade
INTENSIDADE_MIN = -500  # Limite inferior (volume baixo)
INTENSIDADE_MAX = 30000  # Limite superior (volume alto)

# Fator de Ganho
GANHO_AJUSTE = 10000  # Ajusta a sensibilidade do ajuste automático

# Cria objeto PyAudio e Stream
p = pyaudio.PyAudio()
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK,
)

def ajustar_intensidade(data):
    """
    Ajusta a intensidade do áudio em tempo real.

    Args:
        data: bytes - Dados de áudio brutos do microfone.

    Returns:
        bytes - Dados de áudio ajustados para o stream de saída.
    """
    # Converte dados binários em array NumPy
    data_np = np.frombuffer(data, dtype=np.int16)

    # Calcula a intensidade média do buffer
    intensidade_media = np.mean(np.abs(data_np))

    # Ajusta o ganho de acordo com a intensidade média
    if intensidade_media < INTENSIDADE_MIN:
        ganho = GANHO_AJUSTE * (INTENSIDADE_MIN - intensidade_media)
    elif intensidade_media > INTENSIDADE_MAX:
        ganho = -GANHO_AJUSTE * (intensidade_media - INTENSIDADE_MAX)
    else:
        ganho = 0

    # Aplica o ganho ao buffer de áudio
    data_ajustada = data_np * (1 + ganho)

    # Converte o array NumPy de volta para bytes
    data_out = data_ajustada.astype(np.int16).tobytes()

    return data_out

try:
    while True:
        # Lê dados do microfone
        data = stream.read(CHUNK)

        # Ajusta a intensidade do áudio em tempo real
        data_ajustada = ajustar_intensidade(data)

        # Escreve os dados ajustados na saída
        stream.write(data_ajustada)

except KeyboardInterrupt:
    print("Interrompido pelo usuário...")

# Fecha o Stream e termina o PyAudio
stream.stop_stream()
stream.close()
p.terminate()

print("Processo finalizado.")