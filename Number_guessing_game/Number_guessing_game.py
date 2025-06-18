from random import randint

magic_number = randint(1, 100)
print("You have 10 tries to guess my number between 1 and 100\n")

for i in range(10,0,-1) :
    print (f"You have {i} tries left")
    guess = int(input("Guess a number between 1 and 100: "))
    if guess < magic_number :
        print("Too low!")
    elif guess > magic_number :
        print("Too high!")
    else :
        print("You win!")
        break
if guess != magic_number :
    print(f"You lose. My number was {magic_number}")