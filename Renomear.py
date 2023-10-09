from mutagen.id3 import ID3
import os
import shutil
from collections import defaultdict
from tkinter import messagebox
import re

################################################################################################################################
##################################################### Código do organizar ######################################################
################################################################################################################################

def remove_invalid_chars(filename):
    # Remove caracteres não permitidos (exceto espaços e sublinhados)
    cleaned_filename = re.sub(r'[^\w\s_]', '', filename)
    
    # Substituir múltiplos espaços por um único espaço
    cleaned_filename = re.sub(r'\s+', ' ', cleaned_filename)
    
    # Remover espaços em branco no início e no final do nome do arquivo
    cleaned_filename = cleaned_filename.strip()
    
    return cleaned_filename


#Formata o numero da faixa
def format_track_number(track_number):
    # Converte o número de faixa para uma string
    track_str = str(track_number)
    
    # Verifica se tem 2 ou mais digitos e o primeiro dígito é zero e o segundo não
    if len(track_str) >= 2 and track_str[0] == '0' and track_str[1] != '0':
        return track_str[:2]  # Mantém os dois primeiros dígitos
    
    # Verifica se possui apenas 1 dígito e não é zero
    elif len(track_str) == 1 and track_str != '0':
        return '0' + track_str  # Acrescenta um zero à esquerda

    #Verifica se possui 3 digitos e se o primeiro nao é zero
    elif len(track_str) == 3 and track_str[0] != '0':
        return '0' + track_str[:1]  # Acrescenta um zero à esquerda
    
    # Verifica se possui 3 ou mais dígitos e o primeiro é zero
    elif len(track_str) >= 3 and track_str[0] == '0' and track_str[1] !='0':
        return track_str[:2]  # Retorna primeiro e segundo digitos
    
        # Verifica se possui 3 ou mais dígitos e o primeiro e segundo é zero
    elif len(track_str) >= 3 and track_str[0] == '0' and track_str[1] == '0':
        return track_str[1:3]  # Retorna segundo e terceiro digitos

    # Caso contrário, retorna o número de faixa sem alterações
    return track_str[:2]


def organize_mp3_files(directory):
    # Cria um dicionário para mapear álbuns para listas de arquivos MP3
    album_tracks = defaultdict(list)

    for filename in os.listdir(directory):
        if filename.endswith('.mp3'):
            filepath = os.path.join(directory, filename)
            tags = ID3(filepath)
            track_number = tags.get('TRCK', [""])[0]
            song_name = tags.get('TIT2', [""])[0]
            artist_name = tags.get('TPE2', [""])[0]
            album_name = tags.get('TALB', [""])[0]
            
            #Verifica se não tiver TPE2 usar o TPE1
            if not artist_name:
                artist_name = tags.get('TPE1', [""])[0]
            
            # Verifique se o nome da faixa e album está presente nos metadados
            if not song_name and not album_name:
                continue  # Pule o arquivo se o nome da faixa e album estiver ausente
            
            # Remove caracteres inválidos dos nomes das músicas, dos artistas e dos álbuns
            track_number = remove_invalid_chars(track_number)
            song_name = remove_invalid_chars(song_name)
            artist_name = remove_invalid_chars(artist_name)
            album_name = remove_invalid_chars(album_name)
            
            # Formata o número da faixa
            track_number = format_track_number(track_number)
                    
            # Adiciona o arquivo MP3 à lista do álbum correspondente
            album_tracks[(artist_name, album_name)].append((filepath, track_number, song_name, artist_name))


    # Cria pastas para cada álbum e move os arquivos MP3 correspondentes
    for (artist_name, album_name), tracks in album_tracks.items():
        album_folder = f"{artist_name} - {album_name} - {len(tracks)} Faixas"
        album_path = os.path.join(directory, album_folder)
        
        # Cria a pasta se ela não existir
        if not os.path.exists(album_path):
            os.makedirs(album_path)
        
        for filepath, track_number, song_name, artist_name in tracks:
            new_filepath = os.path.join(album_path, f"{track_number} - {song_name} - {artist_name}.mp3")
            shutil.move(filepath, new_filepath)

    return album_tracks  # Retorna o dicionário com informações sobre as faixas organizadas

def organize_button_click (diretorio):

    root = str(diretorio)

    # Abre uma caixa de diálogo para selecionar o diretório
    selected_directory = str(diretorio)

    # Verifica se o usuário selecionou um diretório
    if selected_directory:
        # Chama a função para organizar os arquivos MP3 no diretório selecionado
        album_tracks = organize_mp3_files(selected_directory)
        num_songs = sum(len(files) for _, files in album_tracks.items())
        num_folders = len(album_tracks)
        messagebox.showinfo("Concluido", f"{num_songs} músicas foram organizadas em {num_folders} pastas. Pressione Enter para sair.")
    else:
        messagebox.showerror("ERRO, Nenhum diretório selecionado. O processo foi cancelado.")