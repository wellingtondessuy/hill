import codecs
import numpy
import handle_key
import sys

# Dimensão da matriz chave, por consequência do tamanho do bloco de texto
TEXT_PART_LENGHT = 2

# Verifica se foram passados argumentos suficientes
if len(sys.argv) < 3:
    print("Por favor forneça os argumentos necessários")
    print("Uso: python app.py [nome_do_arquivo.txt] [senha] [criptografar|decriptografar]")
    sys.exit(1)

# Pega o nome do arquivo
FILE_NAME = sys.argv[1]

# Pega a senha se fornecida
USER_PASSWORD = sys.argv[2]

# Pega o modo de operação (criptografar ou decriptografar)
modo = sys.argv[3].lower()
if modo == "criptografar":
    IS_CIPHERING = 1
elif modo == "decriptografar": 
    IS_CIPHERING = 0
else:
    print("Modo inválido. Use 'criptografar' ou 'decriptografar'")
    sys.exit(1)

# Remove o sufixo _cifrado no nome base do arquivo caso esteja decriptografando
baseFileName = FILE_NAME.rsplit('.', 1)[0]
if not IS_CIPHERING and baseFileName.endswith('_cifrado'):
    baseFileName = baseFileName[:-8]

# Adiciona o sufixo _cifrado ou _decifrado no nome do arquivo de resultado
resultFileName = baseFileName + ('_cifrado' if IS_CIPHERING else '_decifrado') + '.txt'

# Alfabeto conhecido de caracteres
alphabet = "".join(chr(i) for i in range(32, 127)) + "çÇáéíóúâêîôûãõàèìòùäëïöüÁÉÍÓÚÂÊÎÔÛÃÕÀÈÌÒÙÄËÏÖÜ—ª"
alphabetLenght = len(alphabet)

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

# Caso esteja criptografando, gera a chave a partir da senha definida
if IS_CIPHERING:
    keyData = handle_key.generateKey(USER_PASSWORD)
    key = keyData[0]
    salt = keyData[1]

    keyFile = codecs.open(".key", "wb");
    keyFile.write(key)
    keyFile.close()

    saltFile = codecs.open(".salt", "wb");
    saltFile.write(salt)
    saltFile.close()
# Caso esteja decriptografando, busca a chave nos arquivos
else:
    keyFile = codecs.open(".key", "rb");
    saltFile = codecs.open(".salt", "rb");

    key = keyFile.read()
    salt = saltFile.read()

    if not handle_key.checkPassword(USER_PASSWORD, key, salt):
        print("Senha inválida!")
        sys.exit(1)


cipherKey = generateCipherKey(key, alphabetLenght)
resultFile = codecs.open(resultFileName, "w", "utf-8");

baseFile = codecs.open(FILE_NAME, "r", "utf-8")

# Itera sobre cada linha do arquivo
for text in baseFile:
    text = text.rstrip()
    text = add_padding(text)

    textChangedToIndexes = []

    arr = []

    # Converte o texto para uma lista de índices
    for c in text:
        try:
            index = alphabet.index(c)
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
                result[i] = (result[i] + (cipherKey[i][j] * partArr[j][0])) % alphabetLenght

        for r in result:
            indexesAfterResult.append(int(r[0]))

    # Converte os índices de volta para caracteres
    textArr = [alphabet[num] for num in indexesAfterResult]
    resultText = ''.join(textArr)

    resultFile.write(resultText)
    resultFile.write('\n')

resultFile.close()