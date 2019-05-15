import mechanicalsoup
from os import system
from threading import Thread
from time import sleep
from datetime import datetime,timedelta
import smtplib
import sqlite3
db = sqlite3.connect('filmesbanco.db')
cursor = db.cursor()

cursor.execute('CREATE TABLE IF NOT EXISTS Filmes(filmes VARCHAR,links VARCHAR)')
cursor.execute('CREATE TABLE IF NOT EXISTS FiltroFilme(filmes VARCHAR)')
cursor.execute('CREATE TABLE IF NOT EXISTS Verificados(filmes VARCHAR)')
cursor.execute('CREATE TABLE IF NOT EXISTS DownList(filmes VARCHAR)')


navegador = mechanicalsoup.Browser()

#nao vi diferença com esse user agent mais to deixando para ver
navegador.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.2228.0 Safari/537.36'})



ListaFilmes = cursor.execute('SELECT * FROM Filmes').fetchall()
Verificados = cursor.execute('SELECT * FROM Verificados').fetchall()
DonwList = cursor.execute('SELECT * FROM DownList').fetchall()


while True:
    FiltroFilme = cursor.execute('SELECT * FROM FiltroFilme').fetchall()
    if FiltroFilme == []:
        print('Os filtros de generos do banco de dados estao vazio')
        while True:
            filtroadd = input('Digite um genero para ser filtrado: ')
            cursor.execute('INSERT INTO FiltroFilme VALUES (?)',[filtroadd])
            db.commit()
            
            comando = input('\nDigite 0 para sair ou Enter para continuar')
            if comando =='0':
                break
    else:
        print('Esses sao seus filtros para o scan de filmes:\n')
        for x in FiltroFilme:
            print(x[0]+'\n')#[0] para tirar de dentro da tupla
            
        
    try:
        FiltroFilme = cursor.execute('SELECT * FROM FiltroFilme').fetchall()
        ListaFilmes = cursor.execute('SELECT * FROM Filmes').fetchall()
        Verificados = cursor.execute('SELECT * FROM Verificados').fetchall()
        pagina = navegador.get('https://bludvcomandotorrents.com/lancamentos/torrent/',timeout = 5)
        if pagina.status_code == 200:
            print('Conectado a:\n'+pagina.url)
        else:
            raise # erro proposital
        

        filmes = pagina.soup.find(id='caixaBusca')
        pesquisa = pagina.soup.findAll(class_='capa_lista text-center')
        
        for check in pesquisa:
                for meufiltro in FiltroFilme:

                    if meufiltro[0].lower() in check.find('p').text.lower() and 'dublad' in check.find('p').text.lower():
                    
                         
                                            link = check.find('a').get('href')
                                            pagina = navegador.get(link)
                                            pesquisa = pagina.soup.findAll('p')
                                            for x in pesquisa:
                                                if('10 / 10' in str(x).lower()):# olhando se o filme esta 10/10
                                                    leitura=pagina.soup.findAll(class_='back')

                                                    try:#pegando o nome do filme
                                                        nome = pagina.soup.find(class_='lista').find('strong',text='Titulo Traduzido:').next.next
                                                    except:# se der falha pega o nome pelo titulo da pagina mesmo
                                                        nome = pagina.soup.title.text

                                                    sobre = '{}\n{}\n{}'.format(nome,leitura[0].text,leitura[1].text)

                                                    #analizando o filme se sera baixar ou nao
                                                    download = False
                                                    for filme in DonwList:
                                                        if filme[0].lower() in nome.lower():
                                                            
                                                            download = True
                                                           
                                                    pegatrailler = pagina.soup.find(class_='w-100 trailer')
                                                  
                                                    trailler= pegatrailler.get('src')


                                                    pegamagnet= pagina.soup.findAll(class_='text-center newdawn')
                                                    for x in pegamagnet:
                                                            if('magnet:' in x.get('href')):# se tiver um link magnet
                                                        
                                                                if(str(ListaFilmes).find(x.get('title'))>1):#filme ja adicionado
                                                                    pass

                                                                else:
                                                                    textolink = x.get('title')
                                                                    print('Filme Adicionado {}\n{}\n\n'.format(nome,textolink))

                                                                    
                                                                    cursor.execute('INSERT INTO Verificados VALUES (?)',[sobre])
                                                                    db.commit()
                                                                    cursor.execute('INSERT INTO Filmes VALUES (?,?)',(x.get('title'),x.get('href')))
                                                                    db.commit()

                                                                    

                                                                    link='\n{}\n{}\n\n'.format(x.get('title'),x.get('href'))
                                                                    osfilmes='{}\n\nTrailler: {}\n{}'.format(sobre,trailler,link)

                                                                    if 'legenda' in textolink.lower() != True:# se nao for legendado ou link de legenda
                                                                       

                                                                        try:
                                                                            smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                                                                            smtp.login('mybotcrawling@gmail.com', 'pythoriano')
                                                                            de = 'mybotcrawling@gmail.com'
                                                                            para = ['marcelo.persevera@gmail.com']
                                                                            menssagem = '\n{}'.format(osfilmes)
                                                                            msg = "From: %s \nTo: %s \nSubject: %s\n %s." % (de, ', '.join(para),nome,menssagem)
                                                                            smtp.sendmail(de, para, msg.encode('utf-8'))
                                                                            smtp.quit()
                                                                            print('Email enviado\n{}'.format(msg))
                                                                        except Exception as falha:
                                                                            print('Falha no envio do email')
                                                                            print(falha)
                                                                        
                                                                        if(download): # se for verdadeiro faz o download   
                                                                            #Examinando o texto do link para fazer o download
                                                                        
                                                                        
                                                                            
                                                                            if '720P' in textolink and 'MKV' in textolink:# se for 720p e mkv faz download
                                                                                print('nao consegui baixar essa imagem {}'.format(pagina.soup.find(class_='img-fluid capa').get('src')))
                                                                                print('Download iniciado')
                                                                                
                                                                                #wget download para baixara capa
                                                                                nomecapa = nome.replace(' ','_')
                                                                                linkcapa = pagina.soup.find(class_='img-fluid capa').get('src')
                                                                                system('wget {}'.format(linkcapa))
                                                                   
                                                                                system('transmission-cli {}'.format(x.get('href')))
                                                                 
                                                                    
                                               
                                                        
        tempo = 60*60 #1 horas   
        somahora=datetime.now() + timedelta(seconds=tempo) 
        print('\n\nFilmes:Proximo scan as {}'.format(somahora.strftime('%H:%M')))
        sleep(tempo)                               
    except Exception as falha:
        print(falha)
        tempo = 60*5 #5 minutos
        somaminutos=datetime.now() + timedelta(seconds=tempo) 
        print('\n\nFilmes:Proximo scan as {}'.format(somaminutos.strftime('%H:%M')))
        sleep(tempo)
                                    

                        
                
                        
                        
                      


                         

                        
                





            

