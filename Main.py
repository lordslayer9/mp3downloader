from distutils.util import convert_path
import os
import requests
import tkinter as tk
import threading
from tkinter import ttk, filedialog, scrolledtext, messagebox
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from collections import defaultdict
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
import Converter
import Renomear


class MP3DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Downloader MP3')
        self.last_directory = None
        self.save_directory = None
        self.organize_directory = None
        self.convert_directory = None
        self.urls = []
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        ### Salva o diretório da aba Musify
        if os.path.exists("last_directory.txt"):
            with open("last_directory.txt", "r") as file:
                self.last_directory = file.read().strip()
        if self.last_directory:
            self.save_directory = self.last_directory
        ### Salva o diretório da aba Organizar --- NAO ESTA SALVANDO
        if os.path.exists("organize_directory.txt"):  
            with open("organize_directory.txt", "r") as file:
                self.organize_directory = file.read().strip()
        if self.organize_directory:
            self.save_organize_directory = self.organize_directory
        ###Salva o diretório da aba converter  --- NÃO ESTA SALVANDO
        if os.path.exists("convert_directory.txt"):  
            with open("convert_directory.txt", "r") as file:
                self.convert_directory = file.read().strip()
        if self.convert_directory:
            self.save_convert_directory = self.convert_directory

        # Aba Musify
        self.musify_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.musify_tab, text='Musify')

        # Aba Organizar
        self.organize_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.organize_tab, text='Organizar')

        # Campo de entrada para o diretório de organização
        self.organize_directory_frame = ttk.Frame(self.organize_tab)
        self.organize_directory_frame.pack()
        self.organize_directory_entry = ttk.Entry(self.organize_directory_frame, width=40)
        self.organize_directory_entry.pack(side=tk.LEFT)

        ### BOTÃO PARA CHAMAR FUNÇÃO ORGANIZAR        / RENOMEAR
        self.organize_button = tk.Label(self.organize_tab, text='Organizar', bg='lightgray', padx=25, pady=15, cursor='hand2', font='Arial, 12')
        self.organize_button.pack(side=tk.BOTTOM, padx=45, pady=15)
        self.organize_button.bind('<Button-1>', lambda e: Renomear.organize_button_click(self.organize_directory))

        # Botão para procurar o diretório de organização (reutilizando a função browse_directory_organize)
        self.organize_browse_button = ttk.Button(self.organize_directory_frame, text='Procurar', command=self.browse_directory_organize)
        self.organize_browse_button.pack(side=tk.RIGHT)
        if self.organize_directory:
            self.organize_directory_entry.insert("0", self.organize_directory)

        # Aba Converter
        self.converter_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.converter_tab, text='Converter')

        ### BOTÃO PARA CHAMAR FUNÇÃO CONVERTER        
        self.converter_button = tk.Label(self.converter_tab, text='Converter', bg='lightgray', padx=25, pady=15, cursor='hand2', font='Arial, 12')
        self.converter_button.pack(side=tk.BOTTOM, padx=45, pady=15)
        self.converter_button.bind('<Button-1>', lambda e: Converter.converter_button_click(self.convert_directory))

        # Campo de entrada para o diretório de conversão
        self.convert_directory_frame = ttk.Frame(self.converter_tab)
        self.convert_directory_frame.pack()

        self.convert_directory_entry = ttk.Entry(self.convert_directory_frame, width=40)
        self.convert_directory_entry.pack(side=tk.LEFT)

        # Botão para procurar o diretório de conversão (reutilizando a função browse_directory_convert)
        self.convert_browse_button = ttk.Button(self.convert_directory_frame, text='Procurar', command=self.browse_directory_convert)
        self.convert_browse_button.pack(side=tk.RIGHT)

        if self.convert_directory:
            self.convert_directory_entry.insert("0", self.convert_directory)

        # Caixa de texto para inserir os links (Musify)
        self.link_entry = scrolledtext.ScrolledText(self.musify_tab, width=40, height=10)
        self.link_entry.pack(pady=10)

        # Crie um Frame para agrupar o campo de entrada e o botão "Procurar"
        self.directory_frame = ttk.Frame(self.musify_tab)
        self.directory_frame.pack()

        # Campo de entrada para o diretório de salvamento
        self.directory_entry = ttk.Entry(self.directory_frame, width=40)
        self.directory_entry.pack(side=tk.LEFT)

        # Botão para procurar o diretório de salvamento
        self.browse_button = ttk.Button(self.directory_frame, text='Procurar', command=self.browse_directory)
        self.browse_button.pack(side=tk.RIGHT)

        if self.save_directory:
            self.directory_entry.insert("0", self.save_directory)

        # Rótulo acima da barra de progresso
        self.progress_label = ttk.Label(self.musify_tab, text='')
        self.progress_label.pack()

        # Barra de progresso
        self.progress_bar = ttk.Progressbar(self.musify_tab, length=300, mode='determinate')
        self.progress_bar.pack(pady=10)

        # Etiqueta à direita da barra de progresso
        self.progress_info = ttk.Label(self.musify_tab, text='')
        self.progress_info.pack()

        # Botões para baixar e limpar
        fonte = ('Courier', 10, 'bold')
        self.clear_button = tk.Label(self.musify_tab, text='Limpar', bg='lightgray', padx=25, pady=15, cursor='hand2', font=fonte)
        self.clear_button.pack(side=tk.LEFT, padx=45, pady=15)
        self.clear_button.bind('<Button-1>', lambda e: self.clear())

        self.download_button = tk.Label(self.musify_tab, text='Baixar', bg='lightgray', padx=25, pady=15, cursor='hand2', font=fonte)
        self.download_button.pack(side=tk.RIGHT, padx=45, pady=15)
        self.download_button.bind('<Button-1>', lambda e: self.start_download())

    #Buscar diretório Organizar
    def browse_directory_organize(self):
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            self.organize_directory = selected_directory
            self.organize_directory_entry.delete(0, tk.END)
            self.organize_directory_entry.insert(0, selected_directory)
            self.save_organize_directory(selected_directory)

    #Procurar diretório Convert
    def browse_directory_convert(self):
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            self.convert_directory = selected_directory
            self.convert_directory_entry.delete(0, tk.END)
            self.convert_directory_entry.insert(0, selected_directory)
            self.save_converter_directory(selected_directory)

    def button_click_convert(self):
        if self.convert_directory == None:
            print = 'Nenhum diretório Selecionado'
            return
        
    #Procurar diretório Musify
    def browse_directory(self):
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            self.directory_entry.delete(0, tk.END)
            self.directory_entry.insert(0, selected_directory)
            self.save_directory = selected_directory
            self.save_last_directory(selected_directory)

    def save_last_directory(self, directory):
        with open("last_directory.txt", "w") as file:
            file.write(directory)

    def save_organize_directory(self, directory):
        with open("organize_directory.txt", "w") as file:  # Novo: Salvar diretório para a aba Organizar
            file.write(directory)
    
    def save_converter_directory(self, directory):
        with open("convert_directory.txt", "w") as file:  # Novo: Salvar diretório para a aba Converter
            file.write(directory)

    def update_progress(self):
        self.progress_bar["value"] = self.current_song
        self.progress_info.config(text=f'{self.current_song}/{self.total_num_mp3} ({self.current_song})')
        if self.current_song < self.total_num_mp3:
            self.root.after(100, self.update_progress)
        else:
            self.progress_label.config(text='Downloads concluídos!')

    def download_song(self, mp3_url, mp3_name):
        try:
            mp3_response = requests.get(mp3_url, stream=True)
            mp3_response.raise_for_status()

            mp3_path = os.path.join(self.save_directory, mp3_name)

            with open(mp3_path, 'wb') as mp3_file:
                for chunk in mp3_response.iter_content(chunk_size=8192):
                    if chunk:
                        mp3_file.write(chunk)

            self.current_song += 1
        except requests.exceptions.RequestException as e:
            print(f"Erro ao baixar {mp3_name}: {e}")

    def download(self):
        self.current_song = 0
        mp3_links = []

        for url in self.urls:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a')

                mp3_links += [urljoin(url, link.get('href')) for link in links if link.get('href') and link.get('href').endswith('.mp3')]

        self.total_num_mp3 = len(mp3_links)

        if self.total_num_mp3 == 0:
            messagebox.showinfo('Sem Arquivos MP3', 'Nenhum arquivo MP3 encontrado nos sites fornecidos.')
            return

        self.progress_label.config(text='Baixando...')
        self.progress_bar["maximum"] = self.total_num_mp3
        self.progress_bar["value"] = 0
        self.update_progress()

        with ThreadPoolExecutor(max_workers=5) as executor:
            for mp3_url in mp3_links:
                mp3_name = os.path.basename(mp3_url)
                executor.submit(self.download_song, mp3_url, mp3_name)

    def start_download(self):
        if not self.save_directory:
            messagebox.showerror('Erro', 'Escolha um diretório de salvamento.')
            return

        self.urls = self.link_entry.get("1.0", "end-1c").split('\n')
        self.urls = [url.strip() for url in self.urls if url.strip()]

        if not self.urls:
            messagebox.showerror('Erro', 'Nenhum link inserido.')
            return

        download_thread = threading.Thread(target=self.download)
        download_thread.start()

    def clear(self):
        self.link_entry.delete("1.0", tk.END)

def main():
    root = tk.Tk()
    app = MP3DownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
