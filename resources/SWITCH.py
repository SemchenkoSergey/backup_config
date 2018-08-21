# coding: utf-8

import pexpect
import re

DEBUG = False

class Q2900():
    TYPE = 'SWITCH'
    ESC = r' \x1b.+\[74D'
    STOP = 'next page....'
    END = '#'
    LINE_END = 'WIN'
    
    def __init__(self, ip, login, password):
        self.ip = ip
        self.tn = pexpect.spawn('telnet {}'.format(self.ip))
        if DEBUG:
            self.tn.logfile = open('debug {}.txt'.format(self.ip), 'wb')
        self.tn.expect('Username.*:')
        self.tn.sendline(login)
        self.tn.expect('Password.*:')
        self.tn.sendline(password)
        self.tn.expect('>')
        self.tn.sendline('enable')
        self.tn.expect('#')
    
    def __del__(self):
        self.tn.close()
        
    def get_config(self, config_type='startup-config'):
        config = ''
        self.tn.sendline('show {}'.format(config_type))
        while True:
            num = self.tn.expect([self.STOP, self.END], timeout=30)
            #print(str(self.tn.before, 'utf-8', 'ignore').__repr__())
            config += '\r\n'.join(str(self.tn.before, 'utf-8', 'ignore').split('\r\n')[:-1]) + '\r\n'
            if num == 0:
                self.tn.send(' ')
            elif num == 1:
                break
            
        if self.LINE_END == 'UNIX':
            config.replace('\r', '')
            return re.sub(self.ESC, '', '\n'.join(config.split('\n')[1:]))
        elif self.LINE_END == 'WIN':
            return re.sub(self.ESC, '', '\r\n'.join(config.split('\r\n')[1:]))
        

class Q3900(Q2900):
    ESC = r' \x1b.+\[K'


class Q2910(Q2900):
    ESC = r' \x1b.+\[K'
    

class Q2800(Q2900):
    ESC = ' (\x08)+ +(\x08)+'
    STOP = '--More--'
    LINE_END = 'UNIX'
    
    def __init__(self, ip, login, password):
        self.ip = ip
        self.tn = pexpect.spawn('telnet {}'.format(self.ip))
        if DEBUG:
            self.tn.logfile = open('debug {}.txt'.format(self.ip), 'wb')   
        self.tn.expect('login:')
        self.tn.sendline(login)
        self.tn.expect('Password:')
        self.tn.sendline(password)
        self.tn.expect('>|#')
        self.tn.sendline('enable')        
        self.tn.expect('#')
        
        
        
class Q3400(Q2800):
    pass
    
class Q8200(Q2800):
    pass

    
class C3500(Q2900):
    ESC = r' ?(\x08)+ +(\x08)+'
    STOP = '--More--' 
    LINE_END = 'UNIX'
    
    def __init__(self, ip, login, password):
        self.ip = ip
        self.tn = pexpect.spawn('telnet {}'.format(self.ip))
        if DEBUG:
            self.tn.logfile = open('debug {}.txt'.format(self.ip), 'wb')
        self.tn.expect('Username:')
        self.tn.sendline(login)
        self.tn.expect('Password:')
        self.tn.sendline(password)
        self.tn.expect('#')
        self.END = re.search('\n([\w-]+)$', self.tn.before.decode('utf-8')).group(1) + '#'
    
#sw = Q2900('172.26.194.9', 'cepreu', 'HG4w#$$ffg')
#print(sw.get_config())