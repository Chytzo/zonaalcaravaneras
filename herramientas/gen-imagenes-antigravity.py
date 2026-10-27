#!/usr/bin/env python3
"""Genera las 15 ilustraciones de categoría encargándoselas al trabajador Antigravity.

Estrategia: Hermes no llama a ningún proveedor de imagen. Escribe un encargo por
categoría, se lo pasa a `~/.hermes/workers/antigravity/worker.py` y Antigravity lo
ejecuta con sus propios modelos (y su generador de imágenes). Después normaliza:
recorte a 16:10, 800×500, JPG calidad 82 en `public/img/categorias/<slug>.jpg`.

Uso:
    python3 herramientas/gen-imagenes-antigravity.py            # solo las que falten
    python3 herramientas/gen-imagenes-antigravity.py --todas     # regenera todo
    python3 herramientas/gen-imagenes-antigravity.py --solo moda bares-y-cafes
    python3 herramientas/gen-imagenes-antigravity.py --model claude-sonnet-4-6
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

WORKER = Path.home() / ".hermes/workers/antigravity/worker.py"

ESTILO = """ESTILO (obligatorio, forma parte de una familia de 15 ilustraciones idénticas en estilo):
- Ilustración editorial plana y geométrica, sin contornos gruesos, sombras planas alargadas hacia abajo-derecha.
- Paleta ESTRICTA, sin añadir otros colores: azul océano #073b4f, azul atlántico #1b7f9e, crema #faf6ee,
  terracota #e2683f, mostaza #d4a017.
- Fondo crema liso con degradado muy suave. Nada de texturas fotográficas ni degradados complejos.
- Sin texto, sin letras, sin logotipos, sin marcas de agua, sin personas ni caras.
- Composición horizontal 16:10, objetos centrados, bastante aire alrededor."""

CATEGORIAS = {
    "restaurantes": "una mesa puesta vista desde arriba: plato, tenedor, cuchillo y copa de vino",
    "bares-y-cafes": "una taza de café humeante con plato y unos granos de café al lado",
    "alimentacion": "una cesta de la compra con una barra de pan, una manzana y una botella de leche",
    "moda": "una camiseta doblada, una bolsa de compras y un espejo de mano",
    "belleza": "un pintalabios abierto, un espejo redondo de mano y una polvera",
    "salud": "un botiquín cerrado con una cruz, un frasco de medicinas y un estetoscopio",
    "deporte-y-ocio": "un balón, una raqueta de tenis y unas zapatillas deportivas",
    "hogar-y-reformas": "un martillo cruzado con un destornillador y un cubo de pintura con brocha",
    "electronica": "un portátil abierto, un teléfono móvil y unos auriculares",
    "bazares": "una bolsa de papel con asas, un cubo de plástico apilable y un recogedor con escoba",
    "motor": "una rueda de coche con llanta, una llave de tuercas y un semáforo pequeño",
    "mascotas": "un cuenco de comida para animales, una huella de pata y un hueso de juguete",
    "servicios": "un maletín de trabajo abierto con documentos y una lupa",
    "hogar-y-decoracion": "un jarrón con ramas, un cuadro enmarcado y una lámpara de pie",
    "generico": "una casa sencilla de frente con puerta y ventanas",
}


def encargo(slug: str, asunto: str) -> str:
    return f"""Genera UNA imagen de ilustración para la categoría «{slug}» de un directorio de comercios de barrio.

SUJETO: {asunto}. Debe reconocerse de un vistazo como esa categoría, sin necesidad de leer nada.

{ESTILO}

RUTA DE SALIDA OBLIGATORIA: guarda el resultado como {slug}.jpg en el directorio de trabajo actual.
Cuando termines, responde solo con la ruta del archivo generado."""


def normalizar(origen: Path, destino: Path) -> bool:
    """Recorta a 16:10, reescala a 800×500 y guarda JPG optimizado."""
    try:
        from PIL import Image
    except ImportError:
        # sin Pillow: copiar tal cual y avisar
        destino.write_bytes(origen.read_bytes())
        print(f"  ! Pillow no disponible: copiado sin normalizar → {destino}")
        return True
    with Image.open(origen) as im:
        im = im.convert("RGB")
        w, h = im.size
        objetivo = 16 / 10
        if w / h > objetivo:
            nuevo_w = int(h * objetivo)
            izq = (w - nuevo_w) // 2
            im = im.crop((izq, 0, izq + nuevo_w, h))
        else:
            nuevo_h = int(w / objetivo)
            arriba = (h - nuevo_h) // 2
            im = im.crop((0, arriba, w, arriba + nuevo_h))
        im = im.resize((800, 500), Image.LANCZOS)
        destino.parent.mkdir(parents=True, exist_ok=True)
        im.save(destino, "JPEG", quality=82, optimize=True, progressive=True)
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", nargs="*", help="slugs concretos")
    ap.add_argument("--todas", action="store_true", help="regenera aunque ya existan")
    ap.add_argument("--model", default="gemini-3.8-flash-high")
    ap.add_argument("--timeout", default="12m", help="límite por imagen en agy --print-timeout")
    ap.add_argument("--destino", default=None)
    args = ap.parse_args()

    base = Path(__file__).resolve().parent.parent
    destino_dir = Path(args.destino) if args.destino else base / "public/img/categorias"
    objetivos = args.solo or list(CATEGORIAS)
    pendientes = [
        s for s in objetivos
        if args.todas or not (destino_dir / f"{s}.jpg").exists()
    ]
    if not pendientes:
        print("nada que generar: todas las imágenes ya existen (usa --todas para rehacerlas)")
        return 0
    print(f"{len(pendientes)} categorías a generar con Antigravity ({args.model})\n")

    fallos = []
    for slug in pendientes:
        asunto = CATEGORIAS[slug]
        with tempfile.TemporaryDirectory(prefix=f"agy-{slug}-") as tmp:
            r = subprocess.run(
                [sys.executable, str(WORKER),
                 "--prompt", encargo(slug, asunto),
                 "--out-dir", tmp, "--model", args.model, "--timeout", args.timeout, "--json"],
                capture_output=True, text=True, timeout=900,
            )
            try:
                res = json.loads(r.stdout)
            except Exception:
                res = {"ok": False, "respuesta": (r.stdout + r.stderr)[-800:]}
            print(f"[{slug}] ok={res.get('ok')} {res.get('segundos','?')}s "
                  f"ficheros={len(res.get('ficheros') or [])}", flush=True)
            if not res.get("ficheros"):
                print("   fallo:", (res.get("respuesta") or "")[-300:].replace("\n", " "))
                fallos.append(slug)
                continue
            origen = Path(res["ficheros"][0])
            # Antigravity a veces deja también scripts y __pycache__; coger la primera imagen real
            imagen = None
            for f in map(Path, res["ficheros"]):
                if f.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
                    continue
                try:
                    from PIL import Image as _Im
                    with _Im.open(f) as _im:
                        _im.verify()
                    imagen = f
                    break
                except Exception:
                    continue
            if imagen is None:
                print("   fallo: ningún fichero de imagen válido entre los generados", flush=True)
                fallos.append(slug)
                continue
            normalizar(imagen, destino_dir / f"{slug}.jpg")
            print(f"   → {destino_dir / (slug + '.jpg')}", flush=True)

    print()
    if fallos:
        print("sin generar:", ", ".join(fallos))
        return 1
    print("todas generadas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
