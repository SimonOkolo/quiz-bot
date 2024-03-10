import sqlite3
import pytesseract
from tkinter import Tk, Label, Text, StringVar, END
import time
import pyautogui
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter.ttk import Style


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
    
    img = pyautogui.screenshot(region=(560, 300, 1330-560, 430-300))
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
    answer = answer_entry.get("1.0", END).strip()
    if answer:
        add_to_db(question, answer)
        answer_entry.delete("1.0", END)
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
        answer_entry.pack(expand=True, fill='both', padx=10, pady=10)  # Add padding here
    else:
        message_var.set("New question cannot be empty.")
        answer_entry.pack_forget()  # Hide the answer entry

def detect_or_new_question(label, new_question_var, answer_entry, message_var, submit_button):
    new_question_var.set("")
    answer_entry.delete("1.0", END)
    message_var.set("")
    question, _ = get_question_from_screen()
    label.config(text=f"Question: {question}")
    answer = query_db(clean_text(question))
    if answer:
        message_var.set(f"Answer: {answer}")
        answer_entry.pack_forget()  # Hide the answer entry
        submit_button.pack_forget()  # Hide the submit button
    else:
        answer_entry.pack(expand=True, fill='both', padx=10, pady=10)  # Add padding here
        submit_button.pack(pady=0)  # Show the submit button

def find_and_answer_question(label, new_question_var, answer_entry, message_var, submit_button):
    # Get the answer from the database
    question_text, _ = get_question_from_screen()
    label.config(text=f"Question: {question_text}")
    answer = query_db(clean_text(question_text))

    # Display the question and answer in the message_label
    message_var.set(f"Answer: {answer}")

    button_info = [
        {"x": 570, "y": 440, "width": 370, "height": 120},  # Button 1 DONE
        {"x": 970, "y": 440, "width": 370, "height": 120},  # Button 2
        {"x": 570, "y": 600, "width": 370, "height": 120},  # Button 3
        {"x": 970, "y": 600, "width": 370, "height": 120}   # Button 4
    ]

    # Loop through each button location
    for button_data in button_info:
        button_x = button_data["x"]
        button_y = button_data["y"]
        button_width = button_data["width"]
        button_height = button_data["height"]

        # Capture a screenshot of the button
        button_img = pyautogui.screenshot(region=(button_x, button_y, button_width, button_height))

        # Use OCR to extract text from the button image
        button_text = pytesseract.image_to_string(button_img)

        # Clean the extracted text
        button_text = clean_text(button_text)

        # Check if the extracted text matches the answer
        if button_text == answer:
            # If a match is found, click on the button
            button_center_x = button_x + button_width // 2
            button_center_y = button_y + button_height // 2
            pyautogui.click(button_center_x, button_center_y)  # Click at the center of the button
            time.sleep(2)  # Delay for 3 seconds
            find_and_answer_question(label, new_question_var, answer_entry, message_var, submit_button)
            break  # Exit the loop after clicking the button

def main():
    root = Tk()
    root.title("Tassomai Killer")
    root.geometry("800x400")
    root.resizable(False, False)

    # Load the icon image
    icon_image = ImageTk.PhotoImage(file="C:/tassomaibot/evil-tassomai.png")  # Provide the path to your icon image file
    root.iconphoto(True, icon_image)  # Set the icon for the window

    # Load the image for the header
    header_image = Image.open("C:/tassomaibot/evil-tassomai.png")  # Provide the path to your image file
    header_photo = ImageTk.PhotoImage(header_image)

    # Create a label to display the header image
    header_label = Label(root, image=header_photo)
    header_label.image = header_photo  # Keep a reference to avoid garbage collection
    header_label.pack(anchor="n", pady=0)  # Anchor to the top-middle

    label = ttk.Label(root, text="")
    label.pack()

    # Create a frame to contain the new_question_entry and update_button
    entry_frame = ttk.Frame(root)
    entry_frame.pack()

    new_question_var = StringVar()
    new_question_entry = ttk.Entry(entry_frame, textvariable=new_question_var, width=80, justify="center")
    new_question_entry.grid(row=0, column=0)  # Use grid layout for more precise positioning

    update_button = ttk.Button(entry_frame, text="Update Question", command=lambda: update_question(new_question_var, label, message_var, answer_entry))
    update_button.grid(row=0, column=1, padx=5, pady=30)  # Use grid layout for more precise positioning

    answer_entry = Text(root, width=80, height=5,)  # Adjust width and height as needed
    answer_entry.pack()

    message_var = StringVar()
    message_label = ttk.Label(root, textvariable=message_var)
    message_label.pack()

    # Create a style object
    style = Style()

    # Configure the style for the submit button
    style.configure('Submit.TButton', font=('Helvetica', 12, 'bold'))

    submit_button = ttk.Button(root, text="Submit Answer", command=lambda: get_new_answer(label.cget("text")[10:], answer_entry, message_var), width=20, style='Submit.TButton')
    submit_button.pack(pady=0)

    detect_button = ttk.Button(root, text="Analyse Next Question", command=lambda: find_and_answer_question(label, new_question_var, answer_entry, message_var, submit_button))        

    detect_button.pack()

    root.mainloop()

if __name__ == '__main__':
    main()