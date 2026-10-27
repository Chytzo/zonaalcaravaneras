#!/usr/bin/env python3
"""Genera las ilustraciones de categoría de las guías de barrio.

Una sola familia visual para las cuatro webs: mismo lienzo 800×500, misma luz
(sombra larga hacia la derecha), mismo grano de papel, misma paleta atlántica
heredada de `src/styles/global.css`. Nada de fotos de stock ni de imágenes de
terceros: son SVG propios, pesan 3-6 KB y no hacen ni una petición externa.

Salida: public/img/categorias/<slug>.svg  (+ generico.svg)

Uso:
    python3 herramientas/gen-imagenes-categorias.py [--destino RUTA]
"""
import argparse
import os

# Paleta base del sitio (global.css)
OCEANO = '#073b4f'
OCEANO_HONDO = '#04222e'
AGUA = '#1b7f9e'
AGUA_CLARA = '#dcf0f6'
ARENA = '#faf6ee'
ARENA_HONDA = '#efe7d8'
SOL = '#e2683f'
SOL_CLARO = '#fbe6de'
ORO = '#d4a017'
TINTA = '#16232a'

# Fondo de cada categoría: degradado muy claro, tinte propio para distinguirlas
# sin competir con el contenido de la tarjeta.
FONDOS = {
    'restaurantes': ('#fff2ec', '#ffe0d2'),
    'bares-y-cafes': ('#fdf1e3', '#f8dfc4'),
    'alimentacion': ('#eef7ec', '#d8ecd6'),
    'moda': ('#f3eefb', '#e3d8f6'),
    'belleza': ('#fceef6', '#f6dcec'),
    'salud': ('#eaf3fb', '#d5e7f7'),
    'deporte-y-ocio': ('#e9f6f2', '#d2ece5'),
    'hogar-y-reformas': ('#f5f1e8', '#e9e1d0'),
    'electronica': ('#e8f5f4', '#d0ebe9'),
    'bazares': ('#fbf5e3', '#f4e8c2'),
    'motor': ('#eef1f4', '#dde3e9'),
    'mascotas': ('#fdeeee', '#f7dcdc'),
    'servicios': ('#eff2f5', '#dfe5ec'),
    'hogar-y-decoracion': ('#f7f2e9', '#ece0cd'),
}


def lienzo(slug: str, cuerpo: str) -> str:
    """Envuelve una escena con el fondo, el grano y la sombra comunes."""
    a, b = FONDOS.get(slug, ('#f4f4f2', '#e6e6e2'))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="800" height="500" role="img">
  <defs>
    <linearGradient id="fondo" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0" stop-color="{a}"/>
      <stop offset="1" stop-color="{b}"/>
    </linearGradient>
    <radialGradient id="luz" cx="0.32" cy="0.22" r="0.85">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.75"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </radialGradient>
    <filter id="grano" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7"/>
      <feColorMatrix type="saturate" values="0"/>
    </filter>
    <filter id="difumina" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="9"/>
    </filter>
  </defs>
  <rect width="800" height="500" fill="url(#fondo)"/>
  <rect width="800" height="500" fill="url(#luz)"/>
{cuerpo}
  <rect width="800" height="500" filter="url(#grano)" opacity="0.055" style="mix-blend-mode:multiply"/>
</svg>
'''


def sombra(cx: float, cy: float, rx: float, ry: float, op: float = 0.16) -> str:
    """Sombra larga hacia la derecha, la firma de la familia."""
    return (
        f'  <ellipse cx="{cx + rx * 0.42:.1f}" cy="{cy}" rx="{rx}" ry="{ry}" '
        f'fill="{OCEANO}" opacity="{op}" filter="url(#difumina)"/>'
    )


# --------------------------------------------------------------------------
# Escenas. Cada una: tres objetos grandes, un acento de color, cero texto.
# --------------------------------------------------------------------------

def restaurantes() -> str:
    return (
        sombra(392, 396, 196, 26)
        + f'''
  <circle cx="392" cy="300" r="134" fill="{ARENA}"/>
  <circle cx="392" cy="300" r="134" fill="none" stroke="{AGUA_CLARA}" stroke-width="3"/>
  <circle cx="392" cy="300" r="98" fill="{SOL}" opacity="0.14"/>
  <circle cx="392" cy="300" r="68" fill="{SOL_CLARO}"/>
  <circle cx="392" cy="300" r="68" fill="none" stroke="{SOL}" stroke-width="4" opacity="0.5"/>
  <!-- tenedor -->
  <g fill="{TINTA}">
    <rect x="196" y="256" width="18" height="112" rx="9"/>
    <rect x="196" y="206" width="6" height="46" rx="3"/>
    <rect x="207" y="206" width="6" height="46" rx="3"/>
    <rect x="218" y="206" width="6" height="46" rx="3"/>
    <rect x="196" y="244" width="28" height="16" rx="8"/>
  </g>
  <!-- cuchillo -->
  <g fill="{TINTA}">
    <rect x="566" y="256" width="18" height="112" rx="9"/>
    <path d="M566 206c22 0 30 18 30 34v16h-30z"/>
  </g>
  <!-- copa -->
  <g>
    <path d="M392 196h56l-8 54a20 20 0 0 1-40 0z" fill="{AGUA}"/>
    <path d="M394 236h52l-6 34a20 20 0 0 1-40 0z" fill="{OCEANO}" opacity="0.45"/>
    <rect x="414" y="288" width="12" height="46" rx="6" fill="{AGUA}" opacity="0.7"/>
    <rect x="396" y="330" width="48" height="10" rx="5" fill="{AGUA}" opacity="0.7"/>
  </g>
  <circle cx="238" cy="404" r="18" fill="{ORO}" opacity="0.7"/>
  <circle cx="556" cy="408" r="12" fill="{SOL}" opacity="0.55"/>'''
    )



def bares_y_cafes() -> str:
    return (
        sombra(392, 396, 170, 22)
        + f'''
  <path d="M258 244h236v86a70 70 0 0 1-70 70h-96a70 70 0 0 1-70-70z" fill="{ARENA}"/>
  <path d="M258 244h236v22H258z" fill="{ARENA_HONDA}"/>
  <path d="M494 268h34a30 30 0 0 1 0 60h-34" fill="none" stroke="{ARENA}" stroke-width="18"/>
  <ellipse cx="376" cy="248" rx="118" ry="18" fill="{OCEANO}" opacity="0.86"/>
  <g stroke="{ARENA}" stroke-width="7" stroke-linecap="round" opacity="0.55" fill="none">
    <path d="M330 214c14-18 14-32 0-48"/>
    <path d="M382 206c16-22 16-38 0-58"/>
    <path d="M434 214c14-18 14-32 0-48"/>
  </g>
  <g fill="{SOL}">
    <ellipse cx="216" cy="330" rx="17" ry="23" transform="rotate(-20 216 330)"/>
    <ellipse cx="216" cy="330" rx="4" ry="20" fill="{OCEANO}" opacity="0.35" transform="rotate(-20 216 330)"/>
    <ellipse cx="196" cy="382" rx="16" ry="22" transform="rotate(14 196 382)"/>
  </g>
  <circle cx="596" cy="376" r="34" fill="{ORO}" opacity="0.85"/>
  <circle cx="596" cy="376" r="22" fill="{ARENA}" opacity="0.55"/>'''
    )


def alimentacion() -> str:
    return (
        sombra(400, 404, 186, 24)
        + f'''
  <path d="M296 236h208l-26 168H322z" fill="{ORO}" opacity="0.85"/>
  <path d="M296 236h208l-8 46H304z" fill="{SOL}" opacity="0.7"/>
  <g stroke="{OCEANO}" stroke-width="7" fill="none" opacity="0.5" stroke-linecap="round">
    <path d="M330 268l16 116"/><path d="M368 268l8 116"/><path d="M408 268l-8 116"/><path d="M448 268l-16 116"/>
  </g>
  <path d="M336 244a64 64 0 0 1 128 0" fill="none" stroke="{OCEANO}" stroke-width="12" stroke-linecap="round"/>
  <circle cx="400" cy="228" r="34" fill="{SOL}"/>
  <circle cx="400" cy="228" r="24" fill="{SOL_CLARO}" opacity="0.35"/>
  <path d="M400 194c0-14 10-24 22-26 0 14-10 24-22 26z" fill="{AGUA}"/>
  <circle cx="500" cy="300" r="26" fill="{AGUA}"/>
  <path d="M500 274c0-12 8-20 18-22 0 12-8 20-18 22z" fill="{OCEANO}" opacity="0.65"/>
  <ellipse cx="286" cy="330" rx="24" ry="30" fill="{SOL}" opacity="0.75"/>'''
    )


def moda() -> str:
    return (
        sombra(402, 402, 168, 22)
        + f'''
  <path d="M400 158v32" stroke="{TINTA}" stroke-width="8" stroke-linecap="round"/>
  <path d="M400 190a20 20 0 1 0 0-40 20 20 0 0 0 0 40z" fill="{ORO}"/>
  <path d="M330 236h140l52 96-40 22-30-44v112H348V310l-30 44-40-22z" fill="{AGUA}"/>
  <path d="M348 236c10 26 94 26 104 0" fill="none" stroke="{OCEANO}" stroke-width="6" opacity="0.5"/>
  <path d="M366 190c22 16 46 16 68 0" fill="none" stroke="{TINTA}" stroke-width="7" stroke-linecap="round"/>
  <circle cx="596" cy="330" r="46" fill="{SOL}" opacity="0.8"/>
  <rect x="168" y="268" width="76" height="120" rx="12" fill="{OCEANO}" opacity="0.18"/>'''
    )


def belleza() -> str:
    return (
        sombra(396, 400, 164, 22)
        + f'''
  <!-- pintalabios -->
  <g>
    <rect x="252" y="266" width="60" height="132" rx="12" fill="{OCEANO}"/>
    <rect x="252" y="252" width="60" height="26" rx="8" fill="{ORO}"/>
    <path d="M262 252v-46l40-12v58z" fill="{SOL}"/>
  </g>
  <!-- espejo de mano -->
  <g>
    <circle cx="430" cy="286" r="86" fill="{ARENA}" stroke="{ORO}" stroke-width="10"/>
    <circle cx="430" cy="286" r="66" fill="{AGUA_CLARA}" opacity="0.75"/>
    <rect x="418" y="368" width="24" height="70" rx="12" fill="{ORO}"/>
  </g>
  <!-- polvera -->
  <g>
    <circle cx="580" cy="356" r="44" fill="{SOL}" opacity="0.85"/>
    <circle cx="580" cy="356" r="26" fill="{ARENA}" opacity="0.55"/>
    <path d="M556 300c0-14 12-24 24-24s24 10 24 24" fill="none" stroke="{TINTA}" stroke-width="6" opacity="0.5"/>
  </g>
  <circle cx="206" cy="200" r="12" fill="{AGUA}" opacity="0.5"/>
  <circle cx="238" cy="170" r="7" fill="{AGUA}" opacity="0.35"/>'''
    )



def salud() -> str:
    return (
        sombra(400, 400, 168, 22)
        + f'''
  <rect x="286" y="212" width="228" height="176" rx="24" fill="{ARENA}"/>
  <rect x="286" y="212" width="228" height="40" rx="20" fill="{AGUA}" opacity="0.85"/>
  <rect x="356" y="286" width="88" height="28" rx="8" fill="{AGUA}"/>
  <rect x="386" y="256" width="28" height="88" rx="8" fill="{AGUA}"/>
  <path d="M330 212v-24a16 16 0 0 1 16-16h108a16 16 0 0 1 16 16v24" fill="none" stroke="{OCEANO}" stroke-width="12"/>
  <g>
    <rect x="560" y="292" width="60" height="96" rx="12" fill="{SOL}" opacity="0.85"/>
    <rect x="572" y="266" width="36" height="30" rx="6" fill="{OCEANO}"/>
    <rect x="556" y="312" width="68" height="26" fill="{ARENA}" opacity="0.7"/>
  </g>
  <circle cx="240" cy="356" r="26" fill="{AGUA}" opacity="0.35"/>
  <circle cx="212" cy="300" r="15" fill="{AGUA}" opacity="0.25"/>'''
    )


def deporte_y_ocio() -> str:
    return (
        sombra(384, 402, 168, 24)
        + f'''
  <g>
    <circle cx="322" cy="304" r="106" fill="{ARENA}" stroke="{OCEANO}" stroke-width="6"/>
    <path d="M322 262l40 30-15 48h-50l-15-48z" fill="{OCEANO}" opacity="0.85"/>
    <path d="M322 198v64M226 336l64-26M418 336l-64-26M262 200l28 62M382 200l-28 62" stroke="{OCEANO}" stroke-width="6" opacity="0.5" fill="none"/>
  </g>
  <g transform="rotate(14 586 290)">
    <ellipse cx="586" cy="232" rx="62" ry="78" fill="{SOL}" opacity="0.9"/>
    <ellipse cx="586" cy="232" rx="42" ry="56" fill="{SOL_CLARO}" opacity="0.6"/>
    <rect x="574" y="310" width="24" height="90" rx="12" fill="{AGUA}"/>
  </g>
  <circle cx="204" cy="190" r="15" fill="{ORO}" opacity="0.8"/>'''
    )



def hogar_y_reformas() -> str:
    return (
        sombra(400, 404, 176, 22)
        + f'''
  <g transform="rotate(-16 300 300)">
    <rect x="288" y="238" width="26" height="174" rx="12" fill="{ORO}"/>
    <path d="M244 196h120a15 15 0 0 1 0 30h-44v22h-34v-22h-42z" fill="{TINTA}"/>
  </g>
  <g>
    <path d="M452 266h176l-18 146H470z" fill="{AGUA}"/>
    <path d="M452 266h176l-4 32H456z" fill="{OCEANO}" opacity="0.8"/>
    <path d="M482 266c0-38 28-56 58-56s58 18 58 56" fill="none" stroke="{OCEANO}" stroke-width="9" opacity="0.55"/>
    <rect x="500" y="318" width="80" height="14" rx="7" fill="{ARENA}" opacity="0.55"/>
  </g>
  <path d="M300 148c14 18 22 30 22 42a22 22 0 0 1-44 0c0-12 8-24 22-42z" fill="{SOL}" opacity="0.7"/>'''
    )



def electronica() -> str:
    return (
        sombra(400, 402, 176, 22)
        + f'''
  <rect x="252" y="212" width="300" height="188" rx="16" fill="{OCEANO}"/>
  <rect x="268" y="228" width="268" height="140" rx="8" fill="{AGUA}" opacity="0.65"/>
  <path d="M240 400h324l-16 22H256z" fill="{OCEANO}" opacity="0.75"/>
  <g>
    <rect x="576" y="272" width="76" height="132" rx="14" fill="{TINTA}"/>
    <rect x="586" y="286" width="56" height="100" rx="6" fill="{AGUA_CLARA}" opacity="0.85"/>
  </g>
  <rect x="300" y="256" width="60" height="60" rx="8" fill="{SOL}" opacity="0.9"/>
  <path d="M330 316v26h96v-26" fill="none" stroke="{ARENA}" stroke-width="8" opacity="0.6"/>
  <circle cx="196" cy="330" r="18" fill="{ORO}" opacity="0.7"/>'''
    )


def bazares() -> str:
    return (
        sombra(400, 404, 178, 22)
        + f'''
  <!-- bolsa de papel -->
  <g>
    <path d="M286 244h228l-20 158H306z" fill="{SOL}" opacity="0.85"/>
    <path d="M286 244h228l-6 30H292z" fill="{ORO}"/>
    <path d="M336 244c0-34 26-56 64-56s64 22 64 56" fill="none" stroke="{OCEANO}" stroke-width="11" opacity="0.75"/>
  </g>
  <!-- etiqueta colgante -->
  <g transform="rotate(-14 596 300)">
    <rect x="556" y="248" width="84" height="112" rx="12" fill="{ARENA}" stroke="{AGUA}" stroke-width="5"/>
    <circle cx="598" cy="272" r="9" fill="{AGUA}"/>
    <path d="M574 300h48M574 320h34" stroke="{OCEANO}" stroke-width="6" opacity="0.4" stroke-linecap="round"/>
  </g>
  <circle cx="204" cy="212" r="26" fill="{AGUA}" opacity="0.3"/>
  <circle cx="212" cy="330" r="14" fill="{AGUA}" opacity="0.2"/>'''
    )



def motor() -> str:
    return (
        sombra(390, 404, 176, 24)
        + f'''
  <!-- llanta -->
  <g>
    <circle cx="382" cy="312" r="118" fill="{TINTA}"/>
    <circle cx="382" cy="312" r="72" fill="{ARENA}"/>
    <circle cx="382" cy="312" r="30" fill="{OCEANO}"/>
    <g stroke="{AGUA_CLARA}" stroke-width="10" stroke-linecap="round" opacity="0.5">
      <path d="M382 218v34"/><path d="M382 372v34"/>
      <path d="M288 312h34"/><path d="M442 312h34"/>
      <path d="M316 246l24 24"/><path d="M448 246l-24 24"/>
      <path d="M316 378l24-24"/><path d="M448 378l-24-24"/>
    </g>
  </g>
  <!-- carretera -->
  <g stroke="{TINTA}" stroke-width="12" stroke-linecap="round" opacity="0.3">
    <path d="M180 452h58"/><path d="M268 452h58"/><path d="M356 452h58"/><path d="M444 452h58"/><path d="M532 452h58"/>
  </g>
  <!-- tuerca -->
  <g>
    <path d="M604 214l28 16v32l-28 16-28-16v-32z" fill="{SOL}" opacity="0.9"/>
    <circle cx="604" cy="246" r="14" fill="{ARENA}" opacity="0.7"/>
  </g>'''
    )



def mascotas() -> str:
    return (
        sombra(400, 400, 164, 22)
        + f'''
  <g fill="{AGUA}">
    <ellipse cx="400" cy="330" rx="70" ry="58"/>
    <ellipse cx="306" cy="212" rx="30" ry="42" transform="rotate(-18 306 212)"/>
    <ellipse cx="368" cy="176" rx="30" ry="44"/>
    <ellipse cx="432" cy="176" rx="30" ry="44"/>
    <ellipse cx="494" cy="212" rx="30" ry="42" transform="rotate(18 494 212)"/>
  </g>
  <g>
    <ellipse cx="600" cy="368" rx="66" ry="26" fill="{SOL}" opacity="0.85"/>
    <ellipse cx="600" cy="352" rx="52" ry="20" fill="{SOL_CLARO}" opacity="0.7"/>
    <circle cx="588" cy="300" r="12" fill="{ORO}"/>
    <circle cx="620" cy="286" r="10" fill="{ORO}"/>
  </g>
  <circle cx="206" cy="300" r="40" fill="{SOL}" opacity="0.55"/>
  <circle cx="206" cy="300" r="20" fill="{ARENA}" opacity="0.8"/>'''
    )


def servicios() -> str:
    return (
        sombra(400, 402, 170, 22)
        + f'''
  <!-- maletín -->
  <g>
    <rect x="244" y="240" width="248" height="164" rx="18" fill="{OCEANO}"/>
    <rect x="244" y="240" width="248" height="30" rx="15" fill="{AGUA}"/>
    <path d="M332 240v-26a16 16 0 0 1 16-16h40a16 16 0 0 1 16 16v26" fill="none" stroke="{OCEANO}" stroke-width="10"/>
    <rect x="336" y="296" width="108" height="66" rx="8" fill="{ARENA}" opacity="0.92"/>
    <path d="M352 316h76M352 336h52" stroke="{OCEANO}" stroke-width="6" opacity="0.4" stroke-linecap="round"/>
  </g>
  <!-- lupa -->
  <g>
    <circle cx="580" cy="308" r="42" fill="none" stroke="{ORO}" stroke-width="13"/>
    <circle cx="580" cy="308" r="30" fill="{AGUA_CLARA}" opacity="0.5"/>
    <path d="M610 338l40 40" stroke="{ORO}" stroke-width="13" stroke-linecap="round"/>
  </g>'''
    )



def hogar_y_decoracion() -> str:
    return (
        sombra(400, 406, 168, 22)
        + f'''
  <g>
    <path d="M330 264h100l18 120a26 26 0 0 1-26 26h-84a26 26 0 0 1-26-26z" fill="{SOL}" opacity="0.85"/>
    <path d="M324 264h112l-6 28H330z" fill="{ORO}"/>
    <g stroke="{OCEANO}" stroke-width="7" fill="none" stroke-linecap="round">
      <path d="M380 264c0-40-28-56-28-84"/>
      <path d="M380 264c18-30 6-52 24-74"/>
      <path d="M380 264c-8-24-40-32-48-58"/>
    </g>
    <circle cx="352" cy="172" r="13" fill="{AGUA}" opacity="0.65"/>
    <circle cx="404" cy="184" r="10" fill="{SOL}" opacity="0.7"/>
  </g>
  <g>
    <path d="M548 206h100l24 58H524z" fill="{ARENA}"/>
    <path d="M536 264h124l-8 18H544z" fill="{ORO}" opacity="0.6"/>
    <rect x="592" y="282" width="16" height="110" rx="8" fill="{TINTA}" opacity="0.65"/>
    <rect x="556" y="392" width="88" height="14" rx="7" fill="{TINTA}" opacity="0.65"/>
  </g>
  <g>
    <rect x="176" y="206" width="96" height="118" rx="6" fill="{AGUA}" opacity="0.32"/>
    <rect x="190" y="220" width="68" height="90" rx="3" fill="{AGUA_CLARA}" opacity="0.85"/>
  </g>'''
    )



def generico() -> str:
    return (
        sombra(400, 402, 180, 24)
        + f'''
  <path d="M256 236h288v168H256z" fill="{ARENA}"/>
  <path d="M240 236l60-72h200l60 72z" fill="{AGUA}"/>
  <path d="M240 236h320l-18 30H258z" fill="{OCEANO}" opacity="0.85"/>
  <rect x="366" y="300" width="68" height="104" rx="8" fill="{SOL}" opacity="0.85"/>
  <rect x="296" y="288" width="52" height="56" rx="6" fill="{AGUA_CLARA}"/>
  <rect x="452" y="288" width="52" height="56" rx="6" fill="{AGUA_CLARA}"/>
  <path d="M400 164v-56" stroke="{OCEANO}" stroke-width="10" stroke-linecap="round"/>
  <circle cx="400" cy="152" r="14" fill="{ORO}"/>'''
    )


ESCENAS = {
    'restaurantes': restaurantes,
    'bares-y-cafes': bares_y_cafes,
    'alimentacion': alimentacion,
    'moda': moda,
    'belleza': belleza,
    'salud': salud,
    'deporte-y-ocio': deporte_y_ocio,
    'hogar-y-reformas': hogar_y_reformas,
    'electronica': electronica,
    'bazares': bazares,
    'motor': motor,
    'mascotas': mascotas,
    'servicios': servicios,
    'hogar-y-decoracion': hogar_y_decoracion,
    'generico': generico,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--destino', default=None)
    args = ap.parse_args()
    destino = args.destino or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public', 'img', 'categorias'
    )
    os.makedirs(destino, exist_ok=True)
    total = 0
    for slug, escena in ESCENAS.items():
        svg = lienzo(slug, escena())
        ruta = os.path.join(destino, f'{slug}.svg')
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(svg)
        total += len(svg.encode())
        print(f'{ruta}  {len(svg.encode()) / 1024:.1f} KB')
    print(f'\n{len(ESCENAS)} imágenes · {total / 1024:.1f} KB en total')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
