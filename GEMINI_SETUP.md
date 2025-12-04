# Guía: Configurar Gemini con Cookies Manuales

## Problema Actual
- `browser_cookie3` no puede leer cookies de Chrome en Windows
- Solución: Configurar cookies manualmente

## Pasos para Obtener Cookies

### 1. Abrir DevTools en Gemini
1. Ve a https://gemini.google.com (ya estás ahí)
2. Presiona **F12** (o Ctrl+Shift+I)
3. Ve a la pestaña **"Application"**

### 2. Encontrar las Cookies
1. En el panel izquierdo, expande **"Cookies"**
2. Haz clic en **"https://gemini.google.com"**
3. Busca estas cookies:
   - `__Secure-1PSID`
   - `__Secure-1PSIDTS`

### 3. Copiar los Valores
- Haz clic en cada cookie
- Copia el valor completo (columna "Value")
- Los valores son largos (varios caracteres)

## Configuración en .env

Una vez que tengas los valores, edita el archivo `.env`:

```env
# Gemini Cookies (obtenidas manualmente)
GEMINI_COOKIE_1PSID=tu_valor_de_1PSID_aqui
GEMINI_COOKIE_1PSIDTS=tu_valor_de_1PSIDTS_aqui
```

## Reiniciar el Servidor

Después de configurar las cookies:

1. Detén el servidor actual (Ctrl+C)
2. Reinicia: `python src/run.py`
3. El servidor debería iniciar en modo WebAI (Gemini)

## Verificación

Si las cookies son correctas:
- ✅ El servidor dirá: "WebAI-to-API mode is available"
- ✅ Iniciará en modo WebAI (más rápido que g4f)
- ✅ Podrás usar los modelos de Gemini directamente

## Notas Importantes

- Las cookies expiran periódicamente (cada 12-24 horas)
- El sistema de auto-renovación está implementado pero requiere acceso al navegador
- Si el servidor falla al iniciar, las cookies probablemente expiraron
- Simplemente repite el proceso para obtener nuevas cookies

## Alternativa: Usar g4f

Si prefieres no configurar cookies manualmente:
- El servidor ya funciona con g4f
- Tiene acceso a múltiples modelos
- No requiere cookies
- Actualmente está corriendo en este modo
