from transmitter.source_analysis import analyze_source, calculate_entropy
from transmitter.huffman import build_huffman_code
from transmitter.source_encoder import encode_source

from common.file_utils import read_file
from common.report_utils import print_source, print_huffman

from pathlib import Path

ruta = Path("textito.txt")
datos = read_file(ruta) #Genera un binario a partir del archivo de texto

r = analyze_source(datos)

#
print_source(r) #imprime los resultados del análisis de la fuente, incluyendo conteos, probabilidades y entropía

cod_huffman = build_huffman_code(r.probabilities)
print_huffman(cod_huffman) #imprime el código y sus estadísticos

print(cod_huffman.codebook[10]) #Imprime la palabra binaria correspondiente al 
#símbolo 10 (salto de línea) en el código Huffman generado.

codificacion = encode_source(datos, cod_huffman.codebook) #Codifica la fuente de datos utilizando el código Huffman generado.
print(codificacion)