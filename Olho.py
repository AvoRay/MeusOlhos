#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from threading import Thread
import sqlite3

db = sqlite3.connect('filmesbanco.db')

cursor = db.cursor()
while True:
    menu = input('\nDigite\n0: Vasculhar\n1: Add Filme\n2: Filmes na Lista\n')
    
    if menu =='1':
        filme = input('Digite o nome do filme:')
        try:
            cursor.execute('INSERT INTO DownList VALUES (?)',[filme])
            db.commit()
            print('O filme {} foi adicionado !'.format(filme))
        except:
            print('Falha ao adicionar o filme')
            
    elif menu =='2':
        #Lista de filmes ja adicionados
        filmes = cursor.execute('SELECT * FROM DownList').fetchall()
        for filme in filmes:
            print(filme[0])
            
    elif menu =='0':
        break


def site1():
    import girodenoticias

def site2():
    import crawlingfilmes
def site3():
    import radar64crawling

site001=Thread(target = site1)
site001.start()


site002=Thread(target = site2)
site002.start()


site003=Thread(target = site3)
site003.start()
