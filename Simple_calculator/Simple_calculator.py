# Addition
def addition(x, y):
    return x + y

# Subtraction
def subtraction(x, y):
    return x - y

# Multiplication
def multiplication(x, y):
    return x * y

# Division
def division(x, y):
    return x / y

# Exponentiation
def exponentiation(x, y):
    return x ** y

while True :
    # Get the action from the user
    action = input("What action do you want to do? (addition, subtraction, multiplication, division, exponentiation): ")

    # Perform the selected operation
    if action == "addition":
        # Get the numbers from the user
        x = float(input("Give me the first number: "))
        y = float(input("Give me the second number: "))
        print("Result:", addition(x, y))

    elif action == "subtraction":
        # Get the numbers from the user
        x = float(input("Give me the first number: "))
        y = float(input("Give me the second number: "))
        print("Result:", subtraction(x, y))

    elif action == "multiplication":
        # Get the numbers from the user
        x = float(input("Give me the first number: "))
        y = float(input("Give me the second number: "))
        print("Result:", multiplication(x, y))

    elif action == "division":
        # Get the numbers from the user
        x = float(input("Give me the first number: "))
        y = float(input("Give me the second number: "))
        if y != 0:
            print("Result:", division(x, y))
        else:
            print("Error: Division by zero is not allowed.")

    elif action == "exponentiation":
        x = float(input("Give me the base number: "))
        y = float(input("Give me the exponent: "))
        print("Result:", exponentiation(x, y))

    else :
        print("Invalid action")