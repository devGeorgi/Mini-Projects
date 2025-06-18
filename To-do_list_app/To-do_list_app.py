import os

# Initialize an empty list to store tasks
tasks = []

# Load tasks from a file if it exists
if os.path.exists("3. To-do_list_app/tasks.txt"):
    with open("3. To-do_list_app/tasks.txt", "r") as file:
        tasks = file.read().splitlines()

def display_menu():
    print("\nTo-Do List Menu:")
    print("1. Add Task")
    print("2. Remove Task")
    print("3. View Tasks")
    print("4. Save Tasks")
    print("5. Exit")

def view_tasks():
    if not tasks:
        print("\nNo tasks in your to-do list.")
    else:
        print("\nYour Tasks:")
        for i, task in enumerate(tasks, start=1):
            print(f"{i}. {task}")

def add_task():
    task = input("Enter a new task: ")
    tasks.append(task)
    print(f"Task '{task}' added.")

def remove_task():
    view_tasks()
    if tasks:
        try:
            task_num = int(input("Enter the number of the task to remove: "))
            if 1 <= task_num <= len(tasks):
                removed_task = tasks.pop(task_num - 1)
                print(f"Task '{removed_task}' removed.")
            else:
                print("Invalid task number.")
        except ValueError:
            print("Please enter a valid number.")

def save_tasks():
    with open("3. To-do_list_app/tasks.txt", "w") as file:
        for task in tasks:
            file.write(task + "\n")
    print("Tasks saved.")

# Main loop
while True:
    display_menu()
    choice = input("Choose an option (1-5): ")

    if choice == "1":
        add_task()
    elif choice == "2":
        remove_task()
    elif choice == "3":
        view_tasks()
    elif choice == "4":
        save_tasks()
    elif choice == "5":
        save_tasks()
        print("Goodbye!")
        break
    else:
        print("Invalid choice, please select from 1 to 5.")
