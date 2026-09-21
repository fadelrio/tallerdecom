# Preparación del entorno para colaboradores

Esta guía permite trabajar desde una terminal y cualquier editor o IDE.
No requiere Codex. Un entorno virtual (`venv`) mantiene las dependencias de
este proyecto separadas de las de otros proyectos.

## Requisitos previos

- Python 3.10 o posterior con el módulo `venv` disponible.
- Una copia del proyecto y una terminal ubicada en la carpeta que contiene
  `main.py` y `requirements.txt`.
- Acceso a Internet para descargar las dependencias la primera vez.

Si la ruta contiene espacios, escribirla entre comillas al usar `cd`.
Cada colaborador debe crear su propio `.venv`: no copiar el de otra computadora
ni subirlo a Git. La carpeta ya está excluida por `.gitignore`.

## Linux y macOS (Bash o Zsh)

Desde la raíz del proyecto:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip --version
python -m pip install -r requirements.txt
```

La creación se realiza una sola vez. Al abrir otra terminal, volver a la raíz
del proyecto y ejecutar `source .venv/bin/activate`.

## Windows (PowerShell)

Desde la raíz del proyecto:

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip --version
python -m pip install -r requirements.txt
```

Verificar que la versión mostrada sea 3.10 o posterior. Si `py` no está
disponible pero `python` corresponde a una versión compatible, usar
`python --version` y `python -m venv .venv` en los dos primeros pasos.

Si PowerShell bloquea el script de activación, usar los comandos sin activación
de la sección siguiente. No es necesario cambiar la política de ejecución.
En la terminal CMD, la activación se realiza con `.venv\Scripts\activate.bat`.

## Trabajar sin activar el entorno

La activación es una comodidad: también se puede invocar directamente el
intérprete del entorno. Desde la raíz, en Linux/macOS:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
.venv/bin/python -m pytest -q
```

En Windows (PowerShell):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
.\.venv\Scripts\python.exe -m pytest -q
```

## Verificar el entorno y ejecutar

Con el entorno activado, los comandos son iguales en todos los sistemas:

```bash
python -c "import sys; print(sys.executable)"
python -m pip check
python main.py
python -m pytest -q
```

La primera salida debe apuntar al Python dentro de `.venv`. El programa
principal muestra las etapas pendientes y no requiere un archivo de entrada.
La suite incluye arquitectura, análisis y codificación por bloques e
integración con Huffman. Las pruebas de decodificación ya se ejecutan.
La suite da 62 aprobadas sin omisiones; consultar el
[estado de las pruebas](tests/README.md). `pytest` es la única dependencia externa directa del proyecto;
`pip` también instalará las dependencias propias de esa herramienta.

Para salir de un entorno activado:

```bash
deactivate
```

## Configurar un editor o IDE

Abrir la raíz del proyecto y seleccionar como intérprete Python:

- Linux/macOS: `.venv/bin/python` dentro de la copia local del proyecto.
- Windows: `.venv\Scripts\python.exe` dentro de la copia local del proyecto.

Configurar esa misma raíz como directorio de trabajo al ejecutar el programa
o las pruebas. La terminal integrada y el ejecutor del editor pueden usar
intérpretes distintos: verificar ambos si uno no encuentra las dependencias.

## Problemas frecuentes

### `No module named pip`

Restaurar `pip` en el entorno elegido y repetir la instalación. En Linux/macOS:

```bash
.venv/bin/python -m ensurepip --upgrade
.venv/bin/python -m pip install -r requirements.txt
```

En Windows (PowerShell):

```powershell
.\.venv\Scripts\python.exe -m ensurepip --upgrade
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### No está disponible `venv` o `ensurepip`

Instalar el componente de entornos virtuales correspondiente a la instalación
de Python del sistema. Algunas distribuciones Linux lo distribuyen por
separado. Después volver a crear el entorno con ese Python. Si ya existe un
`.venv` incompleto, desactivarlo y renombrarlo como respaldo antes de crear uno
nuevo; no reutilizar entornos copiados o movidos de otra computadora.

### `No module named pytest` o dependencias en otro Python

Instalar con `python -m pip`, usando el intérprete del entorno como en los
ejemplos anteriores. Ejecutar también las pruebas con `python -m pytest`.
Esto evita depender de a qué instalación apunten los comandos `pip` o `pytest`.

### No se encuentra `requirements.txt`

Volver a la raíz del proyecto antes de instalar. No ejecutar la instalación
desde `common`, `receiver`, `transmitter` o `tests`.

### Fallos de red durante la instalación

Comprobar la conexión y la configuración de proxy si corresponde y repetir
el comando. No es necesario usar `sudo` para instalar dentro del entorno.

## Mantenimiento

Después de obtener cambios en `requirements.txt`, volver a ejecutar la
instalación dentro del entorno. Si se agregan dependencias al proyecto,
declararlas en ese archivo y documentarlas en el [README](README.md).
Actualizar esta guía cuando cambien los pasos o la versión mínima de Python.
