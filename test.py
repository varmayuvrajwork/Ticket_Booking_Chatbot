import os
while True:
      user_input = input("You: ")
      if user_input.lower() == "exit":
            print("Goodbye!")
            break
print(f"You said: {user_input}")
