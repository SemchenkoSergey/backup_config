# coding: utf-8

import pexpect
import re
import time

DEBUG = False

class H5600():
    TYPE = 'DSLAM'
    ESC = r'\x1b\[37D +\x1b\[37D(\x1b\[1A)?'
    STOP = '---- More \( Press \'Q\' to break \) ----'
    LOGIN = 'root'
    PASSWORD = 'admin'
    
    def __init__(self, ip):
        self.ip = ip
        self.tn = pexpect.spawn('telnet {}'.format(self.ip))
        if DEBUG:
            self.tn.logfile = open('debug {}.txt'.format(self.ip), 'wb')        
        self.tn.expect('>>User name:')
        self.tn.sendline(self.LOGIN)
        self.tn.expect('>>User password:')
        self.tn.sendline(self.PASSWORD)
        self.tn.expect('(>|\) ----)')
        self.tn.sendline(' ')
        self.tn.expect('>')
        self.tn.sendline('enable')
        self.tn.expect('#')
        self.tn.sendline('undo smart')
        self.tn.expect('#')
        self.tn.sendline('undo interactive')
        self.tn.expect('#')
        self.tn.sendline('scroll 512')
        self.tn.expect('#')
        self.tn.sendline('idle-timeout 10')
        self.tn.expect('#')        
        self.hostname = re.search('\n([\w-]+)$', self.tn.before.decode('utf-8')).group(1)
        
        
    def __del__(self):
        self.tn.close()
        
    
    def get_config(self, config_type='saved-configuration'):
        for _ in range(0, 5):
            self.tn.sendline('display {}'.format(config_type))
            config = ''
            while True:
                try:
                    num = self.tn.expect([self.STOP, '{}#'.format(self.hostname)], timeout=10)
                except:
                    print(self.hostname, ' except 1')
                    time.sleep(10)
                    break
                #print(str(self.tn.before, 'utf-8', 'ignore').__repr__())
                config += '\r\n'.join(str(self.tn.before, 'utf-8', 'ignore').split('\r\n')[:-1]) + '\r\n'
                if num == 0:
                    self.tn.send(' ')
                    continue
                elif num == 1:
                    break
            if ('Failure: System is busy' in config) or ('please wait' in config):
                time.sleep(10)
            elif '#\r\nreturn' in config:
                config = re.sub(r'([^#])(\r\n)([^ #\r]+)', '\g<1> \g<3>', config)
                return re.sub(self.ESC, '', '\r\n'.join(config.split('\r\n')[1:]))
            self.tn.sendline(' ')
            while True:
                try:
                    self.tn.expect('#', timeout=10)
                except:
                    print(self.hostname, ' except 2')
                    break
        return ''

class H5616(H5600):
    LOGIN = 'root'
    PASSWORD = 'mduadmin'    
    

#dslam = H5600('172.26.194.12')
#print(dslam.get_config())
