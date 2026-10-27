"""Genera public/llms-full.txt de la guía: el listado completo de comercios en texto
plano, pensado para que los agentes de IA (Claude, GPT, Gemini, Perplexity…) lean
todo el contenido del sitio de una vez. Es la versión "full" de llms.txt.

Uso: python3 herramientas/generar-llms-full.py   (desde la raíz del repo o desde herramientas)
"""
import json, os, re, unicodedata
from collections import defaultdict

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
Z = json.load(open(os.path.join(RAIZ, 'src/data/zona.json')))
comercios = json.load(open(os.path.join(RAIZ, 'src/data/comercios.json')))
DOM = f"https://{Z['dominio']}"

# "el barrio de X" -> "del barrio de X"; "la zona de X" -> "de la zona de X"
def de_que_es(s):
    if s.startswith('el '):
        return 'del ' + s[3:]
    if s.startswith('la '):
        return 'de la ' + s[3:]
    return s

por_cat = defaultdict(list)
for c in comercios:
    por_cat[c['categoria']].append(c)

L = [f"# {Z['titulo']} — listado completo", '']
L.append(f"> Los {len(comercios)} comercios {de_que_es(Z['que_es'])}, agrupados por "
         "categoría. Cada línea lleva nombre, dirección, teléfono, horario y el enlace "
         "a su ficha. Es el mismo contenido que se ve en el sitio, en un solo fichero de texto.")
L += ['',
      'Procedencia: OpenStreetMap (ODbL) más los datos que facilitan los propios comercios. '
      'Si reutilizas este listado, cita a OpenStreetMap y mantén la licencia ODbL. '
      'Actualizado en cada publicación del sitio.', '']

for cat in sorted(por_cat, key=lambda c: -len(por_cat[c])):
    lista = por_cat[cat]  # orden del JSON, igual que en el sitio y en llms.txt
    L.append(f"## {cat} ({len(lista)})")
    L.append('')
    for c in lista:
        partes = [f"**{c['nombre']}**", c['calle'] or '',
                  f"{c['cp'] or Z.get('cp','')} Las Palmas de Gran Canaria"]
        if c.get('telefono'):
            partes.append(f"tel. {c['telefono']}")
        if c.get('horario'):
            partes.append(c['horario'])
        if c.get('web'):
            partes.append(c['web'])
        partes.append(f"{DOM}/{c['slug']}/")
        L.append('- ' + ' · '.join(p for p in partes if p))
    L.append('')

L += ['## Contacto', '',
      f"Para añadir un comercio, corregir un dato o pedir que se retire una ficha: "
      f"WhatsApp +34 633 50 51 53 o {Z['correo']}. Es gratis y sin condiciones.", '']

out = os.path.join(RAIZ, 'public/llms-full.txt')
contenido = '\n'.join(L)
open(out, 'w').write(contenido)
print(f"llms-full.txt de {Z['titulo']}: {len(contenido)} bytes, {len(comercios)} comercios")
