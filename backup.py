#!/usr/bin/env python3
# coding: utf-8

from concurrent.futures import ThreadPoolExecutor
from resources import SWITCH
from resources import DSLAM
from resources import settings
import zipfile
import datetime
import os
import shutil

DEBUG = True

def run(arg):
    ip = arg[0]
    model = arg[1]
    print('Обработка {}'.format(ip))  
    try:
        if model == 'Q2900':
            ob = SWITCH.Q2900(ip, settings.switch_login, settings.switch_password)
        elif model == 'Q2910':
            ob = SWITCH.Q2910(ip, settings.switch_login, settings.switch_password)
        elif model == 'Q3900':
            ob = SWITCH.Q3900(ip, settings.switch_login, settings.switch_password)
        elif model == 'Q2800':
            ob = SWITCH.Q2800(ip, settings.switch_login, settings.switch_password)
        elif model == 'Q3400':
            ob = SWITCH.Q3400(ip, settings.switch_login, settings.switch_password)
        elif model == 'Q8200':
            ob = SWITCH.Q8200(ip, settings.switch_login, settings.switch_password)
        elif model == 'C3500':
            ob = SWITCH.C3500(ip, settings.switch_login, settings.switch_password)            
        elif model == 'H5600':
            ob = DSLAM.H5600(ip)
        elif model == 'H5616':
            ob = DSLAM.H5616(ip)                
        else:
            return (0, ip)
    except Exception as ex:
        print(ex)
        return (0, ip)
    
    if DEBUG:
        ob.tn.logfile = open('{}{}debug{}{}.txt'.format(settings.backup_folder, os.sep, os.sep, ob.ip), 'wb') 
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    folder_name = '{}{}{}'.format(settings.backup_folder, os.sep, today)
    if ob.TYPE == 'SWITCH':
        out_file = '{}{}{}{}{} {}.cfg'.format(folder_name, os.sep, 'SWITCH', os.sep, ip, today)
    elif ob.TYPE == 'DSLAM':
        out_file = '{}{}{}{}{} {}.cfg'.format(folder_name, os.sep, 'DSLAM', os.sep, ip, today)
    else:
        return (0, ip)
    
    config = ob.get_config()
    if config == '':
        return (0, ip)
    
    with open(out_file, 'a') as file:
        file.write(config)
    print('{} обработан'.format(ip))    
    del ob
    return (1, ip)
 
    
def main():
    switch_ok = 0
    switch_bad = []
    dslam_ok = 0
    dslam_bad = []
    
    print('--- Начало обработки ({}) ---\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    
    folder_name = '{}{}{}'.format(settings.backup_folder, os.sep, today)
    if not os.path.exists('{}{}{}'.format(settings.backup_folder, os.sep, today)):
        os.mkdir(folder_name)
        os.mkdir('{}{}{}'.format(folder_name, os.sep, 'SWITCH'))
        os.mkdir('{}{}{}'.format(folder_name, os.sep, 'DSLAM'))
    if DEBUG:
        if not os.path.exists('{}{}debug'.format(settings.backup_folder, os.sep)):
            os.mkdir('{}{}debug'.format(settings.backup_folder, os.sep))
            
    # Обработка SWITCH
    with ThreadPoolExecutor(max_workers=settings.threads) as executor:
        results = executor.map(run, settings.switchs)
    for result in results:
        if result is None:
            continue
        elif result[0] == 1:
            switch_ok += 1
        else:
            switch_bad.append(result[1])
        
    # Обработка DSLAM    
    with ThreadPoolExecutor(max_workers=settings.threads) as executor:
        results = executor.map(run, settings.dslams)
    for result in results:
        if result is None:
            continue
        elif result[0] == 1:
            dslam_ok += 1
        else:
            dslam_bad.append(result[1])    
            
    print('--- Обработка завершена ({}) ---\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    with open('{}{}info.txt'.format(folder_name, os.sep), 'w') as f:
        f.write('{}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M')))
        f.write('\n\nSWITCH:\n')
        f.write('Всего: {}\n'.format(len(settings.switchs)))
        f.write('Обработано: {}\n'.format(switch_ok))
        f.write('Необработанные: {}\n\n'.format(', '.join(switch_bad)))
        
        f.write('DSLAM:\n')
        f.write('Всего: {}\n'.format(len(settings.dslams)))
        f.write('Обработано: {}\n'.format(dslam_ok))
        f.write('Необработанные: {}\n\n'.format(', '.join(dslam_bad)))
        
        
    z_file = zipfile.ZipFile('{}.zip'.format(folder_name), 'w', compression=zipfile.ZIP_DEFLATED)
    for root, folders, files in os.walk(folder_name):
        for file in files:
            #print(os.sep.join((root, file)))
            z_file.write(os.sep.join((root, file)))
    z_file.close()
    shutil.rmtree(folder_name)
    
    
if __name__ == '__main__':
    main()
