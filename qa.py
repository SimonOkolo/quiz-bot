import re
import sqlite3
import pyscreenshot as ImageGrab
import pytesseract
from tkinter import Tk, Label, Button, Entry, StringVar, END
import time

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

DB_FILE = 'C:/tassomaibot/qa.db'

def create_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        );
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()

def clean_text(text):
    cleaned_text = ' '.join(text.split())
    return cleaned_text

def get_question_from_screen():
    time.sleep(1)
    
    img = ImageGrab.grab(bbox=(640, 260, 1260, 355))
    text = pytesseract.image_to_string(img)
    cleaned_text = clean_text(text)
    lines = cleaned_text.split('\n')
    potential_question_lines = []

    for line in lines:
        if line.strip():
            potential_question_lines.append(line)

    question = ' '.join(potential_question_lines)

    if question:
        return question, cleaned_text
    return "No question detected.", cleaned_text

def query_db(cleaned_question):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT answer FROM questions WHERE question=?", (cleaned_question,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def get_new_answer(question, answer_entry, message_var):
    answer = answer_entry.get()
    if answer:
        add_to_db(question, answer)
        answer_entry.delete(0, END)
        message_var.set("Answer added to the database.")
    else:
        message_var.set("Answer cannot be empty.")

def add_to_db(question, answer):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO questions (question, answer) VALUES (?, ?)", (question, answer))
    conn.commit()
    conn.close()

def update_question(new_question_var, question_label, message_var, answer_entry):
    new_question = new_question_var.get()
    if new_question:
        question_label.config(text=f"Question: {new_question}")
        message_var.set("Question updated.")
        answer_entry.pack()  # Re-pack the answer entry
    else:
        message_var.set("New question cannot be empty.")
        answer_entry.pack_forget()  # Hide the answer entry

def detect_or_new_question(label, new_question_var, answer_entry, message_var):
    new_question_var.set("")
    answer_entry.delete(0, END)
    message_var.set("")
    question, _ = get_question_from_screen()
    label.config(text=f"Question: {question}")
    answer = query_db(clean_text(question))
    if answer:
        message_var.set(f"Answer: {answer}")
        answer_entry.pack_forget()  # Hide the answer entry
    else:
        answer_entry.pack()  # Re-pack the answer entry

def main():
    root = Tk()
    root.title("TASSOMAI BOTTT")

    label = Label(root, text="")
    label.pack()

    new_question_var = StringVar()
    new_question_entry = Entry(root, textvariable=new_question_var, width=80)  # Adjust width as needed
    new_question_entry.pack()

    update_button = Button(root, text="Update Question", command=lambda: update_question(new_question_var, label, message_var, answer_entry))
    update_button.pack()

    entry_label = Label(root, text="Answer:")
    entry_label.pack()

    answer_var = StringVar()
    answer_entry = Entry(root, textvariable=answer_var, width=80)  # Adjust width as needed
    answer_entry.pack()

    message_var = StringVar()
    message_label = Label(root, textvariable=message_var)
    message_label.pack()

    detect_button = Button(root, text="Next Question", command=lambda: detect_or_new_question(label, new_question_var, answer_entry, message_var))
    detect_button.pack()

    submit_button = Button(root, text="Submit", command=lambda: get_new_answer(label.cget("text")[10:], answer_entry, message_var))
    submit_button.pack()

    root.mainloop()

if __name__ == '__main__':
    main()