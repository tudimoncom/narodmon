# Скрипт с помощью модуля Питона request и запроса json запрашивает 
# данные избранного датчика у Domoticz и отправляет часть из них на 
# сервис Народный мониторинг (narodmon.ru)
# Автор tudimon.com

# подключаем модули
import requests
import socket
import urllib3
import random
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


ip = '127.0.0.1' # ip-адрес Domoticz
port = '433' # порт
user = 'dz_user' # пользователь Dz
password = 'dz_user_password' # пароль пользователя 
idx = 25  #номер датчика в Domoticz, который будем опрашивать


# Строка запроса если нужна авторизация
#get_url = 'http://'+user+':'+password+'@'+ip+':'+port+'/json.htm?type=devices&rid={}'.format(idx)

# Строка запроса если не нужна авторизация
# в случае если скприт выполняется на том же устройстве что и Dz и в 
# Настройки - Настройки - Система
# Локальные сети (без имени/пароля) указан ip адрес
get_url = 'https://'+ip+'/json.htm?type=devices&rid={}'.format(idx)

#print ('================================')
#print (get_url)
#print ('================================')


# запрос данных избранного датчика
get_data = requests.get(get_url, verify=False).json()

# ключ verify=False пришлось добавить потому что у меня Dz работает только на 433 порту
# а SSL сертификат самоподписанный, соответвенно request ругался на ошибку сертификата


# ответ придет в виде JSON, где необходимо выбрать интересующее поле, 
# например температура, влажность и уровень заряда батарейки 

humidity = get_data['result'][0]['Humidity']
temperature = get_data['result'][0]['Temp']
batt_level = get_data['result'][0]['BatteryLevel']

#Выведем данные в консоль pi
#print ("Влажность " + str(humidity))
#print ("Температура " + str(temperature))
#print ("Заряд батарейки " + str(batt_level))

# подпроцедура str в данном случае выполняет преобраование 
# числа в строку

# ==================== второй датчик - серверная ====================

idx2 = 91  #номер 2го датчика в Domoticz, который будем опрашивать
get_url2 = 'https://'+ip+'/json.htm?type=devices&rid={}'.format(idx2)
get_data2 = requests.get(get_url2, verify=False).json()
temperature2 = get_data2['result'][0]['Temp']

#print (get_url2)
#print ("Температура2 " + str(temperature2))


# =================== третий датчик - давление =====================

idx3 = 125  #номер 3го датчика в Domoticz, который будем опрашивать
get_url3 = 'https://'+ip+'/json.htm?type=devices&rid={}'.format(idx3)
get_data3 = requests.get(get_url3, verify=False).json()
P = get_data3['result'][0]['Data']

# у кастом датчика в ДЗ хранится и величина и размерность в data. 
# Разобьем на массив и возмем первое в массиве число
P_value = P.split(' ')
#print (P_value[0])

# внесем погрешьноть в сотые после запятой
pogreshnost = random.randint(1,99) / 100
#print ("Погрешность " + str(pogreshnost))

P_itog = float(P_value[0]) + pogreshnost
#print ("Новое давление " + str(P_itog))



# ============== передача данных в сервис narodmon ==================

# MAC адрес устройства. Заменить на свой!
DEVICE_MAC = 'bbbbbbbbbb' # MAC WiFi dz Raspberry Pi

# идентификатор устройства, для простоты добавляется 01 (02) к mac устройства
SENSOR_ID_1 = 'dz_t'
SENSOR_ID_2 = 'dz_h'
SENSOR_ID_3 = 'dz_t_serv'
SENSOR_ID_4 = 'dz_p'

# значения датчиков, тип float/integer
sensor_value_1 = temperature
sensor_value_2 = humidity
sensor_value_3 = temperature2
sensor_value_4 = P_itog

#sensor_value_1 = 21
#sensor_value_2 = 67

# создание сокета
sock = socket.socket()

# обработчик исключений
try:
    # подключаемся к сокету
    sock.connect(('narodmon.ru', 8283))

    # формируем строку для сокета при  единичном значении датчика
    #s_sock = ("#{}\n#{}#{}\n##".format(DEVICE_MAC, SENSOR_ID_1, sensor_value_1))

    # пишем в сокет множественные значение датчиков
    s_sock = ("#{}\n#{}#{}\n#{}#{}\n#{}#{}\n#{}#{}\n##".format(DEVICE_MAC, SENSOR_ID_1, sensor_value_1, SENSOR_ID_2, sensor_value_2, SENSOR_ID_3, sensor_value_3, SENSOR_ID_4, sensor_value_4))

    # Пишем строку с консоль для контроля
    #print('======================================')
    #print('s_sock = ' + s_sock)
    #print('======================================')

    # Пишем в сокет
    sock.send(s_sock.encode('utf8'))


    # читаем ответ
    data = sock.recv(1024)
    sock.close()
#    print (data)
except socket.error as e:
    print('ERROR! Exception {}'.format(e))
