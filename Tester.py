from BadAdvice import BadAdvice

badAdvice = BadAdvice()

while True:
    sent = input('Enter a question: ')
    if sent == 'quit' or sent == 'exit':
        break
    print(badAdvice.get_advice(sent))
