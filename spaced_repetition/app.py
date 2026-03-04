"""
app.py

SpacedRepetitionApp — main application window.
"""

from __future__ import annotations

import logging
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from spaced_repetition import db
from spaced_repetition.models import Question

logger = logging.getLogger(__name__)


class SpacedRepetitionApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Spaced Repetition for Java Interview Questions")
        self.geometry("600x400")
        self._current: Question | None = None
        self._build_ui()
        self.refresh_question_list()
        self.load_next_question()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._build_menu()
        self._build_review_section()
        self._build_add_section()
        self._build_list_section()

    def _build_menu(self) -> None:
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self._open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

    def _build_review_section(self) -> None:
        self._question_label = tk.Label(self, text="Select a file to start.", wraplength=550)
        self._question_label.pack(pady=20)

        self._answer_label = tk.Label(self, text="", wraplength=550, fg="blue")
        self._answer_label.pack(pady=20)

        self._show_answer_btn = tk.Button(self, text="Show Answer", command=self._show_answer)
        self._show_answer_btn.pack(pady=5)

        self._right_btn = tk.Button(
            self, text="I got it right", command=lambda: self._rate_answer(correct=True)
        )
        self._right_btn.pack(pady=5)

        self._wrong_btn = tk.Button(
            self, text="I got it wrong", command=lambda: self._rate_answer(correct=False)
        )
        self._wrong_btn.pack(pady=5)

    def _build_add_section(self) -> None:
        self._question_entry = tk.Entry(self)
        self._question_entry.pack()
        self._answer_entry = tk.Entry(self)
        self._answer_entry.pack()
        tk.Button(self, text="Submit", command=self._submit_question).pack()

    def _build_list_section(self) -> None:
        btn_frame = tk.Frame(self)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        tk.Button(btn_frame, text="Refresh List",
                  command=self.refresh_question_list).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Selected",
                  command=self._delete_selected).pack(side=tk.LEFT, padx=5)

        tree_frame = tk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self._tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Question", "Next Review Date"),
            show="headings",
        )
        self._tree.heading("Question", text="Question")
        self._tree.heading("Next Review Date", text="Next Review Date")
        self._tree.column("ID", width=0, stretch=tk.NO, anchor="center")
        self._tree["displaycolumns"] = ("Question", "Next Review Date")
        self._tree.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def refresh_question_list(self) -> None:
        for row in self._tree.get_children():
            self._tree.delete(row)
        for q in db.load_all_with_schedule():
            self._tree.insert("", "end", values=(q.id, q.text, q.next_review))

    def load_next_question(self) -> None:
        due = db.load_due_questions()
        state = tk.NORMAL if due else tk.DISABLED
        if due:
            self._current = due[0]
            self._question_label.config(text=self._current.text)
            self._answer_label.config(text="")
        else:
            self._current = None
            self._question_label.config(text="No more questions to review today!")
            self._answer_label.config(text="")
        for btn in (self._show_answer_btn, self._right_btn, self._wrong_btn):
            btn.config(state=state)

    def _show_answer(self) -> None:
        if self._current:
            self._answer_label.config(text=self._current.answer)
        else:
            messagebox.showerror("Error", "No current answer available.")

    def _rate_answer(self, *, correct: bool) -> None:
        if self._current:
            db.update_schedule(self._current.id, correct)
            self.refresh_question_list()
            self.load_next_question()

    def _submit_question(self) -> None:
        question = self._question_entry.get().strip()
        answer = self._answer_entry.get().strip()
        if question and answer:
            db.insert_question(question, answer)
            self._question_entry.delete(0, tk.END)
            self._answer_entry.delete(0, tk.END)

    def _open_file(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self._import_from_file(Path(file_path))

    def _import_from_file(self, path: Path) -> None:
        try:
            blocks = path.read_text(encoding="utf-8").strip().split("\n\n")
            imported = 0
            for block in blocks:
                parts = block.split("\n")
                if len(parts) >= 2 and parts[0].startswith("Q:") and parts[1].startswith("A:"):
                    db.insert_question(parts[0][3:].strip(), parts[1][3:].strip())
                    imported += 1
                else:
                    logger.warning("Skipping invalid Q/A block: %s", block[:60])
            messagebox.showinfo("Success", f"Imported {imported} question(s).")
            self.refresh_question_list()
            self.load_next_question()
        except Exception as exc:
            messagebox.showerror("Error", f"An error occurred: {exc}")

    def _delete_selected(self) -> None:
        selected = self._tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No item selected")
            return
        if messagebox.askyesno("Confirm Delete", "Delete the selected questions?"):
            for item in selected:
                question_id = self._tree.item(item, "values")[0]
                db.delete_question(question_id)
                self._tree.delete(item)
            messagebox.showinfo("Info", "Selected questions deleted successfully")
