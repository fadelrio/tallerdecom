# Datos para el informe de modulación y canal

- Entrada: `res\muchos_martin_fierro.txt` (4111388 caracteres).
- Bits codificados con Huffman: 19468580.
- Configuración de los gráficos y la corrida con ruido: 4-PAM Gray.
- Energía nominal de bit Eb = 1 en unidades normalizadas y tasa de código = 1.

## D. Energías y probabilidades por esquema y orden

Las energías estimadas se calcularon sobre los símbolos transmitidos del texto indicado.
Las probabilidades teóricas corresponden a AWGN a 6 dB, con símbolos equiprobables.

| Esquema | M | Es teórica | Eb teórica | Es estimada | Eb estimada | SER teórica | BER Gray | BER binaria |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| PAM | 2 | 1 | 1 | 1 | 1 | 0.00238829078 | 0.00238829078 | 0.00238829078 |
| PAM | 4 | 2 | 1 | 1.88249604 | 0.941248021 | 0.0557426126 | 0.0278713278 | 0.037161731 |
| PAM | 8 | 3 | 1 | 2.77097812 | 0.923659374 | 0.250418 | 0.0838167831 | 0.131056643 |
| PAM | 16 | 4 | 1 | 3.69378975 | 0.923447437 | 0.506680626 | 0.14113988 | 0.216829233 |
| FSK | 2 | 1 | 1 | 1 | 1 | 0.0230071389 | 0.0230071389 | 0.0230071389 |
| FSK | 4 | 2 | 1 | 2 | 1 | 0.00666417174 | 0.00444278116 | 0.00444278116 |
| FSK | 8 | 3 | 1 | 3 | 1 | 0.00176008949 | 0.00100576542 | 0.00100576542 |
| FSK | 16 | 4 | 1 | 4 | 1 | 0.000453851816 | 0.000242054302 | 0.000242054302 |

## D. Constelación e histograma del transmisor

![Constelación transmitida de 4-PAM](modulation_info.constellation.png)

![Conteos y frecuencias de los símbolos transmitidos](modulation_info.histogram.png)

Los conteos de la tabla siguiente usan todos los símbolos transmitidos.
La frecuencia de referencia equiprobable es 1/M = 0.25.
La tabla de errores para esta configuración usa la corrida con AWGN descrita en E.

## DATOS DE MODULACIÓN Y DEMODULACIÓN

- Esquema: PAM
- Orden M: 4
- Etiquetamiento: gray
- Energía nominal Eb de información: 1
- Tasa de código k/n: 1

### 1. ENERGÍAS MEDIAS

| Magnitud | Teórica | Estimada |
| --- | ---: | ---: |
| Es (símbolo de modulación) | 2 | 1.88249604234 |
| Ec (bit de canal) | 1 | 0.941248021171 |
| Eb (bit de información) | 1 | 0.941248021171 |

Energías expresadas en unidades normalizadas.

### 2. PROBABILIDADES DE ERROR

| Magnitud | Referencia teórica (AWGN) | Estimada (simulación) |
| --- | ---: | ---: |
| SER | 0.0557426126393 | 0.0570432974567 |
| BER | 0.0278713278452 | 0.0285216487284 |

Las probabilidades son adimensionales. La referencia teórica supone
símbolos equiprobables y recepción coherente, antes de decodificar el canal.

### 3. OCURRENCIA DE SÍMBOLOS MODULADOS

| Etiqueta | Cantidad | Probabilidad observada |
| --- | ---: | ---: |
| 00 | 2037892 | 0.209351889044 |
| 01 | 2455480 | 0.252250549347 |
| 11 | 2769108 | 0.284469437422 |
| 10 | 2471810 | 0.253928124188 |

## E. Muestras a la entrada del receptor

- Canal AWGN a 6 dB. Semilla del generador: 42.
- N0 = 0.251188643. Varianza del ruido por coordenada: 0.125594322.
- Símbolos transmitidos y evaluados para la SER: 9734290.
- Bits recuperados tras demodular: 19468580.
- Bits descartados al modular: 0.
- Bits errados para la BER: 555276 de 19468580.
- La figura muestra 400 muestras recibidas, seleccionadas de la corrida completa.

![Constelación recibida de 4-PAM con AWGN a 6 dB](modulation_info.received.png)
