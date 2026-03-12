"""
图书管理系统 - 命令行交互界面
"""
from library import Library


def print_separator(char: str = "-", width: int = 60) -> None:
    print(char * width)


def print_menu() -> None:
    print_separator("=")
    print("          📚  图书管理系统  📚")
    print_separator("=")
    print("  1. 添加图书")
    print("  2. 删除图书")
    print("  3. 修改图书信息")
    print("  4. 查看所有图书")
    print("  5. 搜索图书")
    print("  6. 借出图书")
    print("  7. 归还图书")
    print("  8. 查看借阅记录")
    print("  0. 退出系统")
    print_separator("=")


def input_int(prompt: str) -> int | None:
    try:
        return int(input(prompt).strip())
    except ValueError:
        print("  ⚠  请输入有效的数字！")
        return None


def show_books(books) -> None:
    if not books:
        print("  暂无图书信息。")
        return
    print_separator()
    for book in books:
        print(f"  {book}")
    print_separator()


def add_book(lib: Library) -> None:
    print("\n── 添加图书 ──")
    title = input("  书名: ").strip()
    author = input("  作者: ").strip()
    isbn = input("  ISBN: ").strip()
    qty = input_int("  馆藏数量 [默认1]: ")
    if qty is None:
        return
    if qty <= 0:
        print("  ⚠  馆藏数量必须大于0，已取消。")
        return
    try:
        book = lib.add_book(title, author, isbn, qty)
        print(f"  ✅ 添加成功: {book}")
    except ValueError as e:
        print(f"  ❌ {e}")


def remove_book(lib: Library) -> None:
    print("\n── 删除图书 ──")
    book_id = input_int("  请输入图书ID: ")
    if book_id is None:
        return
    try:
        book = lib.remove_book(book_id)
        print(f"  ✅ 已删除: {book}")
    except ValueError as e:
        print(f"  ❌ {e}")


def update_book(lib: Library) -> None:
    print("\n── 修改图书信息 ──")
    book_id = input_int("  请输入要修改的图书ID: ")
    if book_id is None:
        return
    print("  （留空表示不修改该字段）")
    title = input("  新书名: ").strip() or None
    author = input("  新作者: ").strip() or None
    isbn = input("  新ISBN: ").strip() or None
    qty_str = input("  新馆藏数量: ").strip()
    quantity = None
    if qty_str:
        try:
            quantity = int(qty_str)
        except ValueError:
            print("  ⚠  数量格式错误，已跳过。")
    try:
        book = lib.update_book(book_id, title=title, author=author, isbn=isbn, quantity=quantity)
        print(f"  ✅ 修改成功: {book}")
    except ValueError as e:
        print(f"  ❌ {e}")


def list_books(lib: Library) -> None:
    print("\n── 所有图书 ──")
    show_books(lib.list_books())


def search_books(lib: Library) -> None:
    print("\n── 搜索图书 ──")
    print("  1. 按书名搜索")
    print("  2. 按作者搜索")
    print("  3. 按ISBN搜索")
    choice = input("  请选择搜索方式: ").strip()
    if choice == "1":
        keyword = input("  书名关键词: ").strip()
        show_books(lib.search_by_title(keyword))
    elif choice == "2":
        keyword = input("  作者关键词: ").strip()
        show_books(lib.search_by_author(keyword))
    elif choice == "3":
        isbn = input("  ISBN: ").strip()
        book = lib.search_by_isbn(isbn)
        show_books([book] if book else [])
    else:
        print("  ⚠  无效选项。")


def borrow_book(lib: Library) -> None:
    print("\n── 借出图书 ──")
    book_id = input_int("  请输入图书ID: ")
    if book_id is None:
        return
    borrower = input("  借阅人姓名: ").strip()
    try:
        record = lib.borrow_book(book_id, borrower)
        print(f"  ✅ 借阅成功: {record}")
    except ValueError as e:
        print(f"  ❌ {e}")


def return_book(lib: Library) -> None:
    print("\n── 归还图书 ──")
    record_id = input_int("  请输入借阅记录ID: ")
    if record_id is None:
        return
    try:
        record = lib.return_book(record_id)
        print(f"  ✅ 归还成功: {record}")
    except ValueError as e:
        print(f"  ❌ {e}")


def list_records(lib: Library) -> None:
    print("\n── 借阅记录 ──")
    print("  1. 查看全部记录")
    print("  2. 按借阅人查询")
    print("  3. 只看未归还记录")
    choice = input("  请选择: ").strip()
    records = []
    if choice == "1":
        records = lib.list_borrow_records()
    elif choice == "2":
        borrower = input("  借阅人姓名: ").strip()
        records = lib.list_borrow_records(borrower=borrower)
    elif choice == "3":
        records = lib.list_borrow_records(unreturned_only=True)
    else:
        print("  ⚠  无效选项。")
        return
    if not records:
        print("  暂无符合条件的借阅记录。")
        return
    print_separator()
    for r in records:
        print(f"  {r}")
    print_separator()


HANDLERS = {
    "1": add_book,
    "2": remove_book,
    "3": update_book,
    "4": list_books,
    "5": search_books,
    "6": borrow_book,
    "7": return_book,
    "8": list_records,
}


def main() -> None:
    lib = Library()
    print("\n欢迎使用图书管理系统！")
    while True:
        print()
        print_menu()
        choice = input("请输入操作编号: ").strip()
        if choice == "0":
            print("再见！👋")
            break
        handler = HANDLERS.get(choice)
        if handler:
            handler(lib)
        else:
            print("  ⚠  无效选项，请重新输入。")


if __name__ == "__main__":
    main()
