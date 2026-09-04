import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

DATA_FILE: Path = Path(__file__).with_name("data.json")


@dataclass
class Book:
    title: str
    author: str
    year: int
    read: bool = False


class BookCollection:
    def __init__(self):
        self.books: List[Book] = []
        self.load_books()

    def load_books(self):
        """Load books from the JSON file if it exists."""
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.books = [Book(**b) for b in data]
        except FileNotFoundError:
            self.books = []
        except json.JSONDecodeError:
            print("Warning: data.json is corrupted. Starting with empty collection.")
            self.books = []

    def save_books(self):
        """Save the current book collection to JSON."""
        with open(DATA_FILE, "w") as f:
            json.dump([asdict(b) for b in self.books], f, indent=2)

    def add_book(self, title: str, author: str, year: int) -> Book:
        if not title or not isinstance(title, str) or not title.strip():
            raise ValueError("Title cannot be empty")
        if not author or not isinstance(author, str) or not author.strip():
            raise ValueError("Author cannot be empty")
        if not isinstance(year, int) or year < 0 or year > 2100:
            raise ValueError("Year must be a positive integer not exceeding 2100")
        
        book = Book(title=title.strip(), author=author.strip(), year=year)
        self.books.append(book)
        self.save_books()
        return book

    def list_books(self) -> List[Book]:
        return self.books

    def find_book_by_title(self, title: str) -> Optional[Book]:
        if not title or not isinstance(title, str):
            raise ValueError("Title must be a non-empty string")
        for book in self.books:
            if book.title.lower() == title.lower():
                return book
        return None

    def mark_as_read(self, title: str) -> bool:
        if not title or not isinstance(title, str):
            raise ValueError("Title must be a non-empty string")
        book = self.find_book_by_title(title)
        if book:
            book.read = True
            self.save_books()
            return True
        return False

    def remove_book(self, title: str) -> bool:
        """Remove a book by title."""
        if not title or not isinstance(title, str):
            raise ValueError("Title must be a non-empty string")
        book = self.find_book_by_title(title)
        if book:
            self.books.remove(book)
            self.save_books()
            return True
        return False

    def find_by_author(self, author: str) -> List[Book]:
        """Find all books by a given author."""
        if not author or not isinstance(author, str):
            raise ValueError("Author must be a non-empty string")
        return [b for b in self.books if b.author.lower() == author.lower()]
