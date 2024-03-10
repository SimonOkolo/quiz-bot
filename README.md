
# Quiz Bot

A python program that stores quiz answers on a local database. Includes a basic GUI.

Works most idealy on quizzes with repeated questions that dont update regularly.

!THE PROGRAM IS STILL BASED ON PERSONAL USAGE SO FILES MAY HAVE LIKE "unflexible" ROUTES, You will need to change these to use it!
eg.


`DB_FILE = 'C:/tassomaibot/qa.db'`

`pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`




## How it works

1. Takes screenshot of the question
2. Extracts text and compares it to a database
3. If a match is found, the answer is returned
4. If no answer is found the program asks for the answer
## Dependencies
- Tesseract OCR
- tkinter
- sqlite3
- pyautogui
