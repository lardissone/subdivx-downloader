#! /usr/bin/env python

# imports
from urllib2 import Request, urlopen, URLError, HTTPError
import urllib
import argparse
import os
import re
try:
    from bs4 import BeautifulSoup
except ImportError:
    print 'Es necesaria la biblioteca bs4'


def get_args():

    args = argparse.ArgumentParser(
        description='Descargar subtitulos de www.subdivx.com')
    args.add_argument('titulo', nargs='*', help='Titulo de la pelicula')
    title = args.parse_args()
    title = vars(title)
    title = ' '.join(title['titulo'])

    if len(title) <= 1:
        args.print_help()
        exit()
    else:
        return title


def get_html(title):

    param = urllib.pathname2url(title)
    url = 'http://subdivx.com/index.php?buscar=%s&accion=5&subtitulos=1'
    req = Request(''.join(url % param))

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


def parse_html(html):

        # Parseo el HTML
        soup = BeautifulSoup(html)

        # Saco los scripts y estilos
        for elem in soup.findAll(['script', 'style']):
            elem.extract()

        # Parseo los titulos
        titles = []
        for c in soup.findAll('a', {'class': 'titulo_menu_izq'}):
            titles.append(c.string)

        # Parseo las descripciones
        descriptions = []
        for d in soup.findAll('div', {'id': 'buscador_detalle_sub'}):
            descriptions.append(d.text)

        # Parseo los links
        links = []
        for l in soup.findAll('a', {'target': 'new', 'rel': 'nofollow'}):
            links.append(l['href'])

        subs = {}
        # Si tengo titulos
        if len(titles) > 0:
            subs['titles'] = titles
            subs['descriptions'] = descriptions
            subs['links'] = links

            return subs

        else:
            # Si no encuentro nada, muero ahi
            print 'No se encontro nada'
            exit()


def show_data(subs):
    i = 0
    # Muestro titulos y descripcion
    for title in subs['titles']:
        print '%s\tTitulo: %s' % (i, title)
        print '\tDescripcion: %s' % subs['descriptions'][i]
        print '-' * 80
        i = i + 1

    # Solo necesito la lista de links y el numero de indice
    # los links tienen el mismo orden que los titulos
    return subs['links']


def search_subtitle(title):
    html = get_html(title)
    subs = parse_html(html)
    links = show_data(subs)
    return links


def download_subtitle(link):

    archName = re.search('[0-9]+', os.path.basename(link))
    archName = archName.group(0) + '.zip'

    try:
        f = urlopen(link)
        print "Bajando ", link

        # Open our local file for writing
        with open(archName, "wb") as local_file:
                    local_file.write(f.read())

    except HTTPError, e:
        print "HTTP Error:", e.code, link
    except URLError, e:
        print "URL Error:", e.reason, link


def choose_and_download(links):
    while(1):
        try:
            value = input('Escoja un titulo: ')
        except NameError:
            print 'Por favor ingrese un numero'
        except KeyboardInterrupt:
            exit()
        else:
            try:
                links[value]
            except IndexError:
                print 'El numero escogido no se encuentra \
                dentro de los posibles, elija nuevamente'
            else:
                download_subtitle(links[value])
                break

# MAIN

# levanto los argumentos
title = get_args()

# presentacion
print '__ __ ____ __ ____ __ __ ____  _| |__  __| (_)_ ____ __  __ ___ _ __'
print '\ V  V /\ V  V /\ V  V /(_-< || | \'_ \/ _` | \ V /\ \ /_/ _/ _ \ \'\
  \\'
print ' \_/\_/  \_/\_/  \_/\_(_)__/\_,_|_.__/\__,_|_|\_/ /_\_(_)__\___/_|_|_|\
  - (c) SubDivX - Todos los derechos reservados'
print 'Este Script solo devuelve los primeros 20 titulos de la busqueda, si \
desea una busqueda mas intensiva, por favor dirijase a www.subdivx.com'
print '\n'

links = search_subtitle(title)
value = choose_and_download(links)
