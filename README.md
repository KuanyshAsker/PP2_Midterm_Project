# PP2 Midterm Project

## Library Management System

A console-based Python application for managing books, members, and borrowing records with SQLite.

### Run the application

Use Python 3.10 or newer. From the repository folder:

```bash
python3 main.py
```

The included `project.db` contains demonstration data: 50 books, 30 members, and 30 borrowings. On a new database, the application creates the tables and loads the demo dataset automatically.

### Features

- Add and display books, members, and borrowings
- Search books by title and members by name or ID
- Show available books
- Update or delete a book; cancel or return a borrowing
- Calculate borrowing totals, active loans, and the most frequently borrowed book
- Export a report to `results.csv`
- Input validation using regular expressions and repeatable sample data using `random`

### Project files

- `main.py` - application source code
- `project.db` - SQLite database with the minimum dataset
- `results.csv` - exported summary and borrowing details
- `ProjectReport.pdf` - project report
- `ProjectPresentation.pptx` - defense presentation
- `GroupID_LibraryManagement.zip` - all submission files in one archive

The report and presentation contain placeholders for the three team members and their contributions. Replace them before final submission. Rename the ZIP using the actual group ID.
