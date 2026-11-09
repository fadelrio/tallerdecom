# Pruebas manuales

Espacio para scripts exploratorios escritos y ejecutados por los colaboradores.
No es necesario convertirlos en herramientas con argumentos ni tests pytest.

## Ejecución

Ejecutar desde la raíz del proyecto con el entorno virtual activado.

```bash
python -m experiments.energias_estimadas
python -m experiments.experimento_modulacion
python -m experiments.bit_error_rate
python -m experiments.modulation_data
```

| Módulo | Datos que produce | Archivos que escribe |
| --- | --- | --- |
| `energias_estimadas` | `Es` y `Eb` de PAM y FSK para `M = 2, 4, 8, 16`, con `Eb` nominal igual a 1 y tasa 1. | Solo salida por consola. |
| `experimento_modulacion` | Dimensiones y primeras coordenadas de 16-PAM Gray antes y después de AWGN a 9 dB, y símbolos decididos. | Texto recuperado en la salida configurada. |
| `bit_error_rate` | BER medida y conteos de bits errados y evaluados para 16-PAM Gray con AWGN a 9 dB. | Texto recuperado en la salida configurada. |
| `modulation_data` | Tablas de D/E y una corrida reproducible de 4-PAM Gray con AWGN a 6 dB. | `res/modulation_info.md` y tres PNG de constelación transmitida, histograma y constelación recibida. |

Los primeros tres módulos toman la entrada de `load_config()`, actualmente
`res/muchos_martin_fierro.txt`. `experimento_modulacion` y `bit_error_rate`
sobrescriben `res/output.txt` cuando completan la escritura. El experimento
de energías muestra esa ruta como parte de la configuración e imprime sus
resultados por consola. Los TXT grandes y sus símbolos se mantienen en memoria.

El generador `modulation_data` usa `res/textito.txt` por defecto y admite
`--input`, `--output`, `--tipo` y `--orden`. Mantener los tres PNG junto al
Markdown para que funcionen sus enlaces relativos.

## Experimento de fuente B

`test_B.py` busca `textito.txt` en el directorio de trabajo. Configurar el IDE
para ejecutar `experiments.test_B` con `res/` como directorio de trabajo y la
raíz en la ruta de módulos de Python. En Bash o Zsh, desde la raíz, se puede
usar un subshell para conservar el directorio de la terminal.

```bash
(cd res && PYTHONPATH=.. python -m experiments.test_B)
```

La entrada requiere al menos un salto de línea. El script imprime el análisis,
el código Huffman, la secuencia completa de bits y el texto decodificado.

## Nuevas pruebas

Agregar los scripts a esta carpeta y documentar sus entradas y comandos aquí.
Pueden conservar el estilo de script manual que necesite cada colaborador.

`pytest.ini` limita la búsqueda automática a `tests/`: `python -m pytest` no
importa estas pruebas manuales. No pasar `experiments/` explícitamente a pytest,
ya que hacerlo anula esa selección inicial.
