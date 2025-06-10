# Projeto para aplicação da Cifra Hill na disciplina de Segurança de Sistemas

## Sobre a Cifra de Hill

A cifra de Hill é um método de criptografia que, através de um cálculo com matrizes, realiza a transformação do texto em um texto cifrado. Para realização desse procedimento, basicamente há 4 passos:

1. Converter o texto em números (índices no alfabeto)
2. Agrupar os números em vetores
3. Multiplicar esses vetores por uma matriz chave
4. Converter os resultados de volta para texto

O procedimento é o mesmo tanto para cifragem quanto para decifragem, o que muda é a matriz chave. Essa matriz chave na decriptografia precisa ser a matriz inversa da matriz utilizada durante o processo de criptografia.

### Características Principais

- Utiliza uma matriz quadrada como chave
- A matriz chave deve ser inversível
- O tamanho da matriz determina o tamanho dos blocos de texto processados

## Implementação

### Estrutura do Projeto

- `app.py`: Implementação principal do algoritmo
- `handle_args.py`: Recebimento e verificação dos argumentos informados via linha de comando
- `handle_key.py`: Gerenciamento de chaves

### Explicação do Código

O código consiste em algumas seções com suas responsabilidades. Abaixo segue essas seções e breves explicações de cada etapa:

#### Definições Gerais

Essa etapa contém algumas informações sobre gerais que são utilizadas durante todo o contexto da aplicação do algoritmo:
```
# Dimensão da matriz chave, por consequência do tamanho do bloco de texto
TEXT_PART_LENGHT = 2

# Alfabeto conhecido de caracteres
ALPHABET = "".join(chr(i) for i in range(32, 127)) + "çÇáéíóúâêîôûãõàèìòùäëïöüÁÉÍÓÚÂÊÎÔÛÃÕÀÈÌÒÙÄËÏÖÜ—ª"
ALPHABET_LENGHT = len(ALPHABET)
```

#### Busca e validação de parâmetros

Nessa etapa são validados e retornados os argumentos do algoritmo que foram inseridos pelo usuário, além de já preparar o nome do arquivo resultando do processo solicitado:

```
def getArgs():
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
    RESULT_FILE_NAME = baseFileName + ('_cifrado' if IS_CIPHERING else '_decifrado') + '.txt'

    return [FILE_NAME, USER_PASSWORD, IS_CIPHERING, RESULT_FILE_NAME];
```

#### Busca/Geração da chave a partir da senha informada pelo usuário

Nesse ponto, caso seja um processo de criptografia, será gerada uma chave a partir da senha inserida pelo usuário. Essa chave, junto com salto aplicado, serão salvos para que possam ser utilizadas posteriormente no processo de decriptografia. Nesse mesmo local, caso seja um processo de decriptografia, será realizada a validação da senha informada pelo usuário e, em caso de sucesso, retornada a chave.

```
def getKey(password, is_ciphering):
    # Caso esteja criptografando, gera a chave a partir da senha definida
    if is_ciphering:
        keyData = generateKey(password)
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

        if not checkPassword(password, key, salt):
            print("Senha inválida!")
            sys.exit(1)

    return key
```

#### Criação da matriz chave para aplicação do algoritmo

Agora com a chave gerada ou buscada conforme o processo a ser aplicado (criptografia/descriptografia), a partir dessa chave é criada a matriz chave para utilização na Cifra de Hill. Se for decriptografia, será retornada a matriz inversa da matriz chave.

```
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
```

#### Aplicação do algoritmo no texto (criptografando ou decriptogrando)

A última etapa do processo é a utilização da matriz chave para tranformação do texto. Para facilitar o entendimento, vamos separar etapa em alguns passos.

##### Leitura do arquivo e abertura do arquivo para o resultado

```
baseFile = codecs.open(FILE_NAME, "r", "utf-8")
resultFile = codecs.open(RESULT_FILE_NAME, "w", "utf-8");
```

##### Iteração sobre cada linha do arquivo a ser processado

```
for text in baseFile:
    text = text.rstrip()
    .
    .
    .
```

##### Em cada iteração: adiciona um padding ao texto caso ele não tenha completado o tamanho do bloco

```
def add_padding(text): # Adiciona espaços para completar o bloco
    # Calcula o número de caracteres necessários para completar o bloco
    padding_needed = (TEXT_PART_LENGHT - len(text) % TEXT_PART_LENGHT) % TEXT_PART_LENGHT
    
    return text + " " * padding_needed
```

##### Em cada iteração: percorre todos os caracteres da linha formando pequenos blocos de números conforme o índice de cada caractere dentro do alfabeto definido. Os bloco tem o mesmo tamanho que a dimensão da matriz chave.

```
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
```

##### Em cada iteração: itera todos os blocos gerados para a linha, multiplicando o bloco pelo matriz chave (ou inversa), para gerar novos blocos de índices.

```
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
```

##### Em cada iteração: converte os blocos de índices gerados para texto conforme o caractere correspondente do índice dentro do alfabeto definido e escreve o texto gerado no arquivo resultante.

```
# Converte os índices de volta para caracteres
textArr = [ALPHABET[num] for num in indexesAfterResult]
resultText = ''.join(textArr)

resultFile.write(resultText)
resultFile.write('\n')
```

##### Fecha o arquivo encerrando o processo de aplicação da Cifra de Hill

```
resultFile.close()
```
