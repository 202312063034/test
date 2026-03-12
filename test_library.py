"""
图书管理系统 - 单元测试
"""
import os
import tempfile
import unittest

from library import Book, BorrowRecord, Library


class TestBook(unittest.TestCase):
    def test_book_creation(self):
        book = Book(1, "Python编程", "张三", "978-3-16-148410-0", 3)
        self.assertEqual(book.book_id, 1)
        self.assertEqual(book.title, "Python编程")
        self.assertEqual(book.author, "张三")
        self.assertEqual(book.isbn, "978-3-16-148410-0")
        self.assertEqual(book.quantity, 3)
        self.assertEqual(book.available, 3)

    def test_book_to_dict_and_from_dict(self):
        book = Book(2, "数据结构", "李四", "978-0-13-468599-1", 2)
        book.available = 1
        d = book.to_dict()
        restored = Book.from_dict(d)
        self.assertEqual(restored.book_id, 2)
        self.assertEqual(restored.title, "数据结构")
        self.assertEqual(restored.available, 1)

    def test_book_repr(self):
        book = Book(3, "算法导论", "王五", "978-0-262-03384-8")
        self.assertIn("算法导论", repr(book))
        self.assertIn("王五", repr(book))


class TestLibraryBookManagement(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        os.unlink(self.tmp.name)
        self.lib = Library(data_file=self.tmp.name)

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def test_add_book(self):
        book = self.lib.add_book("Python编程", "张三", "ISBN-001", 2)
        self.assertEqual(book.title, "Python编程")
        self.assertEqual(book.quantity, 2)
        self.assertEqual(len(self.lib.list_books()), 1)

    def test_add_book_duplicate_isbn_raises(self):
        self.lib.add_book("书A", "作者A", "ISBN-DUP")
        with self.assertRaises(ValueError):
            self.lib.add_book("书B", "作者B", "ISBN-DUP")

    def test_add_book_empty_title_raises(self):
        with self.assertRaises(ValueError):
            self.lib.add_book("", "作者", "ISBN-X")

    def test_add_book_zero_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.lib.add_book("书", "作者", "ISBN-Y", 0)

    def test_remove_book(self):
        book = self.lib.add_book("书X", "作者X", "ISBN-X2")
        self.lib.remove_book(book.book_id)
        self.assertEqual(len(self.lib.list_books()), 0)

    def test_remove_nonexistent_book_raises(self):
        with self.assertRaises(ValueError):
            self.lib.remove_book(999)

    def test_remove_book_with_active_borrow_raises(self):
        book = self.lib.add_book("书Z", "作者Z", "ISBN-Z")
        self.lib.borrow_book(book.book_id, "借阅人A")
        with self.assertRaises(ValueError):
            self.lib.remove_book(book.book_id)

    def test_update_book(self):
        book = self.lib.add_book("旧书名", "旧作者", "ISBN-U1")
        updated = self.lib.update_book(book.book_id, title="新书名")
        self.assertEqual(updated.title, "新书名")
        self.assertEqual(updated.author, "旧作者")

    def test_update_book_quantity(self):
        book = self.lib.add_book("书Q", "作者Q", "ISBN-Q", 3)
        self.lib.borrow_book(book.book_id, "读者")
        # 1 borrowed, 2 available → new quantity must be >= 1
        updated = self.lib.update_book(book.book_id, quantity=2)
        self.assertEqual(updated.quantity, 2)
        self.assertEqual(updated.available, 1)

    def test_update_book_quantity_too_small_raises(self):
        book = self.lib.add_book("书R", "作者R", "ISBN-R", 2)
        self.lib.borrow_book(book.book_id, "读者1")
        self.lib.borrow_book(book.book_id, "读者2")
        with self.assertRaises(ValueError):
            self.lib.update_book(book.book_id, quantity=1)

    def test_list_books(self):
        self.lib.add_book("书1", "作者1", "ISBN-L1")
        self.lib.add_book("书2", "作者2", "ISBN-L2")
        self.assertEqual(len(self.lib.list_books()), 2)


class TestLibrarySearch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        os.unlink(self.tmp.name)
        self.lib = Library(data_file=self.tmp.name)
        self.lib.add_book("Python编程从入门到精通", "张三", "ISBN-P1")
        self.lib.add_book("Java核心技术", "李四", "ISBN-J1")
        self.lib.add_book("数据结构与算法", "张三", "ISBN-D1")

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def test_search_by_title(self):
        results = self.lib.search_by_title("python")
        self.assertEqual(len(results), 1)
        self.assertIn("Python", results[0].title)

    def test_search_by_author(self):
        results = self.lib.search_by_author("张三")
        self.assertEqual(len(results), 2)

    def test_search_by_isbn(self):
        book = self.lib.search_by_isbn("ISBN-J1")
        self.assertIsNotNone(book)
        self.assertEqual(book.title, "Java核心技术")

    def test_search_by_isbn_not_found(self):
        result = self.lib.search_by_isbn("NONEXISTENT")
        self.assertIsNone(result)


class TestLibraryBorrowReturn(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        os.unlink(self.tmp.name)
        self.lib = Library(data_file=self.tmp.name)
        self.book = self.lib.add_book("测试图书", "测试作者", "ISBN-TEST", 2)

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def test_borrow_book(self):
        record = self.lib.borrow_book(self.book.book_id, "读者甲")
        self.assertEqual(record.borrower, "读者甲")
        self.assertEqual(self.book.available, 1)

    def test_borrow_reduces_available(self):
        self.lib.borrow_book(self.book.book_id, "读者甲")
        self.lib.borrow_book(self.book.book_id, "读者乙")
        self.assertEqual(self.book.available, 0)

    def test_borrow_when_unavailable_raises(self):
        self.lib.borrow_book(self.book.book_id, "读者甲")
        self.lib.borrow_book(self.book.book_id, "读者乙")
        with self.assertRaises(ValueError):
            self.lib.borrow_book(self.book.book_id, "读者丙")

    def test_borrow_empty_borrower_raises(self):
        with self.assertRaises(ValueError):
            self.lib.borrow_book(self.book.book_id, "  ")

    def test_return_book(self):
        record = self.lib.borrow_book(self.book.book_id, "读者甲")
        self.lib.return_book(record.record_id)
        self.assertEqual(self.book.available, 2)
        self.assertNotEqual(record.return_date, "")

    def test_return_book_twice_raises(self):
        record = self.lib.borrow_book(self.book.book_id, "读者甲")
        self.lib.return_book(record.record_id)
        with self.assertRaises(ValueError):
            self.lib.return_book(record.record_id)

    def test_return_nonexistent_record_raises(self):
        with self.assertRaises(ValueError):
            self.lib.return_book(999)

    def test_list_borrow_records(self):
        r1 = self.lib.borrow_book(self.book.book_id, "读者甲")
        self.lib.borrow_book(self.book.book_id, "读者乙")
        self.lib.return_book(r1.record_id)
        all_records = self.lib.list_borrow_records()
        self.assertEqual(len(all_records), 2)
        unreturned = self.lib.list_borrow_records(unreturned_only=True)
        self.assertEqual(len(unreturned), 1)
        by_borrower = self.lib.list_borrow_records(borrower="读者甲")
        self.assertEqual(len(by_borrower), 1)


class TestLibraryPersistence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        os.unlink(self.tmp.name)

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def test_data_persists_across_instances(self):
        lib1 = Library(data_file=self.tmp.name)
        book = lib1.add_book("持久化图书", "作者", "ISBN-PERSIST")
        lib1.borrow_book(book.book_id, "读者")

        lib2 = Library(data_file=self.tmp.name)
        self.assertEqual(len(lib2.list_books()), 1)
        self.assertEqual(lib2.list_books()[0].title, "持久化图书")
        self.assertEqual(lib2.list_books()[0].available, 0)
        self.assertEqual(len(lib2.list_borrow_records()), 1)


if __name__ == "__main__":
    unittest.main()
