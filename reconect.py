import mechanicalsoup
import sqlite3
class Facebook():
    def __init__(self):
        self.db = sqlite3.connect('bancoface.db')
        self.cursor = self.db.cursor()
        

        self.cursor.execute('CREATE TABLE IF NOT EXISTS Amigos(nome VARCHAR,link VARCHAR)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS Sobre(nome VARCHAR,sexo VARCHAR,fones VARCHAR,aniversario VARCHAR,cidNatal VARCHAR,cidAtual VARCHAR,relacionamento VARCHAR,familiares VARCHAR,acontecimentos VARCHAR,linksobre VARCHAR)')

        self.browser = mechanicalsoup.Browser()

        self.complete = 'https://m.facebook.com'

        pagina = self.browser.get('https://m.facebook.com/login.php')

        

        login = 'marcelo.persevera@gmail.com'
        senha= 'sw0rdf1nsh123'

        print('Conectando ao facebook com {}'.format(login))


        formulario = pagina.soup.find('form')

        formulario.find('input',{'type':'text'})['value'] = login
        formulario.find('input',{'type':'password'})['value'] = senha 
        response = self.browser.submit(formulario, pagina.url)


        if 'save-device' in response.url:
            print('Conectado com Sucesso')
            self.meumenu()
        else:
            print('Login ou Senha Incorretos')
            
    def meumenu(self):
        while True:
            print('\n###Digite###')
            menu = input('''
    1: Adicionar amigos ao banco
    2: Adicionar sobre todos ao banco
    3: Monitore um amigo
    ''')
            if menu == '1':
                self.addAmigos()

            elif menu == '2':
                self.sobreTodos()

            elif menu == '3':
                self.monitore(input('Digite o nome do amigo: '))
            
    def addAmigos(self):
            perfil = self.browser.get('https://m.facebook.com/profile.php')
            linkpagAmigos = perfil.soup.find('a',text='Amigos').get('href')
            

            
            

            
            amigos = self.browser.get(self.complete+linkpagAmigos)
            self.nomes = amigos.soup.findAll(class_='ce')
            amigosTotal = 0

            # ate aqui ele corre na primeira pagina de amigos
            print('Procurando por novos amigos no facebook...')
            for quem in self.nomes:
                    perfilAmigo = self.complete+quem.get('href')
                    
                    
                    amigosTotal +=1
                    amigosEmBanco = self.cursor.execute('SELECT * FROM Amigos ').fetchall()
                    if str(amigosEmBanco).find(quem.text) < 0:
                        print('{} foi adicionado ao banco de dados'.format(quem.text))
                        self.cursor.execute('INSERT INTO Amigos VALUES (?,?)',(quem.text,perfilAmigo))
                        self.db.commit()
            
            # aqui ele corre da segunda pagina de amigos endiante ate gerar um erro
            #esse erro gerado e normal o motivo e por que acaba os amigos na pagina.
            while True:
                print('\n\nAguarde mais uma pagina para analizar\n\n')
                try:
       
                    #pegando link da proxima pagina de amigos
                    linkproximapag = amigos.soup.find(id = 'm_more_friends').find('a').get('href')            
                    amigos = self.browser.get(self.complete+linkproximapag)
                    
                    
                    nomes = amigos.soup.findAll(class_='bq')
                    
                    for nome in nomes:
                        perfilAmigo = self.complete+nome.get('href')
                        amigosTotal +=1

                        amigosEmBanco = self.cursor.execute('SELECT * FROM Amigos ').fetchall()
                        if str(amigosEmBanco).find(nome.text) < 0:
                            print('{} foi adicionado ao banco de dados'.format(nome.text))
                            self.cursor.execute('INSERT INTO Amigos VALUES (?,?)',(nome.text,perfilAmigo))
                            self.db.commit()
                except Exception as erro:
                    print('Total de amigos {}'.format(amigosTotal))
                    break
    
    def sobreTodos(self):       
        for link in self.cursor.execute('SELECT * FROM Amigos ').fetchall():        
            self.sobreEles(link[1])
                    
                   


        
        
    def monitore(self,nomeAmigo):
        amigosEmBanco = self.cursor.execute('SELECT * FROM Sobre WHERE nome =?',[nomeAmigo]).fetchone()
        linksobre = amigosEmBanco[-1]
        self.sobreEles(linksobre)
    
        
        
    def sobreEles(self,pfAmigo):
                            ######Vasculhador sobre amigos#######
                    pagAmigo = self.browser.get(pfAmigo)
                    
                    pagAmigo.soup.find(class_='e').decompose()

                    link = pagAmigo.soup.find('a',text='Sobre')
                    if link:
                        link = link.get('href')
                        
                        sobreAmigo = self.browser.get(self.complete+link)#aqui ele entra na pagina Sobre do amigo

                        print('\n')
                        
                        nome = sobreAmigo.soup.title.text
                        print(nome)
                        self.cursor.execute('INSERT INTO Sobre(nome,linksobre)VALUES(?,?)',(nome,self.complete+link))
                        self.db.commit()
                        
                        celulares = sobreAmigo.soup.findAll('div',text='Celular') #numeros dos celulares
                        celnums = []
                        for celular in celulares:
                            numero = celular.next.next.next.text
                            print('Celular: '+numero)
                            celnums.append(numero)

                        self.cursor.execute('UPDATE Sobre SET fones = ? WHERE  nome = ?',(str(celnums),nome))

                        
                        cidAtual=(sobreAmigo.soup.find('div',text='Cidade atual'))
                        cidNatal = sobreAmigo.soup.find('div',text='Cidade natal')
                        nasc = sobreAmigo.soup.find('div',text='Data de nascimento')
                        genero = sobreAmigo.soup.find('div',text='Gênero')
                        relaci = sobreAmigo.soup.find('div',text='Relacionamento')
                        acoteci= sobreAmigo.soup.find('div',text='Acontecimentos')
                        familia = sobreAmigo.soup.find('div',text='Membros da família')

                        if cidNatal:
                            cidadeN = cidNatal.next.next.next.text
                            print('Cidade Natal: ' + cidadeN)
                            self.cursor.execute('UPDATE Sobre SET cidNatal = ? WHERE  nome = ?',(cidadeN,nome))
                        if cidAtual:
                            cidadeA = cidAtual.next.next.next.text
                            print('Cidade Atual: ' + cidadeA)
                            self.cursor.execute('UPDATE Sobre SET cidAtual = ? WHERE  nome = ?',(cidadeA,nome))

                        if genero:
                            sexo = genero.next.next.next.text
                            print('Sexo: ' + sexo)
                            self.cursor.execute('UPDATE Sobre SET sexo = ? WHERE  nome = ?',(sexo,nome))

                        if nasc:
                            nascido = nasc.next.next.next.text
                            print('Data de Nascimento: ' + nascido)
                            self.cursor.execute('UPDATE Sobre SET aniversario = ? WHERE  nome = ?',(nascido,nome))

                        if relaci:
                            relacionamento = relaci.next.next.next.next.text
                            print(relacionamento)
                            self.cursor.execute('UPDATE Sobre SET relacionamento = ? WHERE  nome = ?',(relacionamento,nome))

          


                        if familia:
                            print('\n Membros da Familia')
                            familist = []
                            for todos in familia.next.next.next.next.findAll('a'):
                                f_nome = todos.next.next.h3
                                if f_nome:
                                    NoMe = f_nome.text
                                    parente = f_nome.find_next('h3').text
                                    print('{}: {}'.format(NoMe,parente))
                                    familist.append('{}: {}'.format(NoMe,parente))
                            self.cursor.execute('UPDATE Sobre SET familiares = ? WHERE  nome = ?',(str(familist),nome))
                            
                            
                            
                        if acoteci:
                            acontelist = []
                            for aconteceu in acoteci.next.next.next.next.findAll('img'):
                                ano = aconteceu.previous.previous
                                act = aconteceu.next.text
                                print('Em {} {}'.format(ano,act))
                                acontelist.append('Em {} {}'.format(ano,act))

                            self.cursor.execute('UPDATE Sobre SET acontecimentos = ? WHERE  nome = ?',(str(acontelist),nome))

                        print('\n\n')
                            
                    
                    

                    


Facebook()


