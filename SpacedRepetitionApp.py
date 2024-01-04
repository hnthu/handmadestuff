import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sqlite3
from datetime import date, timedelta

import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)

def execute_sql(cursor, query, params=None):
    logging.info(f"Executing SQL: {query}, Parameters: {params}")
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

# Database setup
DATABASE_FILE = 'review_data.db'

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS questions
                 (id INTEGER PRIMARY KEY, question TEXT, answer TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reviews
                 (question_id INTEGER, next_review DATE,
                  FOREIGN KEY(question_id) REFERENCES questions(id))''')
    conn.commit()
    conn.close()

def insert_question(question, answer):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO questions (question, answer) VALUES (?, ?)", (question, answer))
    conn.commit()
    conn.close()

def load_questions():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT id, question, answer FROM questions")
    questions = c.fetchall()
    conn.close()
    return questions

def load_schedule(question_id):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT next_review FROM reviews WHERE question_id = ?", (question_id,))
    result = c.fetchone()
    conn.close()
    return result

def update_schedule(question_id, correct):
    next_review_date = date.today() + (timedelta(days=7) if correct else timedelta(days=1))
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("REPLACE INTO reviews (question_id, next_review) VALUES (?, ?)",
              (question_id, next_review_date))
    conn.commit()
    conn.close()

# GUI Application
class SpacedRepetitionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Spaced Repetition for Java Interview Questions")
        self.geometry("600x400")

        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open...", command=self.open_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit)

        self.question_label = tk.Label(self, text="Select a file to start.", wraplength=550)
        self.question_label.pack(pady=20)

        self.answer_label = tk.Label(self, text="", wraplength=550, fg="blue")
        self.answer_label.pack(pady=20)
        
        self.show_answer_button = tk.Button(self, text="Show Answer", command=self.show_answer)
        self.show_answer_button.pack(pady=5)

        self.right_button = tk.Button(self, text="I got it right", command=lambda: self.rate_answer(True))
        self.right_button.pack(pady=5)

        self.wrong_button = tk.Button(self, text="I got it wrong", command=lambda: self.rate_answer(False))
        self.wrong_button.pack(pady=5)
        
        # Create entry widgets for the question and answer
        self.question_entry = tk.Entry(self)
        self.question_entry.pack()
        self.answer_entry = tk.Entry(self)
        self.answer_entry.pack()
        
        # Create a button to submit the new question and answer
        self.submit_button = tk.Button(self, text="Submit", command=self.submit_question)
        self.submit_button.pack()
        
        # Create a frame for the buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        # Add a button to refresh the list
        self.refresh_button = tk.Button(button_frame, text="Refresh List", command=self.refresh_question_list)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        # Create a button to delete the selected question
        self.delete_button = tk.Button(button_frame, text="Delete Selected", command=self.delete_selected)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        # Modify Treeview setup to include a hidden question ID column
        self.tree = ttk.Treeview(tree_frame , columns=('ID', 'Question', 'Next Review Date'), show='headings')
        self.tree.heading('Question', text='Question')
        self.tree.heading('Next Review Date', text='Next Review Date')
        self.tree.column('ID', width=0, stretch=tk.NO, anchor='center')  # Set the width to 0 to hide it
        self.tree['displaycolumns'] = ('Question', 'Next Review Date')  # Only display these columns
        self.tree.pack(fill=tk.BOTH, expand=True)
        

        self.refresh_question_list()  # Load the initial list of questions
        self.load_next_question()  # Call this method when the app initializes

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No item selected")
            return
        
        response = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the selected questions?")
        if response:
            for item in selected_items:
                question_id = self.tree.item(item, "values")[0]  # Assuming the first value is the question_id
                self.delete_question_from_db(question_id)
                self.tree.delete(item)
            messagebox.showinfo("Info", "Selected questions deleted successfully")

    def delete_question_from_db(self, question_id):
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        # Delete from reviews table first to maintain referential integrity
        execute_sql(c,"DELETE FROM reviews WHERE question_id = ?", (question_id,))
        # Then delete from questions table
        execute_sql(c,"DELETE FROM questions WHERE id = ?", (question_id,))
        conn.commit()
        conn.close()
    
    def refresh_question_list(self):
        # Clear the current items in the tree
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Fetch all questions and their next review dates from the database
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute("SELECT id, question, IFNULL(next_review, 'N/A') FROM questions LEFT JOIN reviews ON questions.id = reviews.question_id")
        questions = c.fetchall()
        conn.close()

        # Insert questions into the Treeview
        for q in questions:
            self.tree.insert('', 'end', values=q)  # q contains the question ID, question, and next review date

    def submit_question(self):
        # Get the question and answer from the entry widgets
        question = self.question_entry.get()
        answer = self.answer_entry.get()
        
        # Insert the question and answer into the database
        insert_question(question, answer)
        
        # Clear the entry widgets
        self.question_entry.delete(0, tk.END)
        self.answer_entry.delete(0, tk.END)
        
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.store_questions_in_db(file_path)

    def store_questions_in_db(self, file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read().strip()
                blocks = content.split('\n\n')  # Assuming two newlines separate Q/A pairs
                for block in blocks:
                    parts = block.split('\n')
                    if len(parts) >= 2 and parts[0].startswith('Q:') and parts[1].startswith('A:'):
                        question = parts[0][3:].strip()  # Remove 'Q:' prefix
                        answer = parts[1][3:].strip()    # Remove 'A:' prefix
                        insert_question(question, answer)
                    else:
                        print(f"Skipping invalid Q/A block: {block}")
                messagebox.showinfo("Success", "Questions have been stored in the database.")
                self.refresh_question_list()
                self.load_next_question();
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def load_next_question(self):
        # Get today's date to find out which questions are due for review
        today = date.today()
        
        # Fetch all questions and their next review date from the database
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute('''SELECT q.id, q.question, q.answer 
                     FROM questions q 
                     LEFT JOIN reviews r ON q.id = r.question_id 
                     WHERE r.next_review <= ? OR r.next_review IS NULL''', (today,))
        
        due_questions = c.fetchall()
        conn.close()
        
        if due_questions:
            # If there are questions due, pick the first one
            self.current_question_id, question_text, answer_text = due_questions[0]
            self.question_label.config(text=question_text)
            self.answer_label.config(text="")  # Hide answer until user requests it
            self.current_answer = answer_text
            self.show_answer_button.config(state=tk.NORMAL)
            self.right_button.config(state=tk.NORMAL)
            self.wrong_button.config(state=tk.NORMAL)
        else:
            # If there are no questions due, inform the user and disable buttons
            self.current_question_id = None
            self.question_label.config(text="No more questions to review today!")
            self.answer_label.config(text="")
            self.show_answer_button.config(state=tk.DISABLED)
            self.right_button.config(state=tk.DISABLED)
            self.wrong_button.config(state=tk.DISABLED)

    def show_answer(self):
        if hasattr(self, 'current_answer'):  # Check if 'current_answer' is defined
            self.answer_label.config(text=self.current_answer)
        else:
            messagebox.showerror("Error", "The current answer is not available.")

    def rate_answer(self, correct):
        update_schedule(self.current_question_id, correct)
        self.refresh_question_list()
        self.load_next_question()

# Initialization
if __name__ == "__main__":
    init_db()  # Initialize the database and tables
    app = SpacedRepetitionApp()
    app.mainloop()