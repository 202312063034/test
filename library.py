"""
图书管理系统 - 核心模块
"""
import json
import os
from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"


class Book:
    """图书类"""

    def __init__(self, book_id: int, title: str, author: str, isbn: str, quantity: int = 1):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.quantity = quantity          # 馆藏总量
        self.available = quantity         # 当前可借数量

    def to_dict(self) -> dict:
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "quantity": self.quantity,
            "available": self.available,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        book = cls(
            book_id=data["book_id"],
            title=data["title"],
            author=data["author"],
            isbn=data["isbn"],
            quantity=data["quantity"],
        )
        book.available = data["available"]
        return book

    def __repr__(self) -> str:
        return (
            f"[{self.book_id}] 《{self.title}》 作者: {self.author} "
            f"ISBN: {self.isbn} 馆藏: {self.quantity} 可借: {self.available}"
        )


class BorrowRecord:
    """借阅记录类"""

    def __init__(self, record_id: int, book_id: int, borrower: str, borrow_date: str):
        self.record_id = record_id
        self.book_id = book_id
        self.borrower = borrower
        self.borrow_date = borrow_date
        self.return_date: str = ""

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "book_id": self.book_id,
            "borrower": self.borrower,
            "borrow_date": self.borrow_date,
            "return_date": self.return_date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BorrowRecord":
        record = cls(
            record_id=data["record_id"],
            book_id=data["book_id"],
            borrower=data["borrower"],
            borrow_date=data["borrow_date"],
        )
        record.return_date = data.get("return_date", "")
        return record

    def __repr__(self) -> str:
        status = f"已归还({self.return_date})" if self.return_date else "借阅中"
        return (
            f"[记录{self.record_id}] 图书ID: {self.book_id} 借阅人: {self.borrower} "
            f"借出日期: {self.borrow_date} 状态: {status}"
        )


class Library:
    """图书馆管理类"""

    def __init__(self, data_file: str = "library_data.json"):
        self.data_file = data_file
        self.books: dict[int, Book] = {}
        self.records: list[BorrowRecord] = []
        self._next_book_id = 1
        self._next_record_id = 1
        self._load()

    # ------------------------------------------------------------------
    # 持久化
    # ------------------------------------------------------------------
    def _load(self) -> None:
        if not os.path.exists(self.data_file):
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for b in data.get("books", []):
                book = Book.from_dict(b)
                self.books[book.book_id] = book
            for r in data.get("records", []):
                self.records.append(BorrowRecord.from_dict(r))
            self._next_book_id = data.get("next_book_id", 1)
            self._next_record_id = data.get("next_record_id", 1)
        except (json.JSONDecodeError, KeyError):
            pass

    def save(self) -> None:
        data = {
            "books": [b.to_dict() for b in self.books.values()],
            "records": [r.to_dict() for r in self.records],
            "next_book_id": self._next_book_id,
            "next_record_id": self._next_record_id,
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # 图书管理
    # ------------------------------------------------------------------
    def add_book(self, title: str, author: str, isbn: str, quantity: int = 1) -> Book:
        """添加图书"""
        if not title or not author or not isbn:
            raise ValueError("书名、作者和ISBN均不能为空")
        if quantity < 1:
            raise ValueError("馆藏数量必须大于0")
        for book in self.books.values():
            if book.isbn == isbn:
                raise ValueError(f"ISBN {isbn} 已存在，请勿重复添加")
        book = Book(self._next_book_id, title, author, isbn, quantity)
        self.books[book.book_id] = book
        self._next_book_id += 1
        self.save()
        return book

    def remove_book(self, book_id: int) -> Book:
        """删除图书"""
        book = self._get_book(book_id)
        if book.available < book.quantity:
            raise ValueError(f"图书《{book.title}》尚有未归还副本，无法删除")
        del self.books[book_id]
        self.save()
        return book

    def update_book(self, book_id: int, title: str = None, author: str = None,
                    isbn: str = None, quantity: int = None) -> Book:
        """修改图书信息"""
        book = self._get_book(book_id)
        if title is not None:
            book.title = title
        if author is not None:
            book.author = author
        if isbn is not None:
            for b in self.books.values():
                if b.isbn == isbn and b.book_id != book_id:
                    raise ValueError(f"ISBN {isbn} 已被其他图书使用")
            book.isbn = isbn
        if quantity is not None:
            if quantity < 1:
                raise ValueError("馆藏数量必须大于0")
            borrowed = book.quantity - book.available
            if quantity < borrowed:
                raise ValueError(f"新数量({quantity})小于当前已借出数量({borrowed})")
            book.available = quantity - borrowed
            book.quantity = quantity
        self.save()
        return book

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------
    def list_books(self) -> list[Book]:
        """列出所有图书"""
        return list(self.books.values())

    def search_by_title(self, keyword: str) -> list[Book]:
        """按书名搜索"""
        keyword = keyword.strip().lower()
        return [b for b in self.books.values() if keyword in b.title.lower()]

    def search_by_author(self, keyword: str) -> list[Book]:
        """按作者搜索"""
        keyword = keyword.strip().lower()
        return [b for b in self.books.values() if keyword in b.author.lower()]

    def search_by_isbn(self, isbn: str) -> Book | None:
        """按ISBN搜索"""
        for book in self.books.values():
            if book.isbn == isbn.strip():
                return book
        return None

    # ------------------------------------------------------------------
    # 借还管理
    # ------------------------------------------------------------------
    def borrow_book(self, book_id: int, borrower: str) -> BorrowRecord:
        """借出图书"""
        if not borrower or not borrower.strip():
            raise ValueError("借阅人姓名不能为空")
        book = self._get_book(book_id)
        if book.available <= 0:
            raise ValueError(f"图书《{book.title}》当前无可借副本")
        book.available -= 1
        record = BorrowRecord(
            record_id=self._next_record_id,
            book_id=book_id,
            borrower=borrower.strip(),
            borrow_date=datetime.now().strftime(DATE_FORMAT),
        )
        self._next_record_id += 1
        self.records.append(record)
        self.save()
        return record

    def return_book(self, record_id: int) -> BorrowRecord:
        """归还图书"""
        record = self._get_record(record_id)
        if record.return_date:
            raise ValueError(f"借阅记录 {record_id} 已于 {record.return_date} 归还")
        book = self._get_book(record.book_id)
        book.available += 1
        record.return_date = datetime.now().strftime(DATE_FORMAT)
        self.save()
        return record

    def list_borrow_records(self, borrower: str = None, book_id: int = None,
                            unreturned_only: bool = False) -> list[BorrowRecord]:
        """查询借阅记录"""
        result = self.records
        if borrower:
            result = [r for r in result if r.borrower == borrower]
        if book_id is not None:
            result = [r for r in result if r.book_id == book_id]
        if unreturned_only:
            result = [r for r in result if not r.return_date]
        return result

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    def _get_book(self, book_id: int) -> Book:
        book = self.books.get(book_id)
        if book is None:
            raise ValueError(f"图书ID {book_id} 不存在")
        return book

    def _get_record(self, record_id: int) -> BorrowRecord:
        for record in self.records:
            if record.record_id == record_id:
                return record
        raise ValueError(f"借阅记录ID {record_id} 不存在")
