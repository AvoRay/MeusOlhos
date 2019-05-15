import mechanicalsoup
from time import sleep
from datetime import datetime,timedelta
import sqlite3
import smtplib

db = sqlite3.connect('noticias.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS Noticias(noticia,link)')
cursor.execute('CREATE TABLE IF NOT EXISTS Filtro(scan)')
cursor.execute('CREATE TABLE IF NOT EXISTS FiltroCidade(cidades)')

while True:

    banconoticia = cursor.execute('SELECT * FROM Noticias').fetchall()
    filtro = cursor.execute('SELECT * FROM Filtro').fetchall()
    filtrocidade = cursor.execute('SELECT * FROM FiltroCidade').fetchall()
    

    if filtro ==[]:
        print('O filtro de noticias esta vazio !')

    if filtrocidade == []:
        print('O filtro de cidades esta vazio')
    

    try:
        browser = mechanicalsoup.Browser()
        
        pglinks = ['https://radar64.com/noticias','https://radar64.com/noticias/crimes/']

        for pg in pglinks:
        
            pagina = browser.get(pg,timeout = 5)

            if pagina.status_code == 200:
                print('Conectado a:\n'+pagina.url)
            else:
                raise # erro proposital

            assuntos = pagina.soup.findAll(class_='cartaoNoticia ')


            

            

            for assunto in assuntos:
                        for x in filtro:# filtros do meu interese
                            if x[0].lower() in assunto.text.lstrip().lower():
                                
         
                                
                                 
                        ############################################################################################
                                    link = 'http://radar64.com{}'.format(assunto.find('a').get('href'))
                                    
                                    pagina = browser.get(link)

                                    remover = pagina.soup.find(class_='linhaCredito')

                                    if remover != None:
                                        remover.decompose()

                                    remover2 = pagina.soup.find(class_='abrirGaleria')
                                    if remover2 != None:
                                        remover2.decompose()
                                    
 
                                    
                                    noticiafull = pagina.soup.find(id = 'textoNoticia').text
                                    
                                    
                                    
                                    

                                    
                                    for filtrocity in filtrocidade: #filtro de cidades
                                        if filtrocity[0].lower() in noticiafull.lower():

                                            
                                            #Se a noticia ja estiver no banco nada acontece
                                            #usando find de funçao string para encontrar textos exemplo -1 = nao tem o texto , maior que -1 texto encontrado
                                            banconoticia= cursor.execute('SELECT * FROM Noticias').fetchall()

                                            ### usando .replace('','').replace('','') para remover aspas.
                                            if str(banconoticia).find(pagina.soup.title.text.replace('','').replace('',''))< 0:
                                                
                                                

                                                                                                                                #usando replace para remover aspas                                            
                                                cursor.execute('INSERT INTO Noticias VALUES (?,?)',(pagina.soup.title.text.replace('','').replace('',''),link))
                                                db.commit()
                                                try:
                                                    smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                                                    smtp.login('mybotcrawling@gmail.com', 'pythoriano')
                                                    de = 'mybotcrawling@gmail.com'
                                                    para = ['marcelo.persevera@gmail.com']
                                                    menssagem = '\n{}'.format(noticiafull)
                                                    msg = "De: %s \nPara: %s \nSubject:   %s\n\n%s.\nLink: %s" % (de, ', '.join(para),pagina.soup.title.text,menssagem,link)
                                                    smtp.sendmail(de, para, msg.encode('utf-8'))
                                                    smtp.quit()
                                                    print('Email enviado\n{}'.format(msg))
                                                except Exception as falha:
                                                    print('Falha no envio do email')
                                                    print(falha)

        tempo = 60*60*0.5                            
        somahora=datetime.now() + timedelta(seconds=tempo) 
        print('\n\nRadar64:Proximo scan as {}'.format(somahora.strftime('%H:%M')))
                
        sleep(tempo)# 1 horas                        
    except Exception as erro:
            
        print(erro)
        tempo = 60*5
        somaminutos=datetime.now() + timedelta(seconds=tempo) 
        print('\n\nRadar64:Proximo scan as {}'.format(somaminutos.strftime('%H:%M')))
        sleep(tempo)#5minutos

