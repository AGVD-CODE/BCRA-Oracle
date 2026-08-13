# Cómo publicar este proyecto en GitHub

Guía paso a paso para subir este repositorio a GitHub por primera vez. No hace falta experiencia previa.

## Antes de empezar

Necesitás:
- Una cuenta de GitHub (gratis, en https://github.com).
- Git instalado en tu computadora. Para verificar, abrí una terminal y escribí `git --version`. Si no lo tenés, descargalo de https://git-scm.com.

## Opción A — Con la interfaz web de GitHub (la más simple)

1. Entrá a https://github.com y hacé clic en **New repository** (botón verde).
2. Poné el nombre: `Oraculo-sistema_financiero`.
3. Agregá la descripción: *"Skill de Claude que responde preguntas sobre el sistema financiero argentino consultando fuentes oficiales del BCRA e INDEC."*
4. Elegí **Public** (para que sea visible).
5. **No** marques "Add a README" ni "Add .gitignore" ni "Choose a license" — ya los tenés en los archivos.
6. Hacé clic en **Create repository**.
7. En la página que aparece, buscá el enlace **uploading an existing file** (o arrastrá los archivos).
8. Arrastrá todo el contenido de la carpeta `Oraculo-sistema_financiero` (el README, LICENSE, la carpeta skill, docs, y el archivo .skill).
9. Escribí un mensaje como *"Primer commit"* y hacé clic en **Commit changes**.

Listo. Tu proyecto está publicado.

## Opción B — Con la terminal (más estándar)

Desde la carpeta del proyecto:

```bash
# 1. Inicializar el repositorio
git init

# 2. Agregar todos los archivos
git add .

# 3. Primer commit
git commit -m "Primer commit: oráculo del sistema financiero argentino"

# 4. Conectar con el repositorio remoto que creaste en GitHub
#    (reemplazá TU-USUARIO por tu nombre de usuario de GitHub)
git remote add origin https://github.com/TU-USUARIO/Oraculo-sistema_financiero.git

# 5. Subir
git branch -M main
git push -u origin main
```

La primera vez te va a pedir autenticarte con GitHub (usuario y un token de acceso, que se genera en Settings → Developer settings → Personal access tokens).

## Después de publicar

- Tu repo va a estar en `https://github.com/TU-USUARIO/Oraculo-sistema_financiero`.
- La gente va a poder descargar el archivo `bcra-oraculo.skill` desde ahí e instalarlo en su Claude.
- Podés editar el README directamente en GitHub si querés mejorarlo.

## Actualizar el proyecto más adelante

Cuando hagas cambios (por ejemplo, mejorás un extractor), para subirlos:

```bash
git add .
git commit -m "Descripción del cambio"
git push
```

## Consejo

En GitHub, el README.md se muestra automáticamente en la portada del repositorio. Es lo primero que ve cualquiera que llegue, así que ya está escrito para explicar bien qué hace el proyecto y cómo usarlo.
