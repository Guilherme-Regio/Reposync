from urllib3.exceptions import InsecureRequestWarning
from subprocess import run, CalledProcessError
from warnings import filterwarnings
from fileinput import FileInput
from requests import post

filterwarnings('ignore', category=InsecureRequestWarning)

class GetData:
    def __init__(self, ip):
        self.rotina = []
        self.ip = ip
        self.timer_path = '/etc/systemd/system/reposync.timer'
        self.service_path = '/etc/systemd/system/reposync.service'
        self.api_url = '' # URL API ENDPOINT
        self.timer_info = self.get_timer_info()
        self.execute_updates()


    def get_timer_info(self):
        try:
            with open(self.timer_path, 'r') as file:
                for line in file:
                    if line.startswith('OnCalendar='):
                        return line.strip().split('=')[1]
        except FileNotFoundError:
            return False


    def update_timer_schedule(self, new_time):
        if self.timer_info and new_time:
            with FileInput(self.timer_path, inplace=True) as file:
                for line in file:
                    if line.startswith('OnCalendar='):
                        print(f'OnCalendar={new_time}') 
                    else:
                        print(line, end='')
        else:
            return False


    def get_filial_rotinas(self):
        response = post(self.api_url, verify=False)
        rotinas = response.json().get('Rotinas', [])
        for rotina in rotinas:
            if rotina.get('nome') == 'reposync':
                self.rotina.append(rotina)


    def update_service_file(self, new_argument):
        try:
            with FileInput(self.service_path, inplace=True) as file:
                for line in file:
                    if line.strip().startswith('ExecStart='):
                        line = f'ExecStart=/var/scripts_rd/rotinas/reposync {new_argument}\n'
                    print(line, end='')
        except Exception as e:
            return False


    def apply_systemd_changes(self):
        try:
            run(['systemctl', 'daemon-reload'], check=True)
        except CalledProcessError as e:
            return False

        
    def execute_updates(self):
        self.get_filial_rotinas()
        if self.rotina:
            for rotina in self.rotina:
                novo_horario = rotina.get('horario_execucao')
                if novo_horario:
                    self.update_timer_schedule(novo_horario)
                    self.update_service_file('2')
                    self.apply_systemd_changes()
    

    def get_reposync_interval(self):
        self.get_filial_rotinas()
        for rotina in self.rotina:
            if rotina.get('nome') == 'reposync':
                return rotina.get('intervalo_execucao')
        return None
    