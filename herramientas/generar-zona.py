"""Genera el plano del barrio a partir de datos de OpenStreetMap (ODbL).

Salida:
  - public/mapa-fondo.svg  : manzanas, parques, agua y calles. Estático, cacheable.
  - src/data/mapa.json     : capa interactiva (edificios con locales, parques infantiles).
"""
import json, math, unicodedata, re
from collections import defaultdict

BASE = '/private/tmp/claude-501/-Users-wosmim/2aea34c7-43f0-461b-94ab-490a468e88dc/scratchpad/'
PROY = '/Users/wosmim/Proyectos/zonaalcaravaneras/'

# ---------------------------------------------------------------------------
# ZONA. Para crear la web de otra zona comercial basta con cambiar este bloque
# y volver a lanzar el script: el resto es genérico.
# ---------------------------------------------------------------------------
ZONA = {
    'nombre': 'Alcaravaneras',
    # Recorte marcado por el usuario: al norte por encima de Calle Barcelona,
    # al oeste Olof Palme / Paseo de Chil, al sur pasado el Parque del Antiguo
    # Estadio Insular, y al este la playa de Las Alcaravaneras con su orilla.
    'sur': 28.1270, 'norte': 28.1350,
    'oeste': -15.4370, 'este': -15.4255,
}

S, N = ZONA['sur'], ZONA['norte']
W, E = ZONA['oeste'], ZONA['este']

K = math.cos(math.radians((S + N) / 2))
ANCHO = 1000
ALTO = round(ANCHO * ((N - S) / ((E - W) * K)))

def px(lon, lat):
    x = (lon - W) * K / ((E - W) * K) * ANCHO
    y = ALTO - (lat - S) / (N - S) * ALTO
    return x, y

def dentro(lon, lat):
    return W <= lon <= E and S <= lat <= N

def toca_zona(geom, margen=0.0004):
    """¿La geometría entra en el recorte? Evita dibujar lo que cae fuera."""
    if not geom:
        return False
    la = [p['lat'] for p in geom]
    lo = [p['lon'] for p in geom]
    return not (max(la) < S - margen or min(la) > N + margen
                or max(lo) < W - margen or min(lo) > E + margen)

def camino(geom, cerrar=True, minimo=1.1):
    """Convierte una lista de puntos OSM en un subcamino SVG.

    Redondea a entero y descarta los puntos que caen a menos de `minimo`
    unidades del anterior: a esta escala no se aprecian y ahorran mucho peso.
    """
    pts = []
    for p in geom:
        x, y = px(p['lon'], p['lat'])
        x, y = round(x), round(y)
        if pts and abs(x - pts[-1][0]) < minimo and abs(y - pts[-1][1]) < minimo:
            continue
        pts.append((x, y))
    if cerrar and len(pts) > 2 and pts[0] == pts[-1]:
        pts.pop()
    if len(pts) < (3 if cerrar else 2):
        return ''
    d = 'M' + ' '.join(f'{x} {y}' for x, y in pts)
    return d + ('Z' if cerrar else '')

def slugificar(t):
    t = unicodedata.normalize('NFD', t)
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '-', t.lower().strip()).strip('-')

def dist_m(px_, py_, x1, y1, x2, y2):
    k = math.cos(math.radians(py_))
    px_, x1, x2 = px_ * k, x1 * k, x2 * k
    dx, dy = x2 - x1, y2 - y1
    t = 0.0 if (dx == 0 and dy == 0) else max(0, min(1, ((px_ - x1) * dx + (py_ - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px_ - (x1 + t * dx), py_ - (y1 + t * dy)) * 111320

def en_poligono(lon, lat, anillo):
    dentro_ = False
    n = len(anillo)
    for i in range(n):
        x1, y1 = anillo[i]
        x2, y2 = anillo[(i + 1) % n]
        if (y1 > lat) != (y2 > lat):
            if lon < (x2 - x1) * (lat - y1) / (y2 - y1) + x1:
                dentro_ = not dentro_
    return dentro_

# ---------- carga ----------
edificios = json.load(open(BASE + 'edif.json'))['elements']
verde = json.load(open(BASE + 'verde.json'))['elements']
vias = json.load(open(BASE + 'vias2.json'))['elements']
negocios = json.load(open(BASE + 'neg.json'))['elements']

# ---------- comercios ----------
CATS = json.load(open(BASE + 'cats.json'))

comercios = []
vistos = set()
for e in negocios:
    t = e.get('tags', {})
    nombre = (t.get('name') or '').strip()
    lat = e.get('lat') or (e.get('center') or {}).get('lat')
    lon = e.get('lon') or (e.get('center') or {}).get('lon')
    clave = t.get('shop') or t.get('amenity') or t.get('craft')
    cat = CATS.get(clave)
    if not (nombre and lat and cat and dentro(lon, lat)):
        continue
    slug = slugificar(nombre)
    # Nombres en alfabetos no latinos pueden quedarse sin slug: les damos uno propio
    if not slug:
        slug = f'comercio-{len(vistos) + 1}'
    if slug in vistos:
        slug = f'{slug}-{len(vistos)}'
    vistos.add(slug)
    comercios.append({'slug': slug, 'nombre': nombre, 'categoria': cat,
                      'lat': lat, 'lon': lon, 'tags': t})

# OSM repite negocios (nodo + polígono del edificio, o dos altas distintas).
# Fusionamos por nombre normalizado dentro de 80 m, ANTES de construir el mapa,
# para que los slugs del plano y de las fichas sean exactamente los mismos.
unicos, fusionados = [], 0
for c in comercios:
    clave = slugificar(c['nombre'])
    gemelo = next(
        (u for u in unicos
         if slugificar(u['nombre']) == clave
         and dist_m(c['lon'], c['lat'], u['lon'], u['lat'], u['lon'], u['lat']) < 80),
        None)
    if gemelo:
        for k, v in c['tags'].items():
            gemelo['tags'].setdefault(k, v)
        fusionados += 1
        continue
    unicos.append(c)
comercios = unicos
print('duplicados fusionados  :', fusionados)

# ---------- asignar cada comercio a su edificio ----------
polis = []
for w in edificios:
    g = w.get('geometry') or []
    if len(g) < 4:
        continue
    anillo = [(p['lon'], p['lat']) for p in g if p]
    lons = [p[0] for p in anillo]; lats = [p[1] for p in anillo]
    polis.append({'id': w['id'], 'anillo': anillo, 'geom': g,
                  'bb': (min(lons), min(lats), max(lons), max(lats)), 'locales': []})

sueltos = []
for c in comercios:
    alojado = None
    for p in polis:
        x0, y0, x1, y1 = p['bb']
        if x0 <= c['lon'] <= x1 and y0 <= c['lat'] <= y1 and en_poligono(c['lon'], c['lat'], p['anillo']):
            alojado = p
            break
    (alojado['locales'] if alojado else sueltos).append(c)

con_locales = [p for p in polis if p['locales']]
print(f'edificios totales      : {len(polis)}')
print(f'edificios con comercio : {len(con_locales)}')
print(f'comercios en edificio  : {sum(len(p["locales"]) for p in con_locales)}')
print(f'comercios sueltos      : {len(sueltos)}')

# ---------- fondo estático ----------
ids_interactivos = {p['id'] for p in con_locales}

d_manzanas = ''.join(camino(p['geom']) for p in polis
                     if p['id'] not in ids_interactivos and toca_zona(p['geom']))

def unir(filtro):
    trozos = []
    for e in verde:
        t = e.get('tags', {})
        if filtro(t) and e.get('geometry') and toca_zona(e['geometry']):
            trozos.append(camino(e['geometry']))
    return ''.join(trozos)

d_parques = unir(lambda t: t.get('leisure') in ('park', 'garden', 'common')
                 or t.get('landuse') in ('grass', 'recreation_ground', 'village_green'))
d_deporte = unir(lambda t: t.get('leisure') in ('pitch', 'sports_centre'))
d_agua = unir(lambda t: t.get('natural') == 'water')

# El mar no viene como polígono: OSM lo describe con líneas de costa. Cerramos
# cada tramo contra el borde este del recorte para poder rellenarlo de azul.
def mar():
    trozos = []
    for e in verde:
        if e.get('tags', {}).get('natural') != 'coastline':
            continue
        g = e.get('geometry') or []
        if not toca_zona(g):
            continue
        pts = [px(q['lon'], q['lat']) for q in g]
        pts = [(round(x), round(y)) for x, y in pts]
        if len(pts) < 2:
            continue
        cuerpo = ' '.join(f'{x} {y}' for x, y in pts)
        trozos.append(f'M{cuerpo} L{ANCHO + 40} {pts[-1][1]} L{ANCHO + 40} {pts[0][1]}Z')
    return ''.join(trozos)

d_mar = mar()
d_arena = unir(lambda t: t.get('natural') in ('beach', 'sand'))

ANCHURAS = {'motorway': 7, 'trunk': 6, 'primary': 5.5, 'secondary': 4.5,
            'tertiary': 3.5, 'residential': 2.6, 'living_street': 2.4,
            'pedestrian': 2.4, 'unclassified': 2.4}
por_ancho = defaultdict(list)
for w in vias:
    a = ANCHURAS.get(w['tags'].get('highway'))
    if a and w.get('geometry') and toca_zona(w['geometry']):
        por_ancho[a].append(camino(w['geometry'], cerrar=False))

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ANCHO} {ALTO}" '
       f'width="{ANCHO}" height="{ALTO}" shape-rendering="geometricPrecision">']
svg.append(f'<rect width="{ANCHO}" height="{ALTO}" fill="#f2ece1"/>')
#
#
if d_mar:
    svg.append(f'<path d="{d_mar}" fill="#bfe0ee"/>')
if d_agua:
    svg.append(f'<path d="{d_agua}" fill="#cfe7f0"/>')
if d_arena:
    svg.append(f'<path d="{d_arena}" fill="#f0e2c2"/>')
if d_parques:
    svg.append(f'<path d="{d_parques}" fill="#cfe4c2"/>')
if d_deporte:
    svg.append(f'<path d="{d_deporte}" fill="#bfdcc8"/>')
for ancho in sorted(por_ancho, reverse=True):
    svg.append(f'<path d="{"".join(por_ancho[ancho])}" fill="none" stroke="#ffffff" '
               f'stroke-width="{ancho}" stroke-linecap="round" stroke-linejoin="round"/>')
svg.append(f'<path d="{d_manzanas}" fill="#ddd3c2" stroke="#cec3b0" stroke-width="0.4"/>')
svg.append('</svg>')

with open(PROY + 'public/mapa-fondo.svg', 'w') as f:
    f.write(''.join(svg))

# ---------- capa interactiva ----------
def reparto(p):
    """Divide el edificio entre sus locales: franjas sobre el lado largo."""
    xs = [px(lon, lat)[0] for lon, lat in p['anillo']]
    ys = [px(lon, lat)[1] for lon, lat in p['anillo']]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    n = len(p['locales'])
    horizontal = (x1 - x0) >= (y1 - y0)
    piezas = []
    for i, c in enumerate(p['locales']):
        if horizontal:
            a = x0 + (x1 - x0) * i / n
            b = x0 + (x1 - x0) * (i + 1) / n
            piezas.append((round(a, 1), round(y0, 1), round(b - a, 1), round(y1 - y0, 1), c))
        else:
            a = y0 + (y1 - y0) * i / n
            b = y0 + (y1 - y0) * (i + 1) / n
            piezas.append((round(x0, 1), round(a, 1), round(x1 - x0, 1), round(b - a, 1), c))
    return piezas

interactivos = []
for p in con_locales:
    for x, y, w, h, c in reparto(p):
        interactivos.append({
            'slug': c['slug'], 'nombre': c['nombre'], 'categoria': c['categoria'],
            'x': x, 'y': y, 'w': max(w, 3.2), 'h': max(h, 3.2),
        })

for c in sueltos:
    x, y = px(c['lon'], c['lat'])
    interactivos.append({
        'slug': c['slug'], 'nombre': c['nombre'], 'categoria': c['categoria'],
        'x': round(x - 3, 1), 'y': round(y - 3, 1), 'w': 6, 'h': 6,
    })

# contorno de los edificios que tienen comercio, para que se vean como bloque
contornos = [camino(p['geom']) for p in con_locales]

infantiles = []
for e in verde:
    if e.get('tags', {}).get('leisure') != 'playground':
        continue
    if e['type'] == 'node':
        lon, lat = e['lon'], e['lat']
    else:
        g = e.get('geometry') or []
        if not g:
            continue
        lon = sum(q['lon'] for q in g) / len(g)
        lat = sum(q['lat'] for q in g) / len(g)
    if not dentro(lon, lat):
        continue
    x, y = px(lon, lat)
    infantiles.append({'x': round(x, 1), 'y': round(y, 1),
                       'nombre': e['tags'].get('name', 'Parque infantil')})

slugs_validos = {f['slug'] for f in fichas} if 'fichas' in dir() else None

mapa = {
    'ancho': ANCHO, 'alto': ALTO,
    'contornos': ''.join(contornos),
    'locales': interactivos,
    'infantiles': infantiles,
}
json.dump(mapa, open(PROY + 'src/data/mapa.json', 'w'), ensure_ascii=False, separators=(',', ':'))

import os
print()
print('viewBox            :', ANCHO, 'x', ALTO)
print('locales pulsables  :', len(interactivos))
print('parques infantiles :', len(infantiles))
print('mapa-fondo.svg     : %.0f kB' % (os.path.getsize(PROY + 'public/mapa-fondo.svg') / 1024))
print('mapa.json          : %.0f kB' % (os.path.getsize(PROY + 'src/data/mapa.json') / 1024))

# ---------- fichas de los comercios ----------
nombradas = [v for v in vias if v['tags'].get('name') and v.get('geometry')]

def calle_cercana(lon, lat):
    mejor, mejor_d = None, 1e9
    for v in nombradas:
        g = v['geometry']
        for i in range(len(g) - 1):
            d = dist_m(lon, lat, g[i]['lon'], g[i]['lat'], g[i + 1]['lon'], g[i + 1]['lat'])
            if d < mejor_d:
                mejor_d, mejor = d, v['tags']['name']
    return mejor, mejor_d

# Rasgos que sí podemos afirmar porque vienen etiquetados en OSM.
CUISINE = {
    'burger': 'Hamburguesas', 'pizza': 'Pizzas', 'italian': 'Cocina italiana',
    'japanese': 'Cocina japonesa', 'mexican': 'Cocina mexicana',
    'american': 'Cocina americana', 'spanish': 'Cocina española',
    'international': 'Cocina internacional', 'coffee_shop': 'Cafetería',
    'ice_cream': 'Heladería', 'churro': 'Churrería', 'empanada': 'Empanadas',
    'fish_and_chips': 'Pescado y patatas', 'regional': 'Cocina regional',
    'seafood': 'Pescado y marisco', 'tapas': 'Tapas', 'chinese': 'Cocina china',
    'indian': 'Cocina india', 'kebab': 'Kebab', 'sandwich': 'Bocadillos',
    'bakery': 'Panadería', 'asian': 'Cocina asiática', 'peruvian': 'Cocina peruana',
    'venezuelan': 'Cocina venezolana', 'arab': 'Cocina árabe',
}
ROPA = {'underwear': 'Ropa interior', 'children': 'Ropa infantil',
        'women': 'Ropa de mujer', 'men': 'Ropa de hombre',
        'babies': 'Ropa de bebé', 'wedding': 'Novias'}
SANIDAD = {'pharmacy': 'Farmacia', 'dentist': 'Dentista', 'doctor': 'Consulta médica',
           'optometrist': 'Óptica', 'physiotherapist': 'Fisioterapia'}

def rasgos_de(t):
    """Datos que OSM etiqueta de forma explícita. No inventamos nada."""
    r = []
    if t.get('brand'):
        r.append(f"Cadena {t['brand']}")
    for v in (t.get('cuisine') or '').split(';'):
        if CUISINE.get(v.strip()):
            r.append(CUISINE[v.strip()])
    for v in (t.get('clothes') or '').split(';'):
        if ROPA.get(v.strip()):
            r.append(ROPA[v.strip()])
    if SANIDAD.get(t.get('healthcare')):
        r.append(SANIDAD[t['healthcare']])
    if t.get('takeaway') == 'yes':
        r.append('Para llevar')
    if t.get('delivery') == 'yes':
        r.append('Reparto a domicilio')
    if t.get('diet:vegetarian') in ('yes', 'only'):
        r.append('Opciones vegetarianas')
    if t.get('diet:vegan') in ('yes', 'only'):
        r.append('Opciones veganas')
    if t.get('internet_access') in ('wlan', 'yes'):
        r.append('WiFi')
    if t.get('atm') == 'yes':
        r.append('Cajero automático')
    if t.get('air_conditioning') == 'yes':
        r.append('Aire acondicionado')
    if t.get('outdoor_seating') == 'yes':
        r.append('Terraza')
    if t.get('wheelchair') == 'yes':
        r.append('Accesible en silla de ruedas')
    elif t.get('wheelchair') == 'limited':
        r.append('Accesibilidad limitada')
    return r

DIAS = {'Mo': 'lunes', 'Tu': 'martes', 'We': 'miércoles', 'Th': 'jueves',
        'Fr': 'viernes', 'Sa': 'sábado', 'Su': 'domingo'}

def horario(oh):
    if not oh:
        return '', []
    if oh == '24/7':
        return 'Abierto todos los días, 24 horas', ['Mo-Su 00:00-24:00']
    if not re.fullmatch(r'[A-Za-z0-9:,\-\s]+', oh):
        return '', []
    txt = oh
    for en, es in DIAS.items():
        txt = re.sub(rf'\b{en}\b', es, txt)
    return txt.replace(',', ', ').replace('  ', ' '), [oh]

fichas = []
for c in comercios:
    t = c['tags']
    calle = t.get('addr:street')
    if not calle:
        calle, d = calle_cercana(c['lon'], c['lat'])
        if not calle or d > 70:
            calle = None
    numero = t.get('addr:housenumber')
    direccion = f'{calle}, {numero}' if calle and numero else (calle or 'Zona Alcaravaneras')

    tel = (t.get('phone') or t.get('contact:phone') or t.get('phone:mobile')
           or t.get('contact:mobile') or t.get('operator:phone') or '').split(';')[0].strip()
    tel = re.sub(r'[^\d+]', '', tel)
    if tel and not tel.startswith('+'):
        tel = '+34' + tel.lstrip('0')

    h, hs = horario(t.get('opening_hours'))
    fichas.append({
        'slug': c['slug'], 'nombre': c['nombre'], 'categoria': c['categoria'],
        'descripcion': '', 'calle': direccion,
        'cp': t.get('addr:postcode') or '35006',
        'telefono': tel,
        'whatsapp': (t.get('contact:whatsapp') or t.get('whatsapp') or '').strip(),
        'email': (t.get('email') or t.get('contact:email') or '').strip(),
        'rasgos': rasgos_de(t),
        'horario': h, 'horarioSchema': hs,
        'web': (t.get('website') or t.get('contact:website')
                or t.get('url') or '').strip(),
        'maps': f"https://www.openstreetmap.org/?mlat={c['lat']}&mlon={c['lon']}#map=19/{c['lat']}/{c['lon']}",
        'lat': round(c['lat'], 6), 'lon': round(c['lon'], 6),
        'fotos': [], 'fuente': 'OpenStreetMap',
    })

fichas.sort(key=lambda f: f['nombre'].lower())
json.dump(fichas, open(PROY + 'src/data/comercios.json', 'w'), ensure_ascii=False, indent=1)
print('fichas generadas   :', len(fichas))
print('  con teléfono     :', sum(1 for f in fichas if f['telefono']))
print('  con horario      :', sum(1 for f in fichas if f['horario']))
print('  con rasgos       :', sum(1 for f in fichas if f['rasgos']))
print('  con email        :', sum(1 for f in fichas if f['email']))
print('  con web          :', sum(1 for f in fichas if f['web']))
print('  con calle+número :', sum(1 for f in fichas if ',' in f['calle']))
print('  completas (tel+horario):', sum(1 for f in fichas if f['telefono'] and f['horario']))
