// Lista slim de comercios para pintar en cliente las tarjetas que no caben
// en el HTML inicial de la portada. Solo los campos que usa la tarjeta.
import comercios from '../data/comercios.json';

export function GET() {
  const slim = comercios.map((c) => ({
    slug: c.slug,
    nombre: c.nombre,
    categoria: c.categoria,
    calle: c.calle,
    telefono: c.telefono || '',
    foto: c.fotos?.[0] || '',
  }));
  return Response.json(slim);
}
