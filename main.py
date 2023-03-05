# Import necessary modules
import os
import shutil
import sqlite3
import requests
import telebot
import config

# Create a Telegram bot instance
bot = telebot.TeleBot(config.TOKEN)

# Define a handler for the "/start" command
@bot.message_handler(commands=['start'])
def start_message(message):
    # Get user ID from the message
    user = message.chat.id

    # Construct the path to the user's database
    path = f"db/{user}.sqlite3"

    # Remove the database if it already exists
    if os.path.exists(path):
        os.remove(path)

    # Connect to the database
    conn = sqlite3.connect(path)

    # Create a cursor to execute SQL queries
    cursor = conn.cursor()

    # Execute the SQL script to create the necessary tables in the database
    with open("sql/create.sql", "r") as f:
        cursor.execute(f.read())

    # Commit the changes to the database
    conn.commit()


# Define a handler for the "/clear" command
@bot.message_handler(commands=['clear'])
def clear_message(message):
    # Get user ID from the message
    user = message.chat.id

    # Construct the path to the user's database
    path = f"db/{user}.sqlite3"

    # Connect to the database
    conn = sqlite3.connect(path)
    
    # Create a cursor to execute SQL queries
    cursor = conn.cursor()
    
    # Execute the SQL script to clear the tables in the database
    with open("sql/clear.sql", "r") as f:
        cursor.execute(f.read())
    
    # Commit the changes to the database
    conn.commit()


# Define a handler for any other message
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Get user ID from the message
    user = message.chat.id

    # Construct the path to the user's database
    path = f"db/{user}.sqlite3"

    # Connect to the database
    conn = sqlite3.connect(path)

    # Create a cursor to execute SQL queries
    cursor = conn.cursor()

    # Execute the SQL script to select the user's previous queries and answers
    with open("sql/select.sql", "r") as f:
        cursor.execute(f.read())

    # Initialize a list to store the previous queries and answers
    messages = []

    # Iterate through the results of the SQL query and add the queries and answers to the list
    for query, answer in cursor.fetchall():
        messages.append(dict(role="user", content=query))
        messages.append(dict(role="assistant", content=answer))

    # Get the current user query
    query = message.text

    # Add the current user query to the list of messages
    messages.append(dict(role="user", content=query))

    # Construct a JSON payload to send to the AI model
    json_payload = {
        "model": config.MODEL,
        "messages": messages,
    }

    # Send the JSON payload to the AI model and get the response
    response = requests.post(config.URL, json=json_payload)

    # Extract the AI's answer from the response
    answer = response.json()["choices"][0]["message"]["content"]

    # Execute the SQL script to insert the current user query and the AI's answer into the database
    with open("sql/insert.sql", "r") as f:
        cursor.execute(f.read(), (query, answer))

    # Commit the changes to the database
    conn.commit()

    # Send the AI's answer to the user
    bot.send_message(user, answer)

# Define the main function
def main():
    # Define the path to the "db" directory
    path = "./db"

    # Remove the "db" directory if it already exists
    if os.path.exists(path):
        shutil.rmtree(path)

    # Create the "db" directory
    os.makedirs(path)

    # Start polling the Telegram bot for new messages
    bot.polling()

# Call the main function if the script is being run directly
if __name__ == "__main__":
    main()