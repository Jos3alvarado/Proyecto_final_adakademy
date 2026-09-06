# Cuentas Claras 🎯 - Erradicando la Amnesia Financiera Estudiantil

**Cuentas Claras** es una plataforma web en **Django** para llevar un control divertido, transparente y visual de las deudas pequeñas entre compañeros de clase, amigos y colegas. Estética **dark premium / glassmorphism** moderna con monetización **Freemium + Stripe**.

---

## ✨ Características

*   📁 **El Tablón** (`/tablon/`): Dashboard responsivo en tarjetas de cristal (glassmorphism).
*   🍿 **Tres tipos de historias** con pestañas: **Chismes**, **Cuentas entre Panas** y **Deudas Serias**.
*   📸 **Evidencias Físicas**: Adjunta capturas, fotos o memes como prueba de la deuda.
*   🔒 **Regla de Oro**: Solo el acreedor original puede marcar como pagada o eliminar su deuda. Terceros reciben **403 Forbidden**.
*   💳 **Pagos con Stripe**: Suscripción mensual/anual, webhooks, gestión de clientes.
*   📣 **Compartir**: Botones de WhatsApp / X / Facebook y copiar enlace en cada historia.
*   🔍 **SEO / OpenGraph**: Meta tags para que los enlaces compartidos se vean atractivos.
*   🎨 **Estética Dark Premium**: Glassmorphism, gradientes, animaciones fluidas, tipografía Plus Jakarta Sans.

---

## 🛠️ Stack

*   **Backend**: Django 5.0.6 (Python 3)
*   **Base de Datos**: SQLite3 (dev) / PostgreSQL (prod)
*   **Imágenes**: Pillow
*   **Frontend**: HTML5, Custom CSS (style.css), Tailwind + DaisyUI (CDN)
*   **Pagos**: Stripe
*   **Servidor Prod**: gunicorn + whitenoise

---

## 🚀 Instalación y Uso Local

```bash
python -m venv .venv
.\.venv\Scripts\activate        # Windows
source .venv/bin/activate       # macOS/Linux

pip install -r requirements.txt

# 1. Configura tus claves (Stripe, secret key)
cp .env.example .env            # luego edita .env con valores reales

# 2. Migraciones + datos de ejemplo
python manage.py migrate
python manage.py setup_categories   # crea las 12 categorías
python manage.py seed_debts         # datos de prueba graciosos (opcional)

# 3. Crea un superusuario (para /admin/)
python manage.py createsuperuser

# 4. Corre el servidor
python manage.py runserver
```

Visita `http://127.0.0.1:8000/`.

> **Nota:** el archivo `.env` está en `.gitignore` (nunca se sube a GitHub). Las variables también pueden definirse en el panel del host (Render/Railway) si no quieres usar archivo local.

---

## 💳 Configuración de Stripe (imprescindible para cobrar)

1. Crea una cuenta en [stripe.com](https://stripe.com).
2. **Developers → API keys**: copia la clave pública (`pk_test_...`) y secreta (`sk_test_...`) al `.env`.
3. **Productos → Añadir precio** (tipo *Subscription*/Periódico):
   - **Premium Mensual** → $9.99/mes
   - **Premium Anual** → $99.99/año
   Copia los IDs (`price_...`) al `.env` en `STRIPE_PRICE_ID_PREMIUM_MONTHLY` y `STRIPE_PRICE_ID_PREMIUM_YEARLY`.
4. **Developers → Webhooks**: añade un endpoint apuntando a `https://TU-DOMINIO/stripe/webhook/` y suscríbete a:
   - `checkout.session.completed`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   Copia el **Signing secret** (`whsec_...`) al `.env`.
5. Para pruebas usa la tarjeta de test de Stripe: `4242 4242 4242 4242`, cualquier fecha futura, CVC cualquiera.

Variables de entorno usadas:

| Variable | Descripción |
|---|---|
| `DJANGO_SECRET_KEY` | Clave secreta de Django |
| `DJANGO_DEBUG` | `True` en dev, `False` en producción |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos separados por coma |
| `DATABASE_URL` | URL de PostgreSQL (Render la provee; local se usa SQLite) |
| `STRIPE_PUBLIC_KEY` | Clave pública de Stripe |
| `STRIPE_SECRET_KEY` | Clave secreta de Stripe |
| `STRIPE_WEBHOOK_SECRET` | Signing secret del webhook |
| `STRIPE_PRICE_ID_PREMIUM_MONTHLY` | ID del precio mensual |
| `STRIPE_PRICE_ID_PREMIUM_YEARLY` | ID del precio anual |

---

## 💰 Estrategia de Monetización (Freemium)

| Plan | Precio | Incluye |
|---|---|---|
| **Gratis** | $0 | 3 publicaciones, chismes, evidencia con foto |
| **Pro Mensual** | $9.99/mes | Publicaciones ilimitadas, todos los tipos, contenido premium |
| **Pro Anual** | $99.99/año | Igual que Pro Mensual (2 meses gratis) |

**Flujo de cobro:**
1. Un usuario gratuito publica hasta 3 historias.
2. Al intentar crear la 4ª se le redirige a `/precios/`.
3. Desde `/precios/` elige plan y paga vía Stripe Checkout.
4. El webhook/`payment_success` activa `subscription_type = premium` con fecha de expiración.

---

## 🧪 Pruebas Unitarias

```bash
python manage.py test
```

---

## 🚀 Deploy (Activar la página en línea)

La app está lista para **Render.com** o **Railway.app**. Ya incluye `Procfile`, `render.yaml`, `requirements.txt` con gunicorn + whitenoise.

### Pasos con Render (seguir `render.yaml`):

1. **Sube el proyecto a GitHub** (ya incluye `render.yaml`).
2. Crea cuenta en [render.com](https://render.com) → **New → Blueprint** (o *New → Web Service* conectando el repo).
3. Render detectará `render.yaml` y creará automáticamente: el **Web Service** (`cuentas-claras`) y la **base de datos PostgreSQL** (`cuentas-claras-db`) gratis.
4. Render ejecuta el build:
   ```
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py setup_categories
   python manage.py collectstatic --noinput
   ```
5. **Reemplaza los placeholders de Stripe** en las variables del panel (Environment):
   `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID_PREMIUM_MONTHLY`, `STRIPE_PRICE_ID_PREMIUM_YEARLY`.
6. Espera a que `Deploy` muestre `Live`. Tendrás una URL tipo `https://cuentas-claras.onrender.com`.
7. Ve a `DJANGO_ALLOWED_HOSTS` y añade tu dominio si usas uno propio.
8. Crea el superusuario/admin con el shell de Render o localmente (ver abajo).
9. **Webhook de Stripe**: crea el webhook en Stripe apuntando a `https://TU-DOMINIO/stripe/webhook/` con los eventos indicados arriba, y copia el nuevo `whsec_...` al panel.
10. **Modo LIVE**: cuando estés listo para cobrar de verdad, activa las claves *live* en Stripe y repite los pasos 5 y 9 con los valores live.

> **Importante**: el plan Free de Render pausa los servicios tras 15 min de inactividad y tarda unos segundos en volver al recibir el primer request. Para uso continuo usa el plan Starter (~$7/mes) o un host como Railway.

---

## ⚖️ Licencia

Desarrollado con fines educativos en el curso de **Adakademy**. ¡Prohibido comerse la malta del compañero sin pagársela! 🕊️
