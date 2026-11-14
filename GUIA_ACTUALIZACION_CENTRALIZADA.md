# SUNARP 2026 — actualización centralizada

El aplicativo público sigue disponible en:
https://abastecimiento012-rgb.github.io/sunarp-seguimiento-2026/

## Qué cambia

- Todas las personas consultan el mismo archivo **datos.json** publicado en el repositorio.
- Al abrir la web, cuando se vuelve a la pestaña o cada 3 minutos, se comprueba la última versión. También hay un botón **Recargar información**.
- Los visitantes **no pueden actualizar los datos** desde la página pública.
- El archivo Excel de trabajo permanece en tu computadora; **no se sube al repositorio**.
- La actualización de datos se realiza con tu propia sesión de GitHub, usando GitHub CLI. **No copies claves, tokens ni contraseñas a la web.**

## Primera configuración (solo una vez, en tu computadora Windows)

1. Descarga una copia del repositorio desde GitHub: **Code → Download ZIP**, y descomprímela en una carpeta permanente. Conserva los archivos `ACTUALIZAR_SUNARP.cmd` y `scripts/publicar_desde_excel.py` juntos.
2. Ten instalado **Python 3** (el archivo .cmd instala `openpyxl` si lo necesita).
3. Instala **GitHub CLI** desde https://cli.github.com/ .
4. Abre `ACTUALIZAR_SUNARP.cmd`; si no tienes sesión iniciada, se abrirá el inicio de sesión de GitHub. Usa **tu cuenta con permiso de escritura** en `abastecimiento012-rgb/sunarp-seguimiento-2026`.
5. Selecciona tu Excel actualizado, comprueba la cantidad de registros y confirma con **s**.

## Cada actualización posterior

1. Guarda los cambios en el Excel habitual.
2. Abre `ACTUALIZAR_SUNARP.cmd`.
3. Selecciona el archivo Excel.
4. Revisa la cantidad de registros y responde **s** para publicarlos.
5. Abre el enlace del aplicativo y pulsa **Recargar información**. Tu jefa y los especialistas podrán consultar la misma versión al recargarla o automáticamente.

El archivo Excel debe conservar el formato del control: **primera hoja**, encabezado DESCRIPCIÓN en **C5**, registros desde la **fila 6**, y columnas B a BF según la plantilla actual. El publicador realiza verificaciones y bloquea la publicación si encuentra menos de 10 registros, identificadores vacíos o repetidos.

## Seguimiento operativo (mejora compacta y opcional)

El aplicativo conserva las mismas pestañas. En **Procedimientos** se muestran la etapa, el responsable, la próxima actuación y una única alerta; en **Alertas y plazos**, se despliegan los pendientes por especialista. Las fichas muestran solo la última actuación documentada, no un historial duplicado.

Para usar estos datos de seguimiento, agrega **cuatro columnas opcionales después de BF**, sin alterar las columnas originales. Coloca los siguientes encabezados en la **fila 5**:

| Columna | Encabezado exacto | Uso |
| --- | --- | --- |
| **BG5** | PRÓXIMA ACTUACIÓN | Acción específica pendiente, por ejemplo «Solicitar subsanación de TDR» |
| **BH5** | FECHA DE COMPROMISO | Fecha interna completa, por ejemplo «18.11.2026» |
| **BI5** | ÚLTIMA ACTUACIÓN | Breve descripción de la última actuación realizada |
| **BJ5** | FECHA ÚLTIMA ACTUACIÓN | Fecha de esa actuación, por ejemplo «13.11.2026» |

Las cuatro columnas son **opcionales**: si no existen, la actualización sigue funcionando y la página señala «Por precisar» cuando corresponde, sin inventar tareas. El publicador solo utiliza una columna adicional si reconoce su encabezado; admite encabezados con tilde y sin tilde.

**Importante:** la fecha de compromiso es un objetivo interno de seguimiento. No equivale a un plazo legal y nunca debe presentarse como incumplimiento normativo automático. El indicador «sin actualización» se calcula solo si se registró una fecha válida en BJ.

La versión pública muestra un único hito principal por pendiente y oculta los hitos adicionales dentro de un desplegable. El archivo original sigue bajo tu control.

## Seguridad y límites

La página estática de GitHub Pages es **solo de consulta**; no hay edición remota desde el navegador. La autoridad para cambiar `datos.json` corresponde a quien tiene permisos sobre el repositorio GitHub. Si otras personas poseen permisos de escritura en ese repositorio, también podrían modificarlo: revisa **Settings → Collaborators**.

El repositorio y el JSON son públicos porque el sitio de consulta es público. **No publiques datos personales, información reservada ni documentos sensibles**. El publicador excluye del JSON nuevo detalles de pagos, saldos, primeros devengados y adelantos; antes de publicar, revisa que los demás campos sean aptos para consulta pública.

La versión compartida requiere acceso a Internet. Si no es posible comprobar la fuente central, el aplicativo mostrará una advertencia en lugar de sustituirla por datos guardados localmente.

## Solución de problemas

- **No encuentro GitHub CLI:** instálalo desde https://cli.github.com/ y vuelve a abrir el .cmd.
- **Error de autenticación:** abre una terminal y ejecuta `gh auth login`.
- **Error 403 al publicar:** verifica que tu cuenta tenga permiso de escritura sobre el repositorio y que hayas completado el inicio de sesión.
- **Excel no reconocido:** revisa C5 y la estructura de columnas; no cambies la primera hoja de la plantilla.
- **La web muestra una versión antigua:** pulsa **Recargar información** y comprueba la conexión; las nuevas publicaciones pueden tardar algo en distribuirse por la red.
