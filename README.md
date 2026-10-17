# Library Management System

A simple console project using the Python concepts from the six lectures: variables, conditions, loops, functions, classes, text files, regular expressions, `random`, and SQLite.

## Run

Install the pandas dependency first:

```bash
python3 -m pip install -r requirements.txt
```

Use Python 3.10 or newer:

```bash
python3 main.py
```

The app creates `project.db` and adds a demo dataset on first run: 50 books, 40 members, and 30 borrowing records. The sample history includes 12 active loans and repeated borrowing of popular books. The code uses simple functions, loops, and SQL statements. Choose a menu option to add, display, search, update, or cancel records, view basic statistics, and save `results.txt`.

## Course concepts

- `Book` and `Member` classes hold and display records.
- Functions and a `while` loop run the menu and database actions.
- SQLite stores books, members, and borrowings in three related tables.
- Regular expressions check member email addresses.
- `random` selects demo members for borrowing records.
- Pandas displays books, members, borrowings, and search results in tables.
- Export uses basic text-file writing.

## Files

- `main.py` - the application
- `requirements.txt` - the pandas dependency
- `project.db` - demo database
- `results.txt` - exported results
- `ProjectReport.pdf` - 3-page report
- `ProjectPresentation.pptx` - 5-slide defense presentation
- `GroupID_LibraryManagement.zip` - submission archive

Add your three team members' names and actual contributions to the report and slides. Rename the ZIP using your group ID before submitting.
