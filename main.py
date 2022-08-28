import requests
import time
import inquirer
import json
from datetime import datetime
from line import LINE
import re 
questions = [
  inquirer.List('service',
                message="What service otp do you need?",
                choices=['C2X', 'Google'],
            ),
]

confirm = {
    inquirer.Confirm('confirmed',
                     message="Do you want otp ?" ,
                     default=True),
}

confirm2 = {
    inquirer.Confirm('confirmed',
                     message="Do you want use sevice ?" ,
                     default=True),
}

f = open('setting.json')

data = json.load(f)
apikey = data['api_key']

if not data['token_line']:
    print('Please check token line')
    exit()

if not apikey:
    print('Please check api key')
    exit()

line = LINE(data['token_line'])




def timestamp():
    nowTime = int(datetime.timestamp(datetime.now()))
    timeUnit = datetime.fromtimestamp(nowTime).strftime('%Y-%m-%d %H:%M:%S')
    fomat_dt = f'[{timeUnit}]'
    return fomat_dt

def check_token(response,id_giaodich):
    convertedDict = json.loads(response)
    if convertedDict['status'] == 401 :
        print(f"{timestamp()} {convertedDict['message']}")
        cancle_trx(id_giaodich)
        exit()


def creating_trx(dichvu_id,so_sms_nhan):
    try:
        GetDS_DichVu = requests.get(f"http://api.codesim.net/api/CodeSim/DangKy_GiaoDich?apikey={apikey}&dichvu_id={dichvu_id}&so_sms_nhan={so_sms_nhan}").json()
        return GetDS_DichVu
    except Exception as int:
        print(int)

def  checking_trx(giaodich_id):
    try:
        GetDS_DichVu = requests.get(f"http://api.codesim.net/api/CodeSim/KiemTraGiaoDich?apikey={apikey}&giaodich_id={giaodich_id}").json()
        return GetDS_DichVu
    except Exception as int:
        print(int)

def cancle_trx(giaodich_id):
    try:
        GetDS_DichVu = requests.get(f"http://api.codesim.net/api/CodeSim/HuyGiaoDich?apikey={apikey}&giaodich_id={giaodich_id}").json()
        if GetDS_DichVu['stt'] == 1:
            print(f"{timestamp()} Success cancle otp")
        if GetDS_DichVu['stt'] == 0:
            print(f"{timestamp()} Failure cancle otp")
    except Exception as int:
        print(int)
    
def main():
    try:
        con = True
        while loop:
            answers = inquirer.prompt(questions)
            service = ""
            if answers['service'] == 'C2X':
                service = answers['service']
                if con == True:
                    confirmation = inquirer.prompt(confirm)
                if confirmation['confirmed'] == True:
                    phoneNumber = ""
                    amount = 1
                    trx = creating_trx(133,amount)
                    if trx['stt'] == 1:
                        check_loop = True
                        phoneNumber = trx['data']['phoneNumber']
                        id_giaodich = trx['data']['id_giaodich']
                        print(f"{timestamp()} Telphone: {phoneNumber} Wait OTP")
                        lineMessage = f'Telphone : {phoneNumber}'
                        response = line.sendtext(lineMessage)
                        check_token(response,id_giaodich)
                        count = 0
                        while check_loop:

                           check_trx = checking_trx(id_giaodich)
                           if check_trx['stt'] == 1 and check_trx['data']['status'] == 0:
                                time.sleep(5)
                                count = count + 5
                                if count >= 60:
                                    cancle_trx(id_giaodich)
                                    break
                                else:
                                    continue

                           if check_trx['stt'] == 1 and check_trx['data']['status'] == 1 :
                                if check_trx['data']['status'] == 1:
                                    listSms = check_trx['data']['listSms'][0]['smsContent']
                                    
                                    sms = re.search(r"\[([A-Za-z0-9_]+)\]", listSms)
                                    
                                    print(f"{timestamp()} MetaMagnet OTP : {sms.group(1)}")
                                    lineMessage = f'MetaMagnet OTP : {sms.group(1)}'
                                    line.sendtext(lineMessage)
                                    check_loop = False
                           if check_trx['stt'] == 3:
                                print(f"{timestamp()} Transaction has been canceled erase")
                                check_loop = False
                    if trx['stt'] == 0:
                        print(f"{timestamp()} Failure create transaction")
            confirmation = inquirer.prompt(confirm2)
            if confirmation['confirmed'] == True:
                con = False
                continue
            if confirmation['confirmed'] == False:
                loop = False
                print(f"{timestamp()} Thank you for sevice")
    except Exception as int:
        print(int)


if __name__ == '__main__':
    main()
