import mechanicalsoup
from time import sleep
from datetime import datetime,timedelta
import sqlite3
import smtplib
dbface = sqlite3.connect('bancoface.db')
db = sqlite3.connect('noticias.db')
cursor = dbface.cursor()
cursor2 = db.cursor()
cursor2.execute('CREATE TABLE IF NOT EXISTS Noticias(noticia,link)')
cursor2.execute('CREATE TABLE IF NOT EXISTS Filtro(scan)')
cursor2.execute('CREATE TABLE IF NOT EXISTS FiltroCidade(cidades)')


while True:
    amigos = cursor.execute('SELECT * FROM Amigos').fetchall()
    filtro = cursor2.execute('SELECT * FROM Filtro').fetchall()
    filtrocidade = cursor2.execute('SELECT * FROM FiltroCidade').fetchall()

    if filtro ==[]:
        print('O filtro de noticias esta vazio !')
        break

    if filtrocidade == []:
        print('O filtro de cidades esta vazio')
        break
    
    
    



    try:
        browser = mechanicalsoup.Browser()
        linkpaginas = ['http://girodenoticias.com/noticias/geral/','http://girodenoticias.com/noticias/policia/']

        for pg in linkpaginas:
    
            pagina = browser.get(pg,timeout =5)

            

            if pagina.status_code == 200:
                print('Conectado a:\n'+pagina.url)
            else:
                raise # erro proposital
            
            asnoticias = pagina.soup.find(class_='ui unstackable divided items')
            noticias = asnoticias.findAll(class_='item')

            

            for x in noticias:
                assunto = x.find('h3')
                for check in filtro:
                    if check[0].lower() in assunto.text.lower():
                        #####for checkcidade in filtrocidade:
                            ######if checkcidade[0].lower() in assunto.text.lower():

                                #Se a noticia ja estiver no banco nada acontece
                                banconoticia= cursor2.execute('SELECT * FROM Noticias').fetchall()
                                if str(banconoticia).find(assunto.text)< 0:#usando find de funçao string para encontrar textos exemplo -1 = nao tem o texto , maior que -1 texto encontrado 
                                    link= 'http://girodenoticias.com{}'.format(x.find('a').get('href'))
                                    pagina = browser.get(link)

                                    noticiafull = pagina.soup.find(id='purepage').text
                                    
                                    for checkcidade in filtrocidade:
                                        if checkcidade[0].lower() in noticiafull.lower():

                                            cursor2.execute('INSERT INTO Noticias VALUES (?,?)',(assunto.text,link))
                                            db.commit()
                                            for amigo in amigos:
                                                ########################################################################
                                                if amigo[0].lower() in noticiafull.lower():# se tiver alguem do facebook na noticia
                                                    try:
                                                        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                                                        smtp.login('mybotcrawling@gmail.com', 'pythoriano')
                                                        de = 'mybotcrawling@gmail.com'
                                                        para = ['marcelo.persevera@gmail.com']
                                                        menssagem = '\n{}'.format(noticiafull)
                                                        msg = "From: %s \nTo: %s \nSubject: Emergencia!!!\n Noticia sobre %s %s.\nLink: %s" % (de, ', '.join(para),amigo[0],menssagem,link)
                                                        smtp.sendmail(de, para, msg.encode('utf-8'))
                                                        smtp.quit()
                                                        print('Email enviado\n{}'.format(msg))
                                                    except Exception as falha:
                                                        print('Falha no envio do email')
                                                        print(falha)
                                            #Ninguem do facebook mas quero ver as notcias
                                            try:
                                                smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                                                smtp.login('mybotcrawling@gmail.com', 'pythoriano')
                                                de = 'mybotcrawling@gmail.com'
                                                para = ['marcelo.persevera@gmail.com']
                                                menssagem = '\n{}'.format(noticiafull)
                                                msg = "De: %s \nPara: %s \nSubject:   %s\n\n%s.\nLink: %s" % (de, ', '.join(para),assunto.text,menssagem,link)
                                                smtp.sendmail(de, para, msg.encode('utf-8'))
                                                smtp.quit()
                                                print('Email enviado\n{}'.format(msg))
                                            except Exception as falha:
                                                print('Falha no envio do email')
                                                print(falha)

                                
                                
        tempo = 60*30                            
        somahora=datetime.now() + timedelta(seconds=tempo) 
        print('\n\nGiroDeNoticias:Proximo scan as {}'.format(somahora.strftime('%H:%M')))
        
        sleep(tempo)# 30 minutos                        
    except Exception as erro:
        
        print(erro)
        tempo = 60*5
        somaminutos=datetime.now() + timedelta(seconds=tempo) 
        print('\n\nGiroDeNoticias:Proximo scan as {}'.format(somaminutos.strftime('%H:%M')))
        sleep(tempo)#5minutos
