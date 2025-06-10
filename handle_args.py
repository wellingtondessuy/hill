import sys

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