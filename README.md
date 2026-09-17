# San Martín Industria

Sitio estático del informe «San Martín: la capital que dejó de cuidar su industria».
Se recuperó la versión pública de Vercel el 17 de septiembre de 2026 para inicializar este repositorio, que estaba vacío.

## Desarrollo y publicación

Requiere Node.js 22.12 o superior.

```sh
npm ci
npm run dev
npm run build
```

Vercel debe usar la rama `main`, ejecutar `npm run build` y publicar `dist` (configurado en `vercel.json`). Los textos de `public/content` conservan sus rutas públicas `/content/*.txt`.

## Fuentes

La sección `#fuentes` contiene Documentos, Sitios oficiales, Otros enlaces y Normativa. Los 12 archivos de Drive se identifican en `sources-documents.json`; sus enlaces de apertura y descarga están renderizados directamente en el HTML. No se modifica la configuración de acceso de Drive.

Las referencias normativas distinguen los textos legales de las páginas municipales que explican los regímenes. Para Tres de Febrero y San Miguel, algunas tarjetas enlazan información oficial de aplicación; no se han localizado todos los textos normativos individuales. Las ordenanzas de Morón corresponden al ejercicio 2024, tal como en el informe.

## Verificación de esta actualización

- Compilación de producción correcta; cuatro grupos, 12 archivos y 12 accesos de descarga; sin IDs duplicados.
- Los 12 archivos de Drive abren sin autenticación y sus descargas devuelven contenido PDF/JPG.
- Las fuentes de San Martín, Morón, San Miguel, PBA, INDEC, UBA y las entidades empresariales respondieron correctamente. UNSAM, INTI y Ley 27.110 fueron comprobados mediante lectura web; algunos rechazan solicitudes automatizadas directas.
- Los enlaces oficiales de Tres de Febrero fueron localizados en búsqueda, pero devolvieron HTTP 502 al verificarlos desde este entorno.
- La revisión visual en navegador quedó bloqueada por el acceso del navegador al servidor de prueba. No se afirma una verificación visual completa de móvil ni de ambos temas.
- La conexión de Vercel no lista el proyecto y devuelve 404 al consultarlo; el estado del deployment de producción debe confirmarse cuando vuelva a estar disponible ese acceso.
