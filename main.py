"""Console-based Library Management System for the Python midterm project."""

from __future__ import annotations

import csv
import random
import re
import sqlite3
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "project.db"
RESULTS_PATH = BASE_DIR / "results.csv"
ISBN_PATTERN = re.compile(r"^(?:\d{9}[\dX]|\d{13})$")
EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}$")


@dataclass
class Book:
    book_id: int
    isbn: str
    title: str
    author: str
    genre: str
    published_year: int
    available: bool


@dataclass
class Member:
    member_id: int
    full_name: str
    email: str
    phone: str


class LibraryManager:
    """Database-backed operations; the connection is encapsulated by the class."""

    def __init__(self, db_path: Path = DB_PATH):
        self._db_path = Path(db_path)
        self._connection = sqlite3.connect(self._db_path)
        self._connection.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        with self._connection:
            self._connection.executescript("""
                PRAGMA foreign_keys = ON;
                CREATE TABLE IF NOT EXISTS books (
                    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isbn TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    published_year INTEGER NOT NULL CHECK(published_year BETWEEN 1000 AND 2100),
                    available INTEGER NOT NULL DEFAULT 1 CHECK(available IN (0, 1))
                );
                CREATE TABLE IF NOT EXISTS members (
                    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS borrowings (
                    borrowing_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
                    member_id INTEGER NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
                    borrowed_on TEXT NOT NULL,
                    due_on TEXT NOT NULL,
                    returned_on TEXT,
                    CHECK(due_on >= borrowed_on)
                );
            """)

    def close(self) -> None:
        self._connection.close()

    def seed_demo_data(self) -> None:
        """Create a repeatable demo dataset with Random (seeded for consistency)."""
        if self._connection.execute("SELECT COUNT(*) FROM books").fetchone()[0] >= 50:
            return
        rng = random.Random(2026)
        first_names = ["Amina", "Daniel", "Sara", "Arman", "Maya", "Timur", "Leila", "Noah", "Dina", "Ethan"]
        last_names = ["Brown", "Kim", "Sato", "Patel", "Garcia", "Ali", "Chen", "Smith", "Ivanov", "Jones"]
        genres = ["Fiction", "Science", "History", "Mystery", "Technology", "Fantasy"]
        titles = [
            "The Quiet Library", "A Map of Stars", "Python in Practice", "The Last Archive", "City of Paper",
            "Modern Data Systems", "River of Time", "The Hidden Garden", "A Study of Light", "Across the Steppe",
            "The Blue Equation", "Small Worlds", "The Open Window", "Stories of Tomorrow", "The Copper Key",
            "A Better Algorithm", "Winter Letters", "The Glass Mountain", "Notes from Earth", "The Long Journey",
        ]
        with self._connection:
            for i in range(50):
                isbn = f"978{6000000000 + i:010d}"
                self._connection.execute(
                    "INSERT OR IGNORE INTO books(isbn,title,author,genre,published_year) VALUES(?,?,?,?,?)",
                    (isbn, f"{titles[i % len(titles)]} {i // len(titles) + 1}",
                     f"{first_names[i % len(first_names)]} {last_names[(i * 3) % len(last_names)]}",
                     genres[i % len(genres)], 1980 + (i * 7) % 45),
                )
            for i in range(30):
                name = f"{first_names[i % len(first_names)]} {last_names[(i * 7) % len(last_names)]}"
                email = f"member{i + 1:02d}@example.edu"
                self._connection.execute(
                    "INSERT OR IGNORE INTO members(full_name,email,phone) VALUES(?,?,?)",
                    (name, email, f"+7 700 {100 + i:03d} {20 + i:02d} {10 + i:02d}"),
                )
            book_ids = [r[0] for r in self._connection.execute("SELECT book_id FROM books ORDER BY book_id")]
            member_ids = [r[0] for r in self._connection.execute("SELECT member_id FROM members ORDER BY member_id")]
            existing = self._connection.execute("SELECT COUNT(*) FROM borrowings").fetchone()[0]
            for i in range(existing, 30):
                borrowed = date(2026, 9, 1) + timedelta(days=i)
                book_id = book_ids[(i * 7) % len(book_ids)]
                member_id = member_ids[(i * 3) % len(member_ids)]
                returned = (borrowed + timedelta(days=rng.randint(3, 14))).isoformat() if i % 3 == 0 else None
                self._connection.execute(
                    "INSERT INTO borrowings(book_id,member_id,borrowed_on,due_on,returned_on) VALUES(?,?,?,?,?)",
                    (book_id, member_id, borrowed.isoformat(), (borrowed + timedelta(days=14)).isoformat(), returned),
                )
            self._connection.execute(
                "UPDATE books SET available = CASE WHEN book_id IN (SELECT book_id FROM borrowings WHERE returned_on IS NULL) THEN 0 ELSE 1 END"
            )

    def add_book(self, isbn: str, title: str, author: str, genre: str, year: int) -> int:
        self._validate_isbn(isbn)
        if not title.strip() or not author.strip() or not genre.strip():
            raise ValueError("Title, author, and genre cannot be empty.")
        if not 1000 <= year <= 2100:
            raise ValueError("Published year must be between 1000 and 2100.")
        with self._connection:
            cur = self._connection.execute(
                "INSERT INTO books(isbn,title,author,genre,published_year) VALUES(?,?,?,?,?)",
                (isbn, title.strip(), author.strip(), genre.strip(), year),
            )
        return cur.lastrowid

    def add_member(self, name: str, email: str, phone: str) -> int:
        if not name.strip() or not phone.strip() or not EMAIL_PATTERN.fullmatch(email.strip()):
            raise ValueError("Enter a name, phone number, and valid email address.")
        with self._connection:
            cur = self._connection.execute(
                "INSERT INTO members(full_name,email,phone) VALUES(?,?,?)",
                (name.strip(), email.strip(), phone.strip()),
            )
        return cur.lastrowid

    def add_borrowing(self, book_id: int, member_id: int, borrowed_on: date | None = None) -> int:
        borrowed_on = borrowed_on or date.today()
        book = self._connection.execute("SELECT available FROM books WHERE book_id=?", (book_id,)).fetchone()
        member = self._connection.execute("SELECT 1 FROM members WHERE member_id=?", (member_id,)).fetchone()
        if not book or not member:
            raise ValueError("Book or member ID was not found.")
        if not book["available"]:
            raise ValueError("That book is currently borrowed.")
        with self._connection:
            cur = self._connection.execute(
                "INSERT INTO borrowings(book_id,member_id,borrowed_on,due_on) VALUES(?,?,?,?)",
                (book_id, member_id, borrowed_on.isoformat(), (borrowed_on + timedelta(days=14)).isoformat()),
            )
            self._connection.execute("UPDATE books SET available=0 WHERE book_id=?", (book_id,))
        return cur.lastrowid

    def list_books(self) -> list[sqlite3.Row]:
        return self._connection.execute("SELECT * FROM books ORDER BY title").fetchall()

    def list_members(self) -> list[sqlite3.Row]:
        return self._connection.execute("SELECT * FROM members ORDER BY full_name").fetchall()

    def list_borrowings(self) -> list[sqlite3.Row]:
        return self._connection.execute("""SELECT br.borrowing_id,b.title,m.full_name,br.borrowed_on,br.due_on,
            COALESCE(br.returned_on,'Not returned') AS returned_on
            FROM borrowings br JOIN books b USING(book_id) JOIN members m USING(member_id)
            ORDER BY br.borrowing_id""").fetchall()

    def search_books(self, title: str) -> list[sqlite3.Row]:
        return self._connection.execute("SELECT * FROM books WHERE title LIKE ? ORDER BY title", (f"%{title}%",)).fetchall()

    def search_members(self, query: str) -> list[sqlite3.Row]:
        return self._connection.execute(
            "SELECT * FROM members WHERE full_name LIKE ? OR CAST(member_id AS TEXT)=? ORDER BY full_name",
            (f"%{query}%", query),
        ).fetchall()

    def available_books(self) -> list[sqlite3.Row]:
        return self._connection.execute("SELECT * FROM books WHERE available=1 ORDER BY title").fetchall()

    def update_book(self, book_id: int, title: str, author: str, genre: str, year: int) -> None:
        if not title.strip() or not author.strip() or not genre.strip() or not 1000 <= year <= 2100:
            raise ValueError("Provide non-empty fields and a year from 1000 to 2100.")
        with self._connection:
            cur = self._connection.execute(
                "UPDATE books SET title=?,author=?,genre=?,published_year=? WHERE book_id=?",
                (title.strip(), author.strip(), genre.strip(), year, book_id),
            )
        if cur.rowcount == 0:
            raise ValueError("Book ID was not found.")

    def delete_book(self, book_id: int) -> None:
        with self._connection:
            cur = self._connection.execute("DELETE FROM books WHERE book_id=?", (book_id,))
        if cur.rowcount == 0:
            raise ValueError("Book ID was not found.")

    def return_borrowing(self, borrowing_id: int) -> None:
        row = self._connection.execute("SELECT book_id,returned_on FROM borrowings WHERE borrowing_id=?", (borrowing_id,)).fetchone()
        if not row:
            raise ValueError("Borrowing ID was not found.")
        if row["returned_on"]:
            raise ValueError("This book has already been returned.")
        with self._connection:
            self._connection.execute("UPDATE borrowings SET returned_on=? WHERE borrowing_id=?", (date.today().isoformat(), borrowing_id))
            self._connection.execute("UPDATE books SET available=1 WHERE book_id=?", (row["book_id"],))

    def delete_borrowing(self, borrowing_id: int) -> None:
        row = self._connection.execute("SELECT book_id,returned_on FROM borrowings WHERE borrowing_id=?", (borrowing_id,)).fetchone()
        if not row:
            raise ValueError("Borrowing ID was not found.")
        with self._connection:
            self._connection.execute("DELETE FROM borrowings WHERE borrowing_id=?", (borrowing_id,))
            if not row["returned_on"]:
                self._connection.execute("UPDATE books SET available=1 WHERE book_id=?", (row["book_id"],))

    def statistics(self) -> dict[str, object]:
        total = self._connection.execute("SELECT COUNT(*) FROM borrowings").fetchone()[0]
        top = self._connection.execute("""SELECT b.title,COUNT(*) AS borrow_count FROM borrowings br
            JOIN books b USING(book_id) GROUP BY b.book_id ORDER BY borrow_count DESC,b.title LIMIT 1""").fetchone()
        active = self._connection.execute("SELECT COUNT(*) FROM borrowings WHERE returned_on IS NULL").fetchone()[0]
        return {"book_count": self._connection.execute("SELECT COUNT(*) FROM books").fetchone()[0],
                "member_count": self._connection.execute("SELECT COUNT(*) FROM members").fetchone()[0],
                "borrowing_count": total, "active_borrowings": active,
                "most_borrowed_title": top["title"] if top else "None",
                "most_borrowed_count": top["borrow_count"] if top else 0}

    def export_results(self, path: Path = RESULTS_PATH) -> Path:
        stats = self.statistics()
        rows = self.list_borrowings()
        with Path(path).open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["LIBRARY MANAGEMENT SYSTEM SUMMARY"])
            writer.writerow(["Books", stats["book_count"]])
            writer.writerow(["Members", stats["member_count"]])
            writer.writerow(["Total borrowings", stats["borrowing_count"]])
            writer.writerow(["Active borrowings", stats["active_borrowings"]])
            writer.writerow(["Most borrowed book", stats["most_borrowed_title"], stats["most_borrowed_count"]])
            writer.writerow([])
            writer.writerow(["Borrowing ID", "Book", "Member", "Borrowed", "Due", "Returned"])
            writer.writerows([[r[c] for c in ("borrowing_id", "title", "full_name", "borrowed_on", "due_on", "returned_on")] for r in rows])
        return Path(path)

    @staticmethod
    def _validate_isbn(isbn: str) -> None:
        if not ISBN_PATTERN.fullmatch(isbn.strip()):
            raise ValueError("ISBN must contain 10 or 13 digits (the 10-digit form may end in X).")


def print_table(rows: Iterable[sqlite3.Row], columns: tuple[tuple[str, str], ...]) -> None:
    rows = list(rows)
    if not rows:
        print("No records found.")
        return
    widths = [max(len(label), *(len(str(row[key])) for row in rows)) for key, label in columns]
    print(" | ".join(label.ljust(width) for (_, label), width in zip(columns, widths)))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(" | ".join(str(row[key]).ljust(width) for (key, _), width in zip(columns, widths)))


def ask_int(prompt: str) -> int:
    try:
        return int(input(prompt).strip())
    except ValueError as exc:
        raise ValueError("Enter a whole number.") from exc


def show_menu() -> None:
    print("""
LIBRARY MANAGEMENT SYSTEM
1. Add book or member
2. Add borrowing
3. Display books, members, or borrowings
4. Search books or members
5. Show available books
6. Update a book
7. Delete a book or cancel a borrowing
8. Return a borrowed book
9. Show statistics
10. Export results.csv
0. Exit
""")


def run_app() -> None:
    library = LibraryManager()
    library.seed_demo_data()
    print("Library database ready. Demo dataset: 50 books, 30 members, 30 borrowings.")
    while True:
        show_menu()
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                kind = input("Add (b)ook or (m)ember? ").strip().lower()
                if kind == "b":
                    new_id = library.add_book(input("ISBN: "), input("Title: "), input("Author: "), input("Genre: "), ask_int("Published year: "))
                    print(f"Book added with ID {new_id}.")
                elif kind == "m":
                    new_id = library.add_member(input("Full name: "), input("Email: "), input("Phone: "))
                    print(f"Member added with ID {new_id}.")
                else:
                    print("Choose b or m.")
            elif choice == "2":
                print_table(library.available_books(), (("book_id", "ID"), ("title", "Title"), ("author", "Author")))
                borrowing_id = library.add_borrowing(ask_int("Book ID: "), ask_int("Member ID: "))
                print(f"Borrowing recorded with ID {borrowing_id}; due in 14 days.")
            elif choice == "3":
                kind = input("Display (b)ooks, (m)embers, or (r)ecords? ").strip().lower()
                if kind == "b": print_table(library.list_books(), (("book_id", "ID"), ("title", "Title"), ("author", "Author"), ("genre", "Genre"), ("available", "Available")))
                elif kind == "m": print_table(library.list_members(), (("member_id", "ID"), ("full_name", "Name"), ("email", "Email"), ("phone", "Phone")))
                elif kind == "r": print_table(library.list_borrowings(), (("borrowing_id", "ID"), ("title", "Book"), ("full_name", "Member"), ("borrowed_on", "Borrowed"), ("due_on", "Due"), ("returned_on", "Returned")))
                else: print("Choose b, m, or r.")
            elif choice == "4":
                kind = input("Search (b)ooks by title or (m)embers by name/ID? ").strip().lower()
                if kind == "b": print_table(library.search_books(input("Title contains: ")), (("book_id", "ID"), ("title", "Title"), ("author", "Author"), ("available", "Available")))
                elif kind == "m": print_table(library.search_members(input("Member name or ID: ")), (("member_id", "ID"), ("full_name", "Name"), ("email", "Email"), ("phone", "Phone")))
                else: print("Choose b or m.")
            elif choice == "5":
                print_table(library.available_books(), (("book_id", "ID"), ("title", "Title"), ("author", "Author"), ("genre", "Genre")))
            elif choice == "6":
                book_id = ask_int("Book ID to update: ")
                library.update_book(book_id, input("New title: "), input("New author: "), input("New genre: "), ask_int("New published year: "))
                print("Book updated.")
            elif choice == "7":
                kind = input("Delete (b)ook or cancel borrowing (r)? ").strip().lower()
                if kind == "b": library.delete_book(ask_int("Book ID: ")); print("Book deleted.")
                elif kind == "r": library.delete_borrowing(ask_int("Borrowing ID: ")); print("Borrowing cancelled.")
                else: print("Choose b or r.")
            elif choice == "8":
                library.return_borrowing(ask_int("Borrowing ID to return: "))
                print("Book marked as returned and available.")
            elif choice == "9":
                for label, value in library.statistics().items(): print(f"{label.replace('_',' ').title()}: {value}")
            elif choice == "10":
                print(f"Summary exported to {library.export_results()}.")
            elif choice == "0":
                print("Goodbye.")
                break
            else:
                print("Select a listed menu option.")
        except (ValueError, sqlite3.IntegrityError) as exc:
            print(f"Could not complete the request: {exc}")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
    library.close()


if __name__ == "__main__":
    run_app()
