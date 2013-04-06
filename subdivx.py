#! /usr/bin/env python

#imports
from urllib2 import Request, urlopen, URLError, HTTPError
import urllib
import argparse
import os
import re
try:
    from bs4 import BeautifulSoup
except ImportError:
    print 'Es necesaria la biblioteca bs4'

def getArgs():
    
    args  = argparse.ArgumentParser(description='Descargar subtitulos de www.subdivx.com')
    args.add_argument('titulo',nargs='*', help='Titulo de la pelicula')
    title = args.parse_args();
    title = vars(title);
    title = ' '.join(title['titulo']);

    if len(title) <= 1:
        args.print_help()
        exit()
    else:
        return title

def getHTML(title):

    param = urllib.pathname2url(title)
    url = 'http://subdivx.com/index.php?buscar=',param,'&accion=5&subtitulos=1'
    req = Request(''.join(url))

    try:
        response = urlopen(req)
    except HTTPError as e:
        print 'El servidor no pudo realizar la peticion'
        print 'Error: ', e.code
    except URLError as e:
        print 'No es posible comunicarse con el servidor'
        print 'Razon: ', e.reason
    else:
        return response.read()

def parseHTML(html):

        #Parseo el HTML
        soup = BeautifulSoup(html)
        
        #Saco los scripts y estilos
        for elem in soup.findAll(['script', 'style']):
            elem.extract()

        #Parseo los titulos
        titles = []
        for c in soup.findAll('a', {'class': 'titulo_menu_izq'}):
             titles.append(c.string)

        #Parseo las descripciones
        descriptions = []
        for d in soup.findAll('div', {'id': 'buscador_detalle_sub'}):
            descriptions.append(d.text)

        #Parseo los links
        links = []
        for l in soup.findAll('a', {'target': 'new', 'rel': 'nofollow'}):
             links.append(l['href'])

        list = {}
        #Si tengo titulos
        if len(titles) > 0:
           list['titles']       = titles
           list['descriptions'] = descriptions
           list['links']        = links

           return list

        else:
            #Si no encuentro nada, muero ahi
            print 'No se encontro nada'
            exit()

def showData(list):        
    i = 0
    #Muestro titulos y descripcion
    for title in list['titles']:
        print i,'\t','Titulo: ',title, "\n"
        print '\t','Descripcion: ',list['descriptions'][i]
        print '-'*80
        i = i + 1

    # Solo necesito la lista de links y el numero de indice
    # los links tienen el mismo orden que los titulos
    return list['links']

def searchSubtitle(title):
    html  = getHTML(title)
    list  = parseHTML(html) 
    links = showData(list)
    return links

def downloadSubtitle(link):

    archName = re.search('[0-9]+', os.path.basename(link));
    archName = archName.group(0) + '.zip'
     
    try:
        f = urlopen(link)
        print "Bajando ", link
        
        # Open our local file for writing
        with open(archName, "wb") as local_file:
                    local_file.write(f.read())

    except HTTPError, e:
            print "HTTP Error:", e.code, url
    except URLError, e:
           print "URL Error:", e.reason, url,
  

def chooseAndDownload(links):
    while(1):
        try:
            value = input('Escoja un titulo: ')
        except NameError as e:
            print 'Por favor ingrese un numero'
        except KeyboardInterrupt as e:
           exit() 
        else:
            try:
                links[value]
            except IndexError:
                print 'El numero escogido no se encuentra dentro de los posibles, elija nuevamente'
            else:
                downloadSubtitle(links[value])
                break

# MAIN #

#levanto los argumentos
title = getArgs()
#Presentacion
print '''__ __ ____ __ ____ __ __ ____  _| |__  __| (_)_ ____ __  __ ___ _ __  
\ V  V /\ V  V /\ V  V /(_-< || | '_ \/ _` | \ V /\ \ /_/ _/ _ \ '  \ 
 \_/\_/  \_/\_/  \_/\_(_)__/\_,_|_.__/\__,_|_|\_/ /_\_(_)__\___/_|_|_|  - (c) SubDivX - Todos los derechos reservados'''
print '''
Este Script solo devuelve los primeros 20 titulos de la busqueda, si desea una busqueda mas intensiva, por favor dirijase a www.subdivx.com
'''
print "\n"
links = searchSubtitle(title)
value = chooseAndDownload(links)

