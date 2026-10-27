"""Genera public/llms.txt de la guía a partir de los comercios reales."""
import json, os
from collections import defaultdict

RAIZ = os.path.join(os.path.dirname(__file__), '..')
comercios = json.load(open(os.path.join(RAIZ, 'src/data/comercios.json')))

por_cat = defaultdict(list)
for c in comercios:
    por_cat[c['categoria']].append(c)

def slug_cat(t):
    import unicodedata, re
    t = unicodedata.normalize('NFD', t)
    t = ''.join(ch for ch in t if unicodedata.category(ch) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')

calles = defaultdict(int)
for c in comercios:
    calles[c['calle'].split(',')[0].strip()] += 1
top_calles = sorted(calles.items(), key=lambda x: -x[1])[:10]

L = []
L.append('# Zona Alcaravaneras')
L.append('')
L.append(f"> Guía digital gratuita e independiente de los {len(comercios)} comercios del "
         "barrio de Las Alcaravaneras, en Las Palmas de Gran Canaria (Canarias, España). "
         "Una página por comercio con dirección, teléfono, horario y cómo llegar, además de "
         "un plano del barrio donde cada local es pulsable. Aparecer es gratuito: no hay "
         "cuotas, exclusividad ni permanencia. No está vinculada a ninguna asociación de "
         "comerciantes ni a ningún partido político.")
L.append('')
L.append('La guía la mantiene [Impulcan](https://impulcan.com) — marketing y '
         'automatizaciones — y ningún comercio paga por estar en ella. El sitio no usa '
         'cookies, ni analítica, ni rastreadores. Los datos de partida y la geometría del '
         'plano provienen de OpenStreetMap (licencia ODbL) y se completan con lo que '
         'facilitan los propios comercios.')
L.append('')
L.append('## Qué zona cubre')
L.append('')
L.append('Barrio de Las Alcaravaneras, Las Palmas de Gran Canaria. Delimitado al oeste por '
         'Calle Olof Palme y Paseo de Chil, al norte por encima de Calle Barcelona, al sur '
         'por el Parque del Antiguo Estadio Insular y al este por la Playa de Las '
         'Alcaravaneras y el puerto. Códigos postales 35006 y 35007.')
L.append('')
L.append('Calles con más comercios: ' + ', '.join(f'{c} ({n})' for c, n in top_calles) + '.')
L.append('')
L.append('## Categorías de comercio')
L.append('')
for cat in sorted(por_cat, key=lambda c: -len(por_cat[c])):
    lista = por_cat[cat]
    ejemplos = ', '.join(c['nombre'] for c in lista[:6])
    L.append(f'- [{cat}](https://zonaalcaravaneras.com/categoria/{slug_cat(cat)}/) '
             f'— {len(lista)} comercios. Ejemplos: {ejemplos}.')
L.append('')
L.append('## Páginas clave')
L.append('')
L.append('- [Inicio](https://zonaalcaravaneras.com/): buscador, plano del barrio y listado completo.')
L.append('- [Añadir o corregir un comercio](https://zonaalcaravaneras.com/alta/): gratis, por WhatsApp o correo.')
L.append('- [Créditos de fotografías y datos](https://zonaalcaravaneras.com/creditos/)')
L.append('- [Aviso legal](https://zonaalcaravaneras.com/aviso-legal/)')
L.append('- [Privacidad](https://zonaalcaravaneras.com/privacidad/)')
L.append(f'- [Listado completo en texto plano](https://zonaalcaravaneras.com/llms-full.txt): '
         f'los {len(comercios)} comercios con dirección, teléfono y horario, para agentes de IA.')
L.append('')
L.append('Cada comercio tiene su propia página en `https://zonaalcaravaneras.com/{nombre-del-comercio}/` '
         'con datos estructurados schema.org LocalBusiness.')
L.append('')
L.append('## Contacto')
L.append('')
L.append('- WhatsApp: +34 633 50 51 53')
L.append('- Correo: hola@zonaalcaravaneras.com')
L.append('')

with open(os.path.join(RAIZ, 'public/llms.txt'), 'w') as f:
    f.write('\n'.join(L))
print('llms.txt generado:', len('\n'.join(L)), 'bytes')
