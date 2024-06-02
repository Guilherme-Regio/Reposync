from sys import argv, exit as exit_sys
from socket import gethostname, gethostbyname
from util.getdata import GetData
from util.postdata import PostData
from util.reposync import Reposync

VERSION = "" # VERSION

class ExecuteReposync:
    def __init__(self, mode):
        self.ip = gethostbyname(gethostname())
        self.reposync_interval = False
        self.mode = mode
        self.data = []


    def manager_service(self):
        self.getdata = GetData(self.ip)
        self.reposync_interval = self.getdata.get_reposync_interval()


    def manager_reposync(self):
        if self.reposync_interval: 
            reposync = Reposync(self.reposync_interval * 60)
            self.data = reposync.return_data()


    def manager_data(self):
        self.postdata = PostData(self.ip, self.data)


    def execute(self):
        if self.mode == 1:
            self.manager_service()
        elif self.mode == 2:
            self.manager_service()
            self.manager_reposync()
            self.manager_data()
        else:
            return False


if __name__ == "__main__":
    if len(argv) > 1 and argv[1] == "--version":
        print(f"Versão do script: {VERSION}")
        exit_sys()
        
    if len(argv) > 1:
        try:
            mode = int(argv[1])
            executor = ExecuteReposync(mode)
            executor.execute()
        except ValueError:
            False
    else:
        False
