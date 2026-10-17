"""A simple library system using Python classes, functions, and SQLite."""

import random
import re
import sqlite3
from datetime import date, timedelta
from pathlib import Path


DATABASE = Path(__file__).with_name("project.db")
RESULTS = Path(__file__).with_name("results.txt")
EMAIL_PATTERN = r"^[\w.-]+@[\w.-]+\.\w+$"
SAMPLE_DAY = date(2026, 10, 17)


class Book:
    """One book in the catalog."""

    def __init__(self, book_id, title, author, genre, available):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.genre = genre
        self.available = available

    def __str__(self):
        status = "Yes" if self.available else "No"
        return f"{self.book_id:<4} {self.title:<37} {self.author:<28} {self.genre:<18} {status}"


class Member:
    """One library member."""

    def __init__(self, member_id, name, email, program):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.program = program

    def __str__(self):
        return f"{self.member_id:<4} {self.name:<25} {self.email:<38} {self.program}"


def connect_database():
    connection = sqlite3.connect(DATABASE)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables(connection):
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT NOT NULL,
            available INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            program TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS borrowings (
            borrowing_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
            member_id INTEGER NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
            borrowed_on TEXT NOT NULL,
            due_on TEXT NOT NULL,
            returned_on TEXT
        );
    """)
    connection.commit()


def add_sample_data(connection):
    """Load a small, repeatable university library dataset once."""
    if connection.execute("SELECT COUNT(*) FROM books").fetchone()[0] > 0:
        return

    books = [
        ("Python Crash Course", "Eric Matthes", "Programming"),
        ("Automate the Boring Stuff with Python", "Al Sweigart", "Programming"),
        ("Think Python", "Allen B. Downey", "Programming"),
        ("Fluent Python", "Luciano Ramalho", "Programming"),
        ("Effective Python", "Brett Slatkin", "Programming"),
        ("Python for Data Analysis", "Wes McKinney", "Data Science"),
        ("Learning Python", "Mark Lutz", "Programming"),
        ("Head First Python", "Paul Barry", "Programming"),
        ("Python Tricks", "Dan Bader", "Programming"),
        ("Python Cookbook", "David Beazley and Brian K. Jones", "Programming"),
        ("Clean Code", "Robert C. Martin", "Programming"),
        ("The Pragmatic Programmer", "Andrew Hunt and David Thomas", "Programming"),
        ("Code Complete", "Steve McConnell", "Programming"),
        ("Design Patterns", "Erich Gamma and others", "Programming"),
        ("Introduction to Algorithms", "Thomas H. Cormen and others", "Computer Science"),
        ("Data Structures and Algorithms in Python", "Michael T. Goodrich and others", "Computer Science"),
        ("Database System Concepts", "Abraham Silberschatz and others", "Computer Science"),
        ("Computer Networking: A Top-Down Approach", "James Kurose and Keith Ross", "Computer Science"),
        ("The Linux Command Line", "William Shotts", "Computer Science"),
        ("The C Programming Language", "Brian Kernighan and Dennis Ritchie", "Programming"),
        ("The Hobbit", "J. R. R. Tolkien", "Fantasy"),
        ("Dune", "Frank Herbert", "Science Fiction"),
        ("1984", "George Orwell", "Classic Fiction"),
        ("Pride and Prejudice", "Jane Austen", "Classic Fiction"),
        ("The Great Gatsby", "F. Scott Fitzgerald", "Classic Fiction"),
        ("To Kill a Mockingbird", "Harper Lee", "Fiction"),
        ("The Little Prince", "Antoine de Saint-Exupery", "Fiction"),
        ("Crime and Punishment", "Fyodor Dostoevsky", "Classic Fiction"),
        ("The Alchemist", "Paulo Coelho", "Fiction"),
        ("Atomic Habits", "James Clear", "Personal Development"),
        ("Sapiens", "Yuval Noah Harari", "History"),
        ("Educated", "Tara Westover", "Memoir"),
        ("And Then There Were None", "Agatha Christie", "Mystery"),
        ("The Kite Runner", "Khaled Hosseini", "Fiction"),
        ("The Book Thief", "Markus Zusak", "Historical Fiction"),
        ("The Silent Patient", "Alex Michaelides", "Mystery"),
        ("The Midnight Library", "Matt Haig", "Fiction"),
        ("A Brief History of Time", "Stephen Hawking", "Science"),
        ("Cosmos", "Carl Sagan", "Science"),
        ("The Diary of a Young Girl", "Anne Frank", "Memoir"),
        ("Words of Edification", "Abai Qunanbaiuly", "Kazakh Literature"),
        ("The Path of Abai", "Mukhtar Auezov", "Kazakh Literature"),
        ("The Nomads", "Ilyas Esenberlin", "Kazakh Literature"),
        ("One Hundred Years of Solitude", "Gabriel Garcia Marquez", "Fiction"),
        ("The Old Man and the Sea", "Ernest Hemingway", "Fiction"),
        ("The Catcher in the Rye", "J. D. Salinger", "Fiction"),
        ("The Name of the Rose", "Umberto Eco", "Mystery"),
        ("A Thousand Splendid Suns", "Khaled Hosseini", "Fiction"),
        ("The Art of War", "Sun Tzu", "History"),
        ("Man's Search for Meaning", "Viktor E. Frankl", "Memoir"),
    ]

    member_names = [
        "Aibek Sarsenov", "Aida Nurgaliyeva", "Alikhan Tolegen", "Amina Zhaksylyk", "Aruzhan Kassen",
        "Asel Mukan", "Askar Bekturov", "Ayan Zhumabay", "Bakyt Ermek", "Danel Akhmet",
        "Diana Abilova", "Dias Kairat", "Dinara Saparova", "Eldar Bek", "Elmira Kazybek",
        "Erasyl Tursyn", "Farida Omarova", "Gulmira Ibrayeva", "Ilyas Sadyk", "Inkar Alimova",
        "Islam Nurtay", "Kamila Balgabek", "Karina Dulat", "Madina Serik", "Miras Akhan",
        "Nurlan Aitbay", "Raushan Kenzhe", "Rustem Bayazit", "Samal Altynbek", "Sanjar Malikov",
        "Sholpan Kadir", "Sultan Zhanibek", "Tamara Ospan", "Timur Kairbek", "Tomiris Mukan",
        "Ulan Nurtay", "Yerlan Akhmet", "Zhanar Mukhtar", "Zhanibek Saken", "Zhibek Aman",
        "Adil Dosan", "Aigerim Baur", "Aslan Toleu", "Dana Murat", "Daniyar Yessim",
        "Gulnaz Serik", "Marat Baimbet", "Nazerke Oral", "Olzhas Talgat", "Ramilya Daulet",
        "Saltanat Zharas", "Zarina Kudaibergen", "Zhasulan Kuandyk", "Akmaral Tursun", "Asem Tanat",
        "Bekzat Omar", "Damir Tulegen", "Aizhan Yerlan", "Arman Kenzhe", "Madina Oraz",
    ]
    programs = ["Computer Science", "Mathematics", "Engineering", "Economics", "Languages"]

    for title, author, genre in books:
        connection.execute(
            "INSERT INTO books(title, author, genre) VALUES (?, ?, ?)",
            (title, author, genre),
        )

    for i, name in enumerate(member_names):
        email = "student" + str(i + 1).zfill(3) + "@students.example.edu"
        program = programs[i % len(programs)]
        connection.execute(
            "INSERT INTO members(name, email, program) VALUES (?, ?, ?)",
            (name, email, program),
        )

    book_ids = [row[0] for row in connection.execute("SELECT book_id FROM books ORDER BY book_id")]
    member_ids = [row[0] for row in connection.execute("SELECT member_id FROM members ORDER BY member_id")]
    loan_counts = [14, 11, 9, 8, 6, 5, 4, 4, 3, 3, 3] + [2] * 10 + [1] * 10
    random.seed(17)
    for book_index, count in enumerate(loan_counts):
        book_id = book_ids[book_index]
        for copy_number in range(count):
            is_current_loan = copy_number == count - 1 and book_index < 25
            member_id = random.choice(member_ids)
            if is_current_loan:
                borrowed_on = SAMPLE_DAY - timedelta(days=random.randint(1, 12))
                returned_on = None
            else:
                borrowed_on = SAMPLE_DAY - timedelta(days=random.randint(20, 180))
                returned_on = borrowed_on + timedelta(days=random.randint(2, 14))
            due_on = borrowed_on + timedelta(days=14)
            connection.execute(
                """INSERT INTO borrowings(book_id, member_id, borrowed_on, due_on, returned_on)
                   VALUES (?, ?, ?, ?, ?)""",
                (book_id, member_id, borrowed_on.isoformat(), due_on.isoformat(),
                 returned_on.isoformat() if returned_on else None),
            )
        if book_index < 25:
            connection.execute("UPDATE books SET available=0 WHERE book_id=?", (book_id,))

    connection.commit()


def get_number(message):
    try:
        return int(input(message))
    except ValueError:
        print("Please enter a number.")
        return None


def add_book(connection):
    title = input("Book title: ").strip()
    author = input("Author: ").strip()
    genre = input("Genre: ").strip()
    if title == "" or author == "" or genre == "":
        print("Title, author, and genre are required.")
        return
    connection.execute(
        "INSERT INTO books(title, author, genre) VALUES (?, ?, ?)",
        (title, author, genre),
    )
    connection.commit()
    print("Book added.")


def add_member(connection):
    name = input("Member name: ").strip()
    email = input("Member email: ").strip()
    program = input("Study program: ").strip()
    if name == "" or program == "" or re.fullmatch(EMAIL_PATTERN, email) is None:
        print("Enter a name, study program, and valid email address.")
        return
    try:
        connection.execute(
            "INSERT INTO members(name, email, program) VALUES (?, ?, ?)",
            (name, email, program),
        )
        connection.commit()
        print("Member added.")
    except sqlite3.IntegrityError:
        print("That email is already registered.")


def show_books(connection, available_only=False):
    if available_only:
        rows = connection.execute(
            "SELECT book_id, title, author, genre, available FROM books WHERE available=1 ORDER BY title"
        )
    else:
        rows = connection.execute(
            "SELECT book_id, title, author, genre, available FROM books ORDER BY title"
        )
    print(f"{'ID':<4} {'TITLE':<37} {'AUTHOR':<28} {'GENRE':<18} AVAILABLE")
    for row in rows:
        print(Book(row[0], row[1], row[2], row[3], row[4]))


def show_members(connection):
    rows = connection.execute("SELECT member_id, name, email, program FROM members ORDER BY name")
    print(f"{'ID':<4} {'NAME':<25} {'EMAIL':<38} PROGRAM")
    for row in rows:
        print(Member(row[0], row[1], row[2], row[3]))


def show_borrowings(connection):
    rows = connection.execute("""
        SELECT borrowings.borrowing_id, books.title, members.name,
               borrowings.borrowed_on, borrowings.due_on, borrowings.returned_on
        FROM borrowings JOIN books ON borrowings.book_id=books.book_id
        JOIN members ON borrowings.member_id=members.member_id
        ORDER BY borrowings.borrowed_on DESC
    """)
    print("ID  | BOOK | MEMBER | BORROWED | DUE | RETURNED")
    for row in rows:
        returned = row[5] if row[5] else "Not returned"
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {returned}")


def display_records(connection):
    choice = input("Display (b)ooks, (m)embers, or bo(r)rowings? ").strip().lower()
    if choice == "b":
        show_books(connection)
    elif choice == "m":
        show_members(connection)
    elif choice == "r":
        show_borrowings(connection)
    else:
        print("Choose b, m, or r.")


def borrow_book(connection):
    book_id = get_number("Book ID: ")
    member_id = get_number("Member ID: ")
    if book_id is None or member_id is None:
        return
    book = connection.execute("SELECT available FROM books WHERE book_id=?", (book_id,)).fetchone()
    member = connection.execute("SELECT member_id FROM members WHERE member_id=?", (member_id,)).fetchone()
    if book is None or member is None:
        print("Book or member was not found.")
    elif book[0] == 0:
        print("That book is already borrowed.")
    else:
        borrowed_on = date.today()
        due_on = borrowed_on + timedelta(days=14)
        connection.execute(
            "INSERT INTO borrowings(book_id, member_id, borrowed_on, due_on) VALUES (?, ?, ?, ?)",
            (book_id, member_id, borrowed_on.isoformat(), due_on.isoformat()),
        )
        connection.execute("UPDATE books SET available=0 WHERE book_id=?", (book_id,))
        connection.commit()
        print("Borrowing saved. Due date:", due_on.isoformat())


def search_records(connection):
    choice = input("Search (b)ooks or (m)embers? ").strip().lower()
    if choice == "b":
        title = input("Book title contains: ").strip()
        rows = connection.execute(
            "SELECT book_id, title, author, genre, available FROM books WHERE title LIKE ? ORDER BY title",
            ("%" + title + "%",),
        )
        found = False
        for row in rows:
            print(Book(row[0], row[1], row[2], row[3], row[4]))
            found = True
        if not found:
            print("No books found.")
    elif choice == "m":
        search = input("Member name or ID: ").strip()
        rows = connection.execute(
            "SELECT member_id, name, email, program FROM members WHERE name LIKE ? OR CAST(member_id AS TEXT)=?",
            ("%" + search + "%", search),
        )
        found = False
        for row in rows:
            print(Member(row[0], row[1], row[2], row[3]))
            found = True
        if not found:
            print("No members found.")
    else:
        print("Choose b or m.")


def update_book(connection):
    book_id = get_number("Book ID to update: ")
    if book_id is None:
        return
    title = input("New title: ").strip()
    author = input("New author: ").strip()
    genre = input("New genre: ").strip()
    if title == "" or author == "" or genre == "":
        print("Title, author, and genre are required.")
        return
    cursor = connection.execute(
        "UPDATE books SET title=?, author=?, genre=? WHERE book_id=?",
        (title, author, genre, book_id),
    )
    connection.commit()
    print("Book updated." if cursor.rowcount else "Book not found.")


def delete_record(connection):
    choice = input("Delete a (b)ook or (c)ancel a borrowing? ").strip().lower()
    record_id = get_number("ID: ")
    if record_id is None:
        return
    if choice == "b":
        cursor = connection.execute("DELETE FROM books WHERE book_id=?", (record_id,))
        connection.commit()
        print("Book deleted." if cursor.rowcount else "Book not found.")
    elif choice == "c":
        row = connection.execute(
            "SELECT book_id, returned_on FROM borrowings WHERE borrowing_id=?", (record_id,)
        ).fetchone()
        if row is None:
            print("Borrowing not found.")
        else:
            connection.execute("DELETE FROM borrowings WHERE borrowing_id=?", (record_id,))
            if row[1] is None:
                connection.execute("UPDATE books SET available=1 WHERE book_id=?", (row[0],))
            connection.commit()
            print("Borrowing cancelled.")
    else:
        print("Choose b or c.")


def return_book(connection):
    borrowing_id = get_number("Borrowing ID to return: ")
    if borrowing_id is None:
        return
    row = connection.execute(
        "SELECT book_id, returned_on FROM borrowings WHERE borrowing_id=?", (borrowing_id,)
    ).fetchone()
    if row is None:
        print("Borrowing not found.")
    elif row[1] is not None:
        print("This book has already been returned.")
    else:
        connection.execute(
            "UPDATE borrowings SET returned_on=? WHERE borrowing_id=?",
            (date.today().isoformat(), borrowing_id),
        )
        connection.execute("UPDATE books SET available=1 WHERE book_id=?", (row[0],))
        connection.commit()
        print("Book returned.")


def show_statistics(connection):
    total = connection.execute("SELECT COUNT(*) FROM borrowings").fetchone()[0]
    active = connection.execute("SELECT COUNT(*) FROM borrowings WHERE returned_on IS NULL").fetchone()[0]
    top_book = connection.execute("""
        SELECT books.title, COUNT(*) AS total
        FROM borrowings JOIN books ON borrowings.book_id=books.book_id
        GROUP BY books.book_id ORDER BY total DESC, books.title LIMIT 1
    """).fetchone()
    print("Total borrowing records:", total)
    print("Books currently borrowed:", active)
    if top_book:
        print("Most borrowed book:", top_book[0], "-", top_book[1], "times")


def export_results(connection):
    total = connection.execute("SELECT COUNT(*) FROM borrowings").fetchone()[0]
    active = connection.execute("SELECT COUNT(*) FROM borrowings WHERE returned_on IS NULL").fetchone()[0]
    top_book = connection.execute("""
        SELECT books.title, COUNT(*) AS total
        FROM borrowings JOIN books ON borrowings.book_id=books.book_id
        GROUP BY books.book_id ORDER BY total DESC, books.title LIMIT 1
    """).fetchone()
    with open(RESULTS, "w", encoding="utf-8") as file:
        file.write("UNIVERSITY LIBRARY SUMMARY\n")
        file.write("Books: " + str(connection.execute("SELECT COUNT(*) FROM books").fetchone()[0]) + "\n")
        file.write("Members: " + str(connection.execute("SELECT COUNT(*) FROM members").fetchone()[0]) + "\n")
        file.write("Borrowing records: " + str(total) + "\n")
        file.write("Current loans: " + str(active) + "\n")
        if top_book:
            file.write("Most borrowed book: " + top_book[0] + " (" + str(top_book[1]) + " loans)\n")
        file.write("\nBORROWING HISTORY\n")
        rows = connection.execute("""
            SELECT borrowings.borrowing_id, books.title, members.name,
                   borrowings.borrowed_on, borrowings.due_on, borrowings.returned_on
            FROM borrowings JOIN books ON borrowings.book_id=books.book_id
            JOIN members ON borrowings.member_id=members.member_id
            ORDER BY borrowings.borrowed_on DESC
        """)
        for row in rows:
            returned = row[5] if row[5] else "Not returned"
            file.write(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | due {row[4]} | {returned}\n")
    print("Results saved to results.txt.")


def show_menu():
    print("""
UNIVERSITY LIBRARY SYSTEM
1. Add a book
2. Add a member
3. Borrow a book
4. Display books, members, or borrowings
5. Search books or members
6. Show available books
7. Update a book
8. Delete a book or cancel a borrowing
9. Return a book
10. Show statistics
11. Export results.txt
0. Exit
""")


def main():
    connection = connect_database()
    create_tables(connection)
    add_sample_data(connection)
    print("Library dataset ready: 50 books, 60 members, and 100 borrowing records.")

    while True:
        show_menu()
        choice = input("Choose an option: ").strip()
        if choice == "1":
            add_book(connection)
        elif choice == "2":
            add_member(connection)
        elif choice == "3":
            borrow_book(connection)
        elif choice == "4":
            display_records(connection)
        elif choice == "5":
            search_records(connection)
        elif choice == "6":
            show_books(connection, available_only=True)
        elif choice == "7":
            update_book(connection)
        elif choice == "8":
            delete_record(connection)
        elif choice == "9":
            return_book(connection)
        elif choice == "10":
            show_statistics(connection)
        elif choice == "11":
            export_results(connection)
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Choose a number from the menu.")

    connection.close()


if __name__ == "__main__":
    main()
