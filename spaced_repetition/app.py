"""
app.py

SpacedRepetitionApp — main application window.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from spaced_repetition import db


class SpacedRepetitionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Spaced Repetition for Java Interview Questions")
        self.geometry("600x400")
        self._current_question_id = None
        self._current_answer = None
        self._build_ui()
        self.refresh_question_list()
        self.load_next_question()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        self._build_menu()
        self._build_review_section()
        self._build_add_section()
        self._build_list_section()

    def _build_menu(self):
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self._open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

    def _build_review_section(self):
        self.question_label = tk.Label(self, text="Select a file to start.", wraplength=550)
        self.question_label.pack(pady=20)

        self.answer_label = tk.Label(self, text="", wraplength=550, fg="blue")
        self.answer_label.pack(pady=20)

        self.show_answer_button = tk.Button(self, text="Show Answer", command=self._show_answer)
        self.show_answer_button.pack(pady=5)

        self.right_button = tk.Button(self, text="I got it right",
                                      command=lambda: self._rate_answer(True))
        self.right_button.pack(pady=5)

        self.wrong_button = tk.Button(self, text="I got it wrong",
                                      command=lambda: self._rate_answer(False))
        self.wrong_button.pack(pady=5)

    def _build_add_section(self):
        self.question_entry = tk.Entry(self)
        self.question_entry.pack()
        self.answer_entry = tk.Entry(self)
        self.answer_entry.pack()
        tk.Button(self, text="Submit", command=self._submit_question).pack()

    def _build_list_section(self):
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        tk.Button(button_frame, text="Refresh List",
                  command=self.refresh_question_list).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete Selected",
                  command=self._delete_selected).pack(side=tk.LEFT, padx=5)

        tree_frame = tk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self.tree = ttk.Treeview(tree_frame,
                                 columns=('ID', 'Question', 'Next Review Date'),
                                 show='headings')
        self.tree.heading('Question', text='Question')
        self.tree.heading('Next Review Date', text='Next Review Date')
        self.tree.column('ID', width=0, stretch=tk.NO, anchor='center')
        self.tree['displaycolumns'] = ('Question', 'Next Review Date')
        self.tree.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def refresh_question_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for q in db.load_all_with_schedule():
            self.tree.insert('', 'end', values=q)

    def load_next_question(self):
        due = db.load_due_questions()
        if due:
            self._current_question_id, question_text, self._current_answer = due[0]
            self.question_label.config(text=question_text)
            self.answer_label.config(text="")
            self.show_answer_button.config(state=tk.NORMAL)
            self.right_button.config(state=tk.NORMAL)
            self.wrong_button.config(state=tk.NORMAL)
        else:
            self._current_question_id = None
            self._current_answer = None
            self.question_label.config(text="No more questions to review today!")
            self.answer_label.config(text="")
            self.show_answer_button.config(state=tk.DISABLED)
            self.right_button.config(state=tk.DISABLED)
            self.wrong_button.config(state=tk.DISABLED)

    def _show_answer(self):
        if self._current_answer is not None:
            self.answer_label.config(text=self._current_answer)
        else:
            messagebox.showerror("Error", "No current answer available.")

    def _rate_answer(self, correct):
        db.update_schedule(self._current_question_id, correct)
        self.refresh_question_list()
        self.load_next_question()

    def _submit_question(self):
        question = self.question_entry.get()
        answer = self.answer_entry.get()
        db.insert_question(question, answer)
        self.question_entry.delete(0, tk.END)
        self.answer_entry.delete(0, tk.END)

    def _open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self._import_from_file(file_path)

    def _import_from_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                blocks = f.read().strip().split('\n\n')
            for block in blocks:
                parts = block.split('\n')
                if len(parts) >= 2 and parts[0].startswith('Q:') and parts[1].startswith('A:'):
                    db.insert_question(parts[0][3:].strip(), parts[1][3:].strip())
                else:
                    print(f"Skipping invalid Q/A block: {block}")
            messagebox.showinfo("Success", "Questions have been stored in the database.")
            self.refresh_question_list()
            self.load_next_question()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No item selected")
            return
        if messagebox.askyesno("Confirm Delete", "Delete the selected questions?"):
            for item in selected:
                question_id = self.tree.item(item, "values")[0]
                db.delete_question(question_id)
                self.tree.delete(item)
            messagebox.showinfo("Info", "Selected questions deleted successfully")
