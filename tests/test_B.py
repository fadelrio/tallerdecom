from transmitter.source_analysis import analyze_source, calculate_entropy
from transmitter.huffman import build_huffman_code
from common.file_utils import read_file
from pathlib import Path
from common.report_utils import print_source, print_huffman

ruta = Path("textito.txt")
datos = read_file(ruta)

r = analyze_source(datos)

print_source(r)
#print(r)
print(calculate_entropy(r.probabilities))

cod_huffman = build_huffman_code(r.probabilities)
print(cod_huffman.statistics)
#print(cod_huffman.codebook)
print_huffman(cod_huffman)