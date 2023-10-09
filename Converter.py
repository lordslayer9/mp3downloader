import os
import threading
from tkinter import messagebox
from mutagen.mp3 import MP3
import shutil
import Main


################################################################################################################################
##################################################### Código do Converter ######################################################
################################################################################################################################

# Função para converter um arquivo MP3 para 128kbps, apenas se o bitrate for maior que 128kbps
def convert_mp3(input_file):
    # Cria o nome do arquivo temporário que substituirá o original depois da conversão usando biblioteca shutil
    temp_output_file = input_file.replace('.mp3', '_temp.mp3')
    
    # Biblioteca mp3 do mutagen para saber se o arquivo ja está em 128kbps
    audio = MP3(input_file)
    current_bitrate = audio.info.bitrate
    if current_bitrate <= 135000:
        print(f"Arquivo já está em 128kbps ou menos: {input_file}")
        return

    # Faz a conversão usando ffmpeg
    os.system(f'ffmpeg -i "{input_file}" -b:a 128k "{temp_output_file}"')
    
    # Verifica se a conversão foi bem-sucedida antes de substituir o arquivo original
    if os.path.exists(temp_output_file):
        # Substitui o arquivo temporário pelo original
        shutil.move(temp_output_file, input_file)
        print(f"Arquivo convertido e substituído: {input_file}")
    else:
        print(f"Erro na conversão: {input_file}")

# Função para processar a lista de arquivos
def process_files(file_list):
    for file in file_list:
        convert_mp3(file)

# Função que busca pelos mp3 em todas subpastas e panha na lista
def get_mp3_files(root_dir):
    mp3_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".mp3"):
                input_file = os.path.join(root, file)
                mp3_files.append(input_file)
    return mp3_files

def converter_button_click(diretorio):

    convert_root_directory = str(diretorio)
    mp3_files = get_mp3_files(convert_root_directory)  #Chama a função de pegar os arquivos no diretorio definido
    
    # Pra deixar mais rápido a conversão, ao invez de fazer 1 por uma, cria as threads e divide os arquivos para cada thread
    num_threads = 6  
    files_per_thread = len(mp3_files) // num_threads
    
    # Crie uma lista de threads para processar os arquivos em paralelo
    threads = []
    
    #Esse eu nao manjei, mas imagino que deve ser pros threads não converterem o mesmo arquivo
    for i in range(num_threads):
        start = i * files_per_thread
        end = (i + 1) * files_per_thread if i < num_threads - 1 else None
        thread_files = mp3_files[start:end]
        thread = threading.Thread(target=process_files, args=(thread_files,))
        thread.start()
        threads.append(thread)

    # Aguarde todas as threads terminarem
    for thread in threads:
        thread.join()
    messagebox.showinfo('Concluído', 'Arquivos convertidos.')
