##Biblioeteke
import RPi.GPIO as GPIO
import serial
import http.client
import urllib
import string
import imaplib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import email
from datetime import datetime
import requests
from email.parser import Parser

#Serijska komunikacija
ser = serial.Serial('/dev/ttyACM0',9600)

#Promenljive za prijem podataka
temperatura = "'Temperatura"
razdaljina = "'Razdaljina"
osvetljenost = "'Osvetljenost"

#definisanje pinova
LEDCrvena = 3
LEDZelena = 4
sleep = 60
#rad sa diodama
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LEDCrvena, GPIO.OUT)
GPIO.setup(LEDCrvena, GPIO.LOW)  #pri pokretanju programa diode ugasiti
GPIO.setup(LEDZelena, GPIO.OUT)
GPIO.setup(LEDZelena, GPIO.LOW)  #pri pokretanju programa diode ugasiti
#rad sa email adresom
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login("internetstvarinis@gmail.com", "singi123")
#inicijalno postavljanje promenljivih na 0
podaci = 0
#vremena za slanje izvestaja
vremeTemperature   = 0    #t2
vremeRastojanja    = 0    #d2
vremeOsvetljenosti = 0    #l2
#vrednosti podataka ako se mail salje posebno za svaku vrednost
temperaturaPosebno = 0    #srt
rastojanjePosebno  = 0    #srd
osvetljenostPosebno= 0    #srf
# vrednosti podataka ukoliko se podaci salju na zahtev konfiguracije
temperaturaKonfig  = 0    #srx
rastojanjeKonfig   = 0    #sry
osvetljenostKonfig = 0    #srz
# pristizanje podataka u niz
prviPodatak = 0  #x
drugiPodatak= 0  #y
treciPodatak= 0  #z
#brojac
brojac = 0
#timeri
timerTemp  = 0
timerRast  = 0
timerOsvet = 0
#niz S
s = []


def konfiguracija():
        mail.list()
        mail.select('inbox')
        
        status, response = mail.search(None,'(SUBJECT "Konfiguracija" UNSEEN)')
		#Broj poruka u mailu
        brojPoruka = (response[0].split()) 
        i=len(response[0].split())
		#niz sa primljenim podacima
        podaci=[] 
		#ako u nizu ima nesto, upaliti crvenu diodu
        if i>0:
                GPIO.output(LEDCrvena, GPIO.HIGH)
				#kada se upali dioda, proveriti koje je vreme("koliko je sati")
                vreme = datetime.time.now().strftime("%HH:%MM:%SS")
				#ispisivanje vremena konfiguracije u formatu "%HH:%MM:%SS"
				#slanje ispisanog vremena na lcd 
                ser.write(vreme.encode)
				#zatim ugasiti diodu
                GPIO.output(LEDCrvena, GPIO.LOW)
		# za svaku poruku u inboxu
        for m_id in brojPoruka:  
				#prepoznaj svaku "liniju poruke"
                retcode, response = mail.fetch(m_id, '(UID BODY[TEXT])')  
                podaci.append(response[0][1].decode("utf-8"))  
                str1 = ''.join(map(str,podaci))
				#regex za provere sadrzaja poruke
                rx = re.compile(r'''^(?P<key>\w+):\s*(?P<value>.+)$''', re.MULTILINE)
				#cmds za svaku vrednost datog kljuca u poruci pronalazi str1 koji je
				#mapiranje vrednosti podataka koji se nalaze u poruci
                cmds = {m.group('key'): m.group('value') for m in rx.finditer(str1)}
				#izvlacenje vrednosti iz maila
                O1 = cmds['Osvetljenost']               # naslov
                vremeOsvetljenosti = int(re.search(r"\d+",O1).group())  # prva rec
                O3 = str(re.search(r"\w+",O1).group())  # druga rec
                T1 =cmds['Temperatura']					#naslov
                vremeTemperature= int(re.search(r"\d+",T1).group())   #prva rec
                T3 = str(re.search(r"\w+",T1).group())  #druga rec
                U1 = cmds['Razdaljina']					#naslov
                vremeRastojanja = int(re.search(r"\d+",U1).group())  #prva rec
                U3 = str(re.search(r"\w+",U1).group())  #druga rec
				
def zahtev():
        mail.list()
        mail.select('inbox')
        result, podaci = mail.uid('search', None, '(SUBJECT "Posalji" UNSEEN)') 
	#uzima samo jedan podatak sa indexom 1
        i = len(podaci[0].split())
        for x in range(i):
                    latest_email_uid = podaci[0].split()[x]
                    #uzimanje maila
                    result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
                    raw_email = email_data[0][1]
                    raw_email_string = raw_email.decode('utf-8')
                    email_message = email.message_from_string(raw_email_string)
                    #prolazak kroz email
                    for part in email_message.walk(): 
                            if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True)
                                    #body email
                                    bodystr=str(body)
                                    split = bodystr.split('\\r\\n')
                                    prvi=split[0]
                                    drugi = prvi.split('b')
                                    treci = drugi[1]
                        
                                    if treci==temperatura:
                                            izvestajTemperaturaK()
                                            print("Poslat Izvestaj")
                                    if treci==razdaljina:
                                            izvestajRastojanjeK()
                                    if treci==osvetljenost:
                                            izvestajOsvetljenostK()
                            else:
                                    continue                
				
def izvestajTemperaturaPosebno():
    msg = MIMEMultipart()
    msg['Subject'] = 'Temperatura '
    sadrzajPoruke = "Prosecna temperatura u poslednjih "+str(vremeTemperature) +"minuta" + "je " + str(temperaturaPosebno) + "stepeni celzijusa"
    textPart = MIMEText(sadrzajPoruke, 'plain')
    msg.attach(textPart)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    #slanjePoruke = MIMEText(sadrzajPoruke,'sadrzaj')
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login("internetstvarinis@gmail.com", "singi123")
    s.sendmail("internetstvarinis@gmail.com", "internetstvarinis@gmail.com", msg.as_string())
    s.quit()
	
def izvestajTemperaturaK():
    msg = MIMEMultipart()
    msg['Subject'] = 'Temperatura '
    sadrzajPoruke = "Prosecna temperatura u poslednjih "+str(vremeTemperature) +"minuta" + "je " + str(temperaturaKonfig) + "stepeni celzijusa"
    textPart = MIMEText(sadrzajPoruke, 'plain')
    msg.attach(textPart)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    #slanjePoruke = MIMEText(sadrzajPoruke,'sadrzaj')
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login("internetstvarinis@gmail.com", "singi123")
    s.sendmail("internetstvarinis@gmail.com", "internetstvarinis@gmail.com", msg.as_string())
    s.quit()

def izvestajRastojanje():
    msg = MIMEMultipart()
    msg['Subject'] = 'Razdaljina '
    sadrzajPoruke = "Prosecna razdaljina u poslednjih "+str(vremeRastojanja) +" minuta" + "je "+str(rastojanjePosebno) + "cm"
    textPart = MIMEText(sadrzajPoruke, 'plain')
    msg.attach(textPart)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    #slanjePoruke = MIMEText(sadrzajPoruke,'sadrzaj')
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login("internetstvarinis@gmail.com", "singi123")
    s.sendmail("internetstvarinis@gmail.com", "internetstvarinis@gmail.com", msg.as_string())
    s.quit()

def izvestajRastojanjeK():
    msg = MIMEMultipart()
    msg['Subject'] = 'Razdaljina '
    sadrzajPoruke = "Prosecna razdaljina u poslednjih "+str(vremeRastojanja) +" minuta" + "je "+str(rastojanjeKonfig) + "cm"
    textPart = MIMEText(sadrzajPoruke, 'plain')
    msg.attach(textPart)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    #slanjePoruke = MIMEText(sadrzajPoruke,'sadrzaj')
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login("internetstvarinis@gmail.com", "singi123")
    s.sendmail("internetstvarinis@gmail.com", "internetstvarinis@gmail.com", msg.as_string())
    s.quit()

def izvestajOsvetljenost():
    msg = MIMEMultipart()
    msg['Subject'] = 'Osvetljenost '
    sadrzajPoruke = "Prosecna osvetljenost u poslednjih "+str(vremeOsvetljenosti) +" minuta" + "je "+str(osvetljenostPosebno) + "lux"
    textPart = MIMEText(sadrzajPoruke, 'plain')
    msg.attach(textPart)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    #slanjePoruke = MIMEText(sadrzajPoruke,'sadrzaj')
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login("internetstvarinis@gmail.com", "singi123")
    s.sendmail("internetstvarinis@gmail.com", "internetstvarinis@gmail.com", msg.as_string())
    s.quit()
	
def izvestajOsvetljenostK():
    msg = MIMEMultipart()
    msg['Subject'] = 'Osvetljenost '
    sadrzajPoruke = "Prosecna razdaljina u poslednjih "+str(vremeOsvetljenosti) +" minuta" + "je "+str(osvetljenostKonfig) + "lux"
    textPart = MIMEText(sadrzajPoruke, 'plain')
    msg.attach(textPart)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    #slanjePoruke = MIMEText(sadrzajPoruke,'sadrzaj')
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login("internetstvarinis@gmail.com", "singi123")
    s.sendmail("internetstvarinis@gmail.com", "internetstvarinis@gmail.com", msg.as_string())
    s.quit()

def notifikacija():
		#kada rastojanje padne ispod 5 cm
		#pali se zelena dioda
        GPIO.output(LEDZelena, GPIO.HIGH)
		#salje se notifikacija
        requests.post("https://maker.ifttt.com/trigger/Udaljenost/with/key/ibaAV5QZYrwkD8a06SgteVF6h_8hELBIylhPzy1rnnO")
        #provera da li je rastojanje ispod 5
        print ("notifikacija")
		#Potrbno je staviti minut, zbog potreba testiranja postavljeno 10
        #time.sleep(10)
time.sleep(10)
		#ugasiti diodu
GPIO.output(LEDZelena, GPIO.LOW)

def citanjePodataka(ser):
    return int(ser.readline())

while True:
	mail.list()
mail.select('inbox')
status, response = mail.search(None,'(SUBJECT "Konfiguracija" UNSEEN)')
status1, response1 = mail.search(None,'(SUBJECT "Posalji" UNSEEN)')
    #broj mailova
msg_num = (response[0].split())
msg_num2 = (response1[0].split())
msg_num2
podaci1=[]
podaci2=[]
i=len(response[0].split())
	#ako ima podataka
if i>0:
		GPIO.output(LEDCrvena, GPIO.HIGH)
time.sleep(10)
GPIO.output(LEDZelena, GPIO.LOW)
i=0
	
for m_id in brojPoruka:  
		#prepoznaj svaku "liniju poruke"
        retcode, response = mail.fetch(m_id, '(UID BODY[TEXT])')  
        podaci1.append(response[0][1].decode("utf-8"))  
        str1 = ''.join(map(str,podaci1))
		#regex za provere sadrzaja poruke
        rx = re.compile(r'''^(?P<key>\w+):\s*(?P<value>.+)$''', re.MULTILINE)
		#cmds za svaku vrednost datog kljuca u poruci pronalazi str1 koji je
		#mapiranje vrednosti podataka koji se nalaze u poruci
        cmds = {m.group('key'): m.group('value') for m in rx.finditer(str1)}
		#izvlacenje vrednosti iz maila
        O1 = cmds['Osvetljenost']               # naslov
        vremeOsvetljenosti = int(re.search(r"\d+",O1).group())  # prva rec
        O3 = str(re.search(r"\w+",O1).group())  # druga rec
        T1 =cmds['Temperatura']					#naslov
        vremeTemperature= int(re.search(r"\d+",T1).group())   #prva rec
        T3 = str(re.search(r"\w+",T1).group())  #druga rec
        U1 = cmds['Razdaljina']					#naslov
        vremeRastojanja = int(re.search(r"\d+",U1).group())  #prva rec
        U3 = str(re.search(r"\w+",U1).group())  #druga rec
for m_id in msg_num:
            mail.store(m_id, '+FLAGS', '\seen')
            vreme = datetime.now()
            v = ("{:02d}:{:02d}:{:02d}".format(vreme.hour,vreme.minute,vreme.second))
            ser.write(v.encode())
            mail.expunge()
            podaci = ser.readline()
if podaci:
		s.append(podaci)
		#stizu 3 podatka
		#kada se u niz s smeste 3 podatka
		#onda se podaci dodaju ponovo na vec postojece kako bi se izracunala srednja vrednost
if len(s)==3:
    prviPodatak = int(s[0])
    drugiPodatak = float(s[1])
    treciPodatak = int(s[2])
		#stampanje samo radi provere, nije neophodno
    print(prviPodatak)
    print(drugiPodatak)
    print(treciPodatak)
    if x<5:
            notifikacija()
		#racunanje srednje vrednosti
    ppSV += prviPodatak
    dpSV += drugiPodatak
    tpSV += treciPodatak
		#ponistavanje
    prviPodatak  = 0
    drugiPodatak = 0
    treciPodatak = 0
    brojac+=1
    timerTemp +=1
    timerRast +=1
    timerOsvet+=1
		#racunanje srednje vrednosti
    temperaturaKonfig =  ppSV/brojac
    rastojanjeKonfig =   dpSV/brojac
    osvetljenostKonfig = tpSV/brojac
    zahtev()
		#vremeTemperature je zahtev/period procitan iz maila
    if (int((timerTemp)) == int((vremeTemperature*60))):
        temperaturaPosebno = temperaturaKonfig
        izvestajTemperatura()
    print("Temperatura")
    timerTemp = 0
    if (int((timerRast)) == int((vremeRastojanja*60))):
        rastojanjePosebno = rastojanjeKonfig
        izvestajRastojanje()
    print("Rastojanje")
    timerRast = 0
    if (int((timerOsvet)) == int((vremeOsvetljenosti*60))):
        osvetljenostPosebno = osvetljenostKonfig
        izvestajOsvetljenost()
    print("Osvetljenost")
    timerOsvet = 0
                        
    s = []
