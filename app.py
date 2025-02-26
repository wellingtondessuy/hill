import codecs
import numpy

file = codecs.open("texto_cifrado.txt", "r", "utf-8")

firstKeyPart = [1, 2]
secondKeyPartcode = [3, 5]
code = [firstKeyPart, secondKeyPartcode]

codeArr = numpy.array(code)

if 1 == 1:
    codeArr = numpy.linalg.inv(codeArr)

# alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
# rever string
alphabet = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ ÇüáéâäàåçêëèïîìÄÅÆæçèéêëìíîïðñòóôõöøùúûüýþÿ'
alphabetLenght = len(alphabet)

splitTextLenght = 2

cipherFile = codecs.open("texto_decifrado.txt", "w", "utf-8");

for text in file:
    text = text.rstrip()

    textChangedToIndexes = []

    arr = []

    for c in text:
        arr.append([alphabet.index(c)])
        
        if len(arr) % splitTextLenght == 0:
            textChangedToIndexes.append(arr)
            arr = []

    textAfterResult = []

    for part in textChangedToIndexes:
        partArr = numpy.array(part)
        partAfterCode = numpy.matmul(codeArr, partArr)
        for result in partAfterCode:
            textAfterResult.append(round(result[0] % alphabetLenght))

    print(alphabetLenght)
    print(textAfterResult)

    cipherTextArr = [alphabet[num] for num in textAfterResult]
    cipherText = ''.join(cipherTextArr)

    cipherFile.write(cipherText)
    cipherFile.write('\n')

cipherFile.close()