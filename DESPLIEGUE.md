# Desplegar zonaalcaravaneras.com

Sitio Astro estático. Repositorio: `Chytzo/zonaalcaravaneras` (privado).

## Antes de publicar — obligatorio

Marcadores `[pendiente]` que hay que rellenar (LSSI, Ley 34/2002):

- `src/pages/aviso-legal.astro` → nombre, NIF y domicilio del titular
- `src/pages/privacidad.astro` → responsable del tratamiento

```bash
grep -rn "pendiente" src/pages/aviso-legal.astro src/pages/privacidad.astro
```

Importa más que en impulcan.com: aquí se publican datos de 327 negocios ajenos, así
que el titular tiene que estar identificado y la vía para pedir la retirada de una
ficha tiene que funcionar de verdad.

## Conectar Cloudflare Pages

1. Panel → **Workers & Pages** → *Create* → **Pages** → *Connect to Git*.
2. Repositorio `Chytzo/zonaalcaravaneras`.
3. Build: preset **Astro**, comando `npm run build`, salida `dist`, rama `main`.
4. *Custom domains* → `zonaalcaravaneras.com` y `www`.

### Redirección del `.es`

Los registros DNS del `.es` ya apuntan a `192.0.2.1` y `100::` con proxy activado,
para que el tráfico entre en el edge de Cloudflare. Falta la regla, que hay que crear
a mano en el panel porque el token disponible solo tiene permiso de DNS:

Zona `zonaalcaravaneras.es` → **Rules** → **Redirect Rules** → *Create rule*

- Si `Hostname` **contains** `zonaalcaravaneras.es`
- Then: **Dynamic redirect**, código **301**
- Expresión: `concat("https://zonaalcaravaneras.com", http.request.uri.path)`
- Marcar **Preserve query string**

## Regenerar los datos del barrio

El plano y las fichas salen de OpenStreetMap. Para actualizar o para crear la web de
otra zona comercial:

```bash
python3 herramientas/generar-zona.py   # plano + fichas
python3 herramientas/generar-llms.py   # llms.txt
npm run build
```

Para otra zona, editar el bloque `ZONA` al principio de `generar-zona.py` (nombre y
límites sur/norte/oeste/este). El resto es genérico.

Nota: el script lee los volcados de Overpass del directorio temporal de la sesión en
que se generaron. Para una zona nueva hay que volver a descargarlos (edificios, vías,
zonas verdes y negocios del bbox). El mirror `overpass-api.de` suele dar timeout;
funcionan mejor `overpass.private.coffee` y `overpass.kumi.systems`.

## Lo que falta de contenido

| Dato | Estado |
|---|---|
| Comercios | 327 |
| Con teléfono | 7 |
| Con horario | 10 |
| Con foto | 0 |

Los teléfonos y las fotos no están en datos abiertos: se recogen a pie de calle.
La página interna `/ruta` lista los 327 agrupados por calle y ordenados de más a
menos densa, con lo que falta en cada uno. Está en `noindex` y fuera del sitemap.

No se usan fotos de Google Maps, Street View ni de webs de los comercios: son de sus
titulares. Solo fotos propias, cedidas por el negocio o con licencia libre acreditada.

## Atribuciones obligatorias

- Datos y geometría del plano: **OpenStreetMap**, licencia ODbL. Ya citado en el pie
  y en `/creditos`.
- Foto de portada: Bengt Nyman, **CC BY-SA 4.0**, vía Wikimedia Commons. La licencia
  exige la atribución: no quitarla.
