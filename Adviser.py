from BadAdviceCFG import BadAdviceCFG as BadAdvice  # Second edition of BadAdvice
# from BadAdvice import BadAdvice  # First edition of BadAdvice

import warnings

warnings.filterwarnings("ignore")

badAdvice = BadAdvice()

print('To close the program, type exit or quit')

while True:
    sent = input('\nEnter a question: ')
    if sent == 'quit' or sent == 'exit':
        break
    print(badAdvice.get_advice(sent))
