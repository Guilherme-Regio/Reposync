from util.actions import *
from shutil import rmtree
from subprocess import run
from threading import Event, Thread
from os import unlink


class Reposync:
    def __init__(self, reposync_interval):

        # Parameters
        self.actions = Actions()
        self.reposdel = []
        self.reposdown = []
        self.reposcheck = []
        self.results = {}
        self.reposync_interval = reposync_interval

        # Paths
        self.pathrepos = "" # PATH REPO
        self.urllist = "" # URL LIST
        self.urldown = "" # URL DOWNLOAD
        self.urlcheck = "" # URL CHECK

        # Cria a estrutura de diretórios se não existir
        run(["mkdir", "-p", self.pathrepos], check=True)

        self.sync_repos()


    def sync_repos(self):
                        
        self.repo_list_check()

        #Deleta os repositórios obsoletos
        if self.reposdel != []:
            self.repo_del()

        #Checa a versão/integridade dos repositórios em produção e devolve o que estiver diferente
        if self.reposcheck != []:
            repos_update = self.repo_compare()
            if repos_update != []:
                for repo in repos_update:
                    self.reposdown.append(repo)



        #Baixa todos os repositórios que estiverem listados para download (Desatualizado + Novos)
        if self.reposdown != []:
            stop_event = Event()
            download_thread = Thread(target=self.repo_down, args=(stop_event,))
            download_thread.start()
            download_thread.join(timeout=self.reposync_interval)
            if download_thread.is_alive():
                stop_event.set()
                download_thread.join()

        # Enviar o status e pacote para o ENDPOINT


    def repo_list_check(self):

        #Faz a comparação da lista pelo http
        webrepos = filter_weblist(self.urllist)
        localrepos = get_locallist(self.pathrepos)
        self.reposdel, self.reposdown, self.reposcheck = self.actions.compare_lists(webrepos, localrepos)


    def repo_del(self):  
        for repo in self.reposdel:
            # Deletar a pasta do repo
            rmtree(f'{self.pathrepos}/{repo}')

    
    def repo_compare(self):
        repos_update = []
        for repo in self.reposcheck:

            # Coleta MD5 do repositório local
            md5local = self.actions.get_dir_md5(f'{self.pathrepos}/{repo}').strip()

            # Coletar o MD5 do repositório no servidor
            url = f'{self.urlcheck}/{repo}.md5'
            md5server = get_textfromweb(url).strip()

            if md5server != md5local:

                # Deletar a pasta do repo desatualizado
                rmtree(f'{self.pathrepos}/{repo}')

                #Adicionar a lista de download do repo
                repos_update.append(repo)

            else:
                result = {repo: 10}
                self.results = {**self.results, **result}   


        return repos_update

            
    def repo_down(self, stop_event):
        repos_sorted = sorted(self.reposdown)
        for repo in repos_sorted:

            # 0 - Start
            # 1 - Erro de download
            # 2 - Download concluído com sucesso
            # 3 - Erro na extração do pacote
            # 4 - Download pausado
            # 10 - Repo sincronizado
            self.actions.clear_screen()
            
            #Montagem de caminhos
            url = f'{self.urldown}/{repo}.tar.gz'
            save = f'/tmp/{repo}.tar.gz'

            if stop_event.is_set():
                result = {repo: 0}
                self.results = {**self.results, **result}
            else:

                #Download
                down_output = self.actions.download_repo(url, save, stop_event)


                if not stop_event.is_set():
                    if down_output != 1:
                        # Descompactar o repo baixado
                        if not self.actions.extract_repo(save, self.pathrepos):
                            self.results = {repo: 3}
                        else:
                            # Remover o arquivo compactado depois de processar
                            unlink(save)
                            result = {repo: 10}
                            self.results = {**self.results, **result}
                    else:

                        result = {repo: 1}
                        self.results = {**self.results, **result}
                else:
                    result = {repo: 4}
                    self.results = {**self.results, **result}


    def return_data(self):
        return self.results
