export default async function handler(request, response) {
  if (request.method !== 'POST') {
    response.setHeader('Allow', 'POST');
    return response.status(405).json({ error: 'Método no permitido' });
  }

  const { name, email, website } = request.body || {};
  if (website) return response.status(200).json({ ok: true });
  if (typeof name !== 'string' || !name.trim() || name.length > 120 ||
      typeof email !== 'string' || email.length > 254 ||
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return response.status(400).json({ error: 'Revisá el nombre y el correo electrónico.' });
  }

  const apiKey = process.env.RESEND_API_KEY;
  const from = process.env.RESEND_FROM_EMAIL;
  const recipient = process.env.SUBSCRIPTION_RECIPIENT_EMAIL;
  if (!apiKey || !from || !recipient) {
    console.error('Subscription email is not configured');
    return response.status(503).json({ error: 'El envío no está disponible en este momento.' });
  }

  try {
    const sent = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from,
        to: [recipient],
        reply_to: email.trim(),
        subject: 'Nueva suscripción — ACEP San Martín',
        text: `Nueva suscripción para recibir novedades de ACEP San Martín.\n\nNombre y Apellido: ${name.trim()}\nCorreo electrónico: ${email.trim()}`
      })
    });
    if (!sent.ok) {
      console.error('Subscription email provider failed', sent.status);
      return response.status(502).json({ error: 'No se pudo enviar la suscripción.' });
    }
    return response.status(200).json({ ok: true });
  } catch (error) {
    console.error('Subscription email request failed', error);
    return response.status(502).json({ error: 'No se pudo enviar la suscripción.' });
  }
}
