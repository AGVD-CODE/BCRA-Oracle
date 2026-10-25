# Cómo publicar este proyecto en GitHub

Guía paso a paso para subir este repositorio a GitHub por primera vez y para publicar versiones nuevas. No hace falta experiencia previa.

El proyecto ya está publicado en https://github.com/AGVD-CODE/BCRA-Oracle. Las dos primeras opciones sirven para crear una copia propia desde cero; para publicar cambios, ir a [Publicar una versión nueva](#publicar-una-versión-nueva).

## Antes de empezar

Necesitás:
- Una cuenta de GitHub (gratis, en https://github.com).
- Git instalado en tu computadora. Para verificar, abrí una terminal y escribí `git --version`. Si no lo tenés, descargalo de https://git-scm.com.
- Para publicar versiones desde la terminal, la herramienta `gh` de GitHub (https://cli.github.com), con la sesión iniciada (`gh auth login`).

## Opción A — Con la interfaz web de GitHub (la más simple)

1. Entrá a https://github.com y hacé clic en **New repository** (botón verde).
2. Poné el nombre: `BCRA-Oracle`.
3. Agregá la descripción: *"Skill de Claude que responde preguntas sobre el sistema financiero argentino consultando fuentes oficiales del BCRA e INDEC."*
4. Elegí **Public** (para que sea visible).
5. **No** marques "Add a README" ni "Add .gitignore" ni "Choose a license" — ya los tenés en los archivos.
6. Hacé clic en **Create repository**.
7. En la página que aparece, buscá el enlace **uploading an existing file** (o arrastrá los archivos).
8. Arrastrá todo el contenido de la carpeta `BCRA-Oracle`: el README, el CHANGELOG, LICENSE, `.gitignore`, las carpetas `skill`, `tools` y `docs`, y los dos archivos `.skill`.
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
git remote add origin https://github.com/TU-USUARIO/BCRA-Oracle.git

# 5. Subir
git branch -M main
git push -u origin main
```

La primera vez te va a pedir autenticarte con GitHub (usuario y un token de acceso, que se genera en Settings → Developer settings → Personal access tokens). Si usás `gh`, `gh auth login` lo resuelve.

## Después de publicar

- Tu repo va a estar en `https://github.com/TU-USUARIO/BCRA-Oracle`.
- La gente va a poder descargar `bcra-oraculo.skill` (español) o `bcra-oracle-en.skill` (inglés) desde ahí, o desde la página de cada release, e instalarlo en su Claude.
- Podés editar el README directamente en GitHub si querés mejorarlo.

## Publicar una versión nueva

Cada versión publicada tiene un número (`2.0.1`, `2.1.0`, `3.0.0`) que sigue la política de [`CONTRATO.md`](CONTRATO.md), sección 6: si cambia una firma de `bcra_comun.py` o una clave de campo, sube la versión mayor.

### 1. Hacer el cambio en una rama

```bash
git checkout -b nombre-del-cambio
```

- Los scripts se editan en `skill/bcra-oraculo/scripts/` y se copian iguales a `skill/bcra-oracle-en/scripts/`: son los mismos en los dos idiomas.
- Si cambia `bcra_comun.py`, actualizá `VERSION` en los dos idiomas.
- Anotá el cambio en `CHANGELOG.md`, bajo el número de la versión nueva.

### 2. Verificar

```bash
python3 tools/verificar.py
```

Tiene que terminar con `0 FALLA`. Necesita red y `pdftotext` (`brew install poppler` en macOS).

### 3. Regenerar los paquetes

Con el script del skill **skill-creator** (necesita PyYAML), desde su carpeta:

```bash
python3 -m scripts.package_skill /ruta/a/BCRA-Oracle/skill/bcra-oraculo /ruta/a/BCRA-Oracle
python3 -m scripts.package_skill /ruta/a/BCRA-Oracle/skill/bcra-oracle-en /ruta/a/BCRA-Oracle
```

Sin skill-creator, desde la carpeta `skill/` del repositorio:

```bash
rm -f ../bcra-oraculo.skill ../bcra-oracle-en.skill
zip -r -D ../bcra-oraculo.skill bcra-oraculo -x '*__pycache__*' '*.DS_Store'
zip -r -D ../bcra-oracle-en.skill bcra-oracle-en -x '*__pycache__*' '*.DS_Store'
```

Revisá que cada paquete tenga la carpeta del skill en la raíz (`bcra-oraculo/SKILL.md`, …) y nada de `__pycache__` ni `.DS_Store`:

```bash
unzip -l bcra-oraculo.skill
```

### 4. Subir, revisar y unir

```bash
git add .
git commit -m "Descripción del cambio"
git push -u origin nombre-del-cambio
gh pr create --base main --fill
gh pr merge --merge --delete-branch
```

### 5. Crear la release con los dos paquetes

```bash
git checkout main
git pull
gh release create v2.0.1 bcra-oraculo.skill bcra-oracle-en.skill --title "v2.0.1" --notes "Qué cambió (copiar del CHANGELOG)"
```

`gh release create` crea también el tag `v2.0.1`. Los skills que dependen de este (como estratega-bancario) usan el `bcra-oraculo` instalado y controlan su versión: con un parche o una versión menor no hay que cambiarles nada.

## Consejo

En GitHub, el README.md se muestra automáticamente en la portada del repositorio. Es lo primero que ve cualquiera que llegue, así que ya está escrito para explicar bien qué hace el proyecto y cómo usarlo.
