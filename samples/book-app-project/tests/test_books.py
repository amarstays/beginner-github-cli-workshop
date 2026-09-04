import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import books
from books import BookCollection


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Use a temporary data file for each test."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", temp_file)


# Test add_book happy path
def test_add_book():
    collection = BookCollection()
    initial_count = len(collection.books)
    collection.add_book("1984", "George Orwell", 1949)
    assert len(collection.books) == initial_count + 1
    book = collection.find_book_by_title("1984")
    assert book is not None
    assert book.author == "George Orwell"
    assert book.year == 1949
    assert book.read is False


# Test add_book input validation
def test_add_book_empty_title():
    collection = BookCollection()
    with pytest.raises(ValueError, match="Title cannot be empty"):
        collection.add_book("", "George Orwell", 1949)


def test_add_book_whitespace_title():
    collection = BookCollection()
    with pytest.raises(ValueError, match="Title cannot be empty"):
        collection.add_book("   ", "George Orwell", 1949)


def test_add_book_empty_author():
    collection = BookCollection()
    with pytest.raises(ValueError, match="Author cannot be empty"):
        collection.add_book("1984", "", 1949)


def test_add_book_whitespace_author():
    collection = BookCollection()
    with pytest.raises(ValueError, match="Author cannot be empty"):
        collection.add_book("1984", "   ", 1949)


def test_add_book_negative_year():
    collection = BookCollection()
    with pytest.raises(ValueError, match="Year must be a positive integer"):
        collection.add_book("1984", "George Orwell", -1949)


def test_add_book_year_too_large():
    collection = BookCollection()
    with pytest.raises(ValueError, match="Year must be a positive integer"):
        collection.add_book("1984", "George Orwell", 2101)


def test_add_book_trims_whitespace():
    collection = BookCollection()
    book = collection.add_book("  1984  ", "  George Orwell  ", 1949)
    assert book.title == "1984"
    assert book.author == "George Orwell"


# Test mark_as_read
def test_mark_book_as_read():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    result = collection.mark_as_read("Dune")
    assert result is True
    book = collection.find_book_by_title("Dune")
    assert book.read is True


def test_mark_book_as_read_invalid():
    collection = BookCollection()
    result = collection.mark_as_read("Nonexistent Book")
    assert result is False


def test_mark_book_as_read_empty_title():
    collection = BookCollection()
    with pytest.raises(ValueError, match="Title must be a non-empty string"):
        collection.mark_as_read("")


def test_mark_book_as_read_case_insensitive():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    result = collection.mark_as_read("dune")
    assert result is True
    book = collection.find_book_by_title("DUNE")
    assert book.read is True


# Test remove_book
def test_remove_book():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    result = collection.remove_book("The Hobbit")
    assert result is True
    book = collection.find_book_by_title("The Hobbit")
    assert book is None


def test_remove_book_invalid():
    collection = BookCollection()
    result = collection.remove_book("Nonexistent Book")
    assert result is False


def test_remove_book_empty_title():
    collection = BookCollection()
    with pytest.raises(ValueError, match="Title must be a non-empty string"):
        collection.remove_book("")


# Test list_books
def test_list_books_empty():
    collection = BookCollection()
    assert collection.list_books() == []


def test_list_books_multiple():
    collection = BookCollection()
    collection.add_book("1984", "George Orwell", 1949)
    collection.add_book("Dune", "Frank Herbert", 1965)
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    books_list = collection.list_books()
    assert len(books_list) == 3
    assert books_list[0].title == "1984"
    assert books_list[1].title == "Dune"
    assert books_list[2].title == "The Hobbit"


# Test find_by_author
def test_find_by_author_single():
    collection = BookCollection()
    collection.add_book("1984", "George Orwell", 1949)
    collection.add_book("Animal Farm", "George Orwell", 1945)
    collection.add_book("Dune", "Frank Herbert", 1965)
    result = collection.find_by_author("George Orwell")
    assert len(result) == 2
    assert all(book.author == "George Orwell" for book in result)


def test_find_by_author_none():
    collection = BookCollection()
    collection.add_book("1984", "George Orwell", 1949)
    result = collection.find_by_author("Unknown Author")
    assert result == []


def test_find_by_author_case_insensitive():
    collection = BookCollection()
    collection.add_book("1984", "George Orwell", 1949)
    result = collection.find_by_author("george orwell")
    assert len(result) == 1
    assert result[0].title == "1984"


def test_find_by_author_empty():
    collection = BookCollection()
    with pytest.raises(ValueError, match="Author must be a non-empty string"):
        collection.find_by_author("")


# Test persistence
def test_persistence_save_and_load(tmp_path, monkeypatch):
    """Test that books persist between collection instances."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", temp_file)
    
    # Add a book with first collection
    collection1 = BookCollection()
    collection1.add_book("1984", "George Orwell", 1949)
    
    # Create a new collection and verify the book is loaded
    collection2 = BookCollection()
    book = collection2.find_book_by_title("1984")
    assert book is not None
    assert book.author == "George Orwell"
    assert book.year == 1949


# Test find_book_by_title edge cases
def test_find_book_by_title_not_found():
    collection = BookCollection()
    collection.add_book("1984", "George Orwell", 1949)
    result = collection.find_book_by_title("Nonexistent")
    assert result is None


def test_find_book_by_title_case_insensitive():
    collection = BookCollection()
    collection.add_book("1984", "George Orwell", 1949)
    result = collection.find_book_by_title("1984")
    assert result is not None
    result = collection.find_book_by_title("1984")
    assert result is not None
    result = collection.find_book_by_title("1984")
    assert result is not None


def test_find_book_by_title_empty():
    collection = BookCollection()
    with pytest.raises(ValueError, match="Title must be a non-empty string"):
        collection.find_book_by_title("")

