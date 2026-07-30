// Datos de contacto del sitio. Cambiar aquí y se actualiza en todas las páginas.
export const contacto = {
  // wa.me exige el número sin "+", sin espacios y sin guiones
  whatsapp: '34633505153',
  whatsappVisible: '+34 633 50 51 53',
  email: 'hola@zonaalcaravaneras.com',
};

// Enlace de WhatsApp con mensaje ya escrito, para que al comerciante
// solo le quede darle a enviar.
export function enlaceWhatsapp(mensaje) {
  const base = `https://wa.me/${contacto.whatsapp}`;
  return mensaje ? `${base}?text=${encodeURIComponent(mensaje)}` : base;
}
