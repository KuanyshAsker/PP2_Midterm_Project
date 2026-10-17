# Library Management System

This is a console program for managing a small university library.

## Running the program

Open a terminal in this folder and run:

```bash
python3 main.py
```

When the program starts for the first time, it creates `project.db` and adds sample records. The sample database contains 50 books, 40 members, and 30 borrowing records.

## Using the menu

The menu lets you add books and members, borrow or return books, display records, search books or members, update a book, and cancel a borrowing. Choose option 9 to see the borrowing statistics. Choose option 10 to save a summary to `results.txt`.

The sample data has 12 active loans. *Python Crash Course* is the most borrowed book, with 8 loans.

## Project files

- `main.py` runs the program.
- `project.db` contains the library data.
- `results.txt` contains an exported summary and borrowing list.
- `ProjectReport.pdf` and `ProjectPresentation.pptx` are the project report and presentation.
