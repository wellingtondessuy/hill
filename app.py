import codecs
import numpy
import handle_key
import sys
import handle_args

# Dimensão da matriz chave, por consequência do tamanho do bloco de texto
TEXT_PART_LENGHT = 2

# Alfabeto conhecido de caracteres
ALPHABET = "".join(chr(i) for i in range(32, 127)) + "çÇáéíóúâêîôûãõàèìòùäëïöüÁÉÍÓÚÂÊÎÔÛÃÕÀÈÌÒÙÄËÏÖÜ—ª"
ALPHABET_LENGHT = len(ALPHABET)

# Pega os argumentos passados pela linha de comando
args = handle_args.getArgs()
FILE_NAME = args[0]
USER_PASSWORD = args[1]
IS_CIPHERING = args[2]
RESULT_FILE_NAME = args[3]

def add_padding(text): # Adiciona espaços para completar o bloco
    # Calcula o número de caracteres necessários para completar o bloco
    padding_needed = (TEXT_PART_LENGHT - len(text) % TEXT_PART_LENGHT) % TEXT_PART_LENGHT
    
    return text + " " * padding_needed

def invertMatrix(matrix, alphabetLenght):
    # Calcula o determinante
    det = int(round(numpy.linalg.det(matrix)))

    # Encontra o inverso multiplicativo do determinante módulo alphabetLenght
    def mod_inverse(a, m):
        for x in range(1, m):
            if (a * x) % m == 1:
                return x
        return 1
    
    # Calcula o inverso multiplicativo do determinante
    det_inv = mod_inverse(det % alphabetLenght, alphabetLenght)

    # Calcula a matriz adjunta (transposta da matriz de cofatores)
    # Para uma matriz 2x2, a adjunta é:
    # [[ d  -b]
    #  [-c   a]]
    # onde a matriz original é [[a b], [c d]]
    adj = numpy.array([[matrix[1,1], -matrix[0,1]], 
                        [-matrix[1,0], matrix[0,0]]])
    
    # Calcula a matriz inversa multiplicando a adjunta pelo inverso do determinante
    # e aplicando o módulo para manter os valores dentro do tamanho do alfabeto
    return (adj * det_inv) % alphabetLenght

def generateCipherKey(key, alphabetLenght): # Gera a matriz da chave
    # Gera uma matriz de cifragem a partir da chave fornecida
    cipherKey = numpy.array([(byte % (alphabetLenght - 1)) + 1 for byte in key]).reshape(TEXT_PART_LENGHT, TEXT_PART_LENGHT)

    # Caso esteja decriptografando, inverte a matriz
    if not IS_CIPHERING:
        cipherKey = invertMatrix(cipherKey, alphabetLenght)

    return cipherKey

key = handle_key.getKey(USER_PASSWORD, IS_CIPHERING)
cipherKey = generateCipherKey(key, ALPHABET_LENGHT)

baseFile = codecs.open(FILE_NAME, "r", "utf-8")
resultFile = codecs.open(RESULT_FILE_NAME, "w", "utf-8");

# Itera sobre cada linha do arquivo
for text in baseFile:
    text = text.rstrip()
    text = add_padding(text)

    textChangedToIndexes = []

    arr = []

    # Converte o texto para uma lista de índices
    for c in text:
        try:
            index = ALPHABET.index(c)
        except ValueError:
            index = -1

        arr.append([index])

        if len(arr) % TEXT_PART_LENGHT == 0:
            textChangedToIndexes.append(arr)
            arr = []

    indexesAfterResult = []

    # Multiplica a matriz da chave pela lista de índices
    for part in textChangedToIndexes:
        partArr = numpy.array(part)
        # Realiza a multiplicação e aplica o módulo em cada etapa
        result = numpy.zeros((TEXT_PART_LENGHT, 1), dtype=int)

        for i in range(TEXT_PART_LENGHT):
            for j in range(TEXT_PART_LENGHT):
                result[i] = (result[i] + (cipherKey[i][j] * partArr[j][0])) % ALPHABET_LENGHT

        for r in result:
            indexesAfterResult.append(int(r[0]))

    # Converte os índices de volta para caracteres
    textArr = [ALPHABET[num] for num in indexesAfterResult]
    resultText = ''.join(textArr)

    resultFile.write(resultText)
    resultFile.write('\n')

resultFile.close()

print("Arquivo processado com sucesso!")