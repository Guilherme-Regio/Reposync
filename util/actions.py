from .getfiles import *
from tarfile import open, ReadError, CompressionError
from hashlib import md5
from threading import Event, Thread
from subprocess import Popen, PIPE
from requests import head
from os import system
    

class Actions:
    def __init__(self):
        self.download_status = {'status': 'not_started'}
        self.localreposedel = []
        self.webreposadd = []
        self.compare_repos = []


    def compare_lists(self, web_list, local_list):
        web_set = set(web_list)
        local_set = set(local_list)

        self.localreposdel = list(local_set - web_set)
        self.webreposadd = list(web_set - local_set)
        self.compare_repos = list(local_set & web_set)

        return self.localreposdel, self.webreposadd, self.compare_repos


    def extract_repo(self, tar_gz_file, target_dir):
        try:
            with open(tar_gz_file, 'r:gz') as tar:
                tar.extractall(path=target_dir)
            return True
        except ReadError:
            return False
        except CompressionError:
            return False
        except Exception as e:
            return False


    def get_remote_file_size(self, url):
        """Obtém o tamanho do arquivo remoto."""
        response = head(url)
        content_length = response.headers.get('content-length', 0)
        return int(content_length)


    def download_repo(self, url, local_filename, stop_event):
        
        # 1 - Erro de download
        # 2 - Download concluído com sucesso
        # 4 - Download pausado 

        local_file_size = path.getsize(local_filename) if path.exists(local_filename) else 0
        remote_file_size = self.get_remote_file_size(url)

        if local_file_size == remote_file_size:
            print(f"Arquivo '{local_filename}' já está baixado e completo.")
            self.download_status['status'] = 'completed'
            return 2

        try:
            resume_header = {'Range': f'bytes={local_file_size}-'} if local_file_size else {}
            with get(url, headers=resume_header, stream=True, timeout=60) as response:
                response.raise_for_status()
                total_size = remote_file_size
                downloaded_size = local_file_size
                
                with open(local_filename, "ab") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if stop_event.is_set():
                            self.download_status['status'] = 'paused'
                            return 4
                        
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        progress = (downloaded_size / total_size) * 100
                        print(f"Download progress: {progress:.2f}%", end='\r')

            self.download_status['status'] = 'completed'
            return 2
        
        except Exception as e:
            print(f"\nErro durante o download: {e}")
            self.download_status['status'] = 'error'
            return 1
        

    def start_download(self, url, local_filename):

        # 1 - Erro de download
        # 2 - Download concluído com sucesso
        # 4 - Download pausado

        stop_event = Event()
        self.download_status = {'status': 'not_started'}
        download_thread = Thread(target=self.download_repo, args=(url, local_filename, stop_event))

        download_thread.start()
        download_thread.join(timeout=1)

        if download_thread.is_alive():
            stop_event.set()
            download_thread.join()

        if self.download_status['status'] == 'completed':
            print("Processo de Download Finalizado com sucesso!!!.")
            return 2
        elif self.download_status['status'] == 'paused':
            print("Download pausado. Aguarde a próxima janela para finalização...")
            return 4
        else:
            print("Erro no download. Verifique o arquivo de log para detalhes.")
            return 1


    def get_file_md5(self, fulpathfile):
        md5_hash = md5()
        try:
            with open(fulpathfile, "rb") as f:
                chunk = f.read(8192)
                while chunk:
                    md5_hash.update(chunk)
                    chunk = f.read(8192)
        except (OSError, IOError) as e:
            print(f"Error opening/reading file: {e}")
            return None

        return md5_hash.hexdigest()


    def get_dir_md5(self, fullpathdir):
        find_command = f"find {fullpathdir} -type f -print0 | sort -z | xargs -0 cat"
        md5_command = "md5sum"

        find_proc = Popen(find_command, shell=True, stdout=PIPE)
        md5_proc = Popen(md5_command, shell=True, stdin=find_proc.stdout, stdout=PIPE)
        find_proc.stdout.close() 

        md5_output, _ = md5_proc.communicate()
        md5_hash = md5_output.decode().split()[0]

        return md5_hash
    

    def clear_screen(self):
        system('clear')
