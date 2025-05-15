from prompt_toolkit import PromptSession
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.styles import Style
from pathlib import Path
from file_operations import FileOperations
import json

class PromptFileManager:
    def __init__(self, config_path='config.json', users_path='users.json'):
        self.load_config(config_path)
        self.load_users(users_path)
        self.user = None
        self.file_ops = None
        self.current_dir = None
        self.session = PromptSession(
            completer=PathCompleter(),
            style=Style.from_dict({
                'prompt': 'bold #00ff00',
                '': '#ffffff'
            }),
            prompt_continuation=lambda width, line_number, is_soft: '. ',
        )

    def load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.root_dir = Path(config['root_directory']).resolve()
                self.quota_mb = config.get('quota_mb', 10)  # Лимит в МБ, по умолчанию 10
            if not self.root_dir.exists():
                self.root_dir.mkdir(parents=True)
                print(f"Создана рабочая директория: {self.root_dir}")
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            print(f"Ошибка загрузки конфигурации: {e}. Используется текущая директория.")
            self.root_dir = Path.cwd()
            self.quota_mb = 10

    def load_users(self, users_path):
        self.users_path = users_path
        try:
            with open(users_path, 'r') as f:
                self.users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = {}
            with open(users_path, 'w') as f:
                json.dump(self.users, f)

    def save_users(self):
        with open(self.users_path, 'w') as f:
            json.dump(self.users, f)

    def register(self, username, password):
        if username in self.users:
            print("Пользователь уже существует")
            return False
        user_dir = self.root_dir / "users" / username
        user_dir.mkdir(parents=True, exist_ok=True)
        self.users[username] = {"password": password, "directory": str(user_dir)}
        self.save_users()
        print(f"Пользователь {username} зарегистрирован")
        return True

    def login(self, username, password):
        if username in self.users and self.users[username]["password"] == password:
            self.user = username
            self.current_dir = Path(self.users[username]["directory"]).resolve()
            self.file_ops = FileOperations(self.current_dir, self.quota_mb)
            print(f"Вход выполнен: {username}")
            return True
        print("Неверное имя пользователя или пароль")
        return False

    def is_within_root(self, path):
        try:
            resolved_path = Path(path).resolve()
            resolved_root = self.current_dir.resolve()
            return resolved_root in resolved_path.parents or resolved_path == resolved_root
        except FileNotFoundError:
            print(f"Путь {path} не существует")
            return False

    def run(self):
        print("Файловый менеджер. Введите 'register <username> <password>' или 'login <username> <password>'.")
        while True:
            if not self.user:
                try:
                    command = self.session.prompt("> ").strip().split()
                    if not command:
                        continue
                    cmd = command[0].lower()
                    if cmd == 'register' and len(command) >= 3:
                        self.register(command[1], command[2])
                    elif cmd == 'login' and len(command) >= 3:
                        self.login(command[1], command[2])
                    elif cmd == 'exit':
                        break
                    else:
                        print("Команды: register <username> <password>, login <username> <password>, exit")
                except Exception as e:
                    print(f"Ошибка: {e}")
                continue

            try:
                command = self.session.prompt(f"{self.current_dir}> ").strip().split()
                if not command:
                    continue
                cmd = command[0].lower()
                args = command[1:]

                if cmd == 'exit':
                    break
                elif cmd == 'logout':
                    self.user = None
                    self.file_ops = None
                    self.current_dir = None
                    print("Выход из учетной записи")
                    continue
                elif cmd == 'help':
                    self.show_help()
                elif cmd == 'ls' or cmd == 'dir':
                    self.file_ops.list_dir(self.current_dir)
                elif cmd == 'mkdir':
                    if args: self.file_ops.create_directory(args[0], self.current_dir)
                    else: print("Укажите имя директории")
                elif cmd == 'rmdir':
                    if args: self.file_ops.remove_directory(args[0], self.current_dir)
                    else: print("Укажите имя директории")
                elif cmd == 'cd':
                    if args:
                        new_dir = self.file_ops.change_directory(args[0], self.current_dir)
                        if self.is_within_root(new_dir):
                            self.current_dir = new_dir
                        else:
                            print("Нельзя выйти за пределы вашей директории")
                    else:
                        print("Укажите директорию")
                elif cmd == 'create':
                    if args: self.file_ops.create_file(args[0], self.current_dir)
                    else: print("Укажите имя файла")
                elif cmd == 'read':
                    if args: self.file_ops.read_file(args[0], self.current_dir)
                    else: print("Укажите имя файла")
                elif cmd == 'write':
                    if len(args) >= 2: self.file_ops.write_file(args[0], ' '.join(args[1:]), self.current_dir)
                    else: print("Укажите имя файла и текст")
                elif cmd == 'rm':
                    if args: self.file_ops.remove_file(args[0], self.current_dir)
                    else: print("Укажите имя файла")
                elif cmd == 'cp':
                    if len(args) >= 2: self.file_ops.copy_file(args[0], args[1], self.current_dir)
                    else: print("Укажите исходный и целевой файлы")
                elif cmd == 'mv':
                    if len(args) >= 2: self.file_ops.move_file(args[0], args[1], self.current_dir)
                    else: print("Укажите исходный и целевой файлы")
                elif cmd == 'rename':
                    if len(args) >= 2: self.file_ops.rename_file(args[0], args[1], self.current_dir)
                    else: print("Укажите старое и новое имя файла")
                elif cmd == 'zip':
                    if args: self.file_ops.zip_file(args[0], self.current_dir)
                    else: print("Укажите имя файла")
                elif cmd == 'unzip':
                    if args: self.file_ops.unzip_file(args[0], self.current_dir)
                    else: print("Укажите имя архива")
                elif cmd == 'quota':
                    self.file_ops.check_quota(self.current_dir)
                else:
                    print("Неизвестная команда. Введите 'help' для списка команд.")
            except Exception as e:
                print(f"Ошибка: {e}")

    def show_help(self):
        print("""
Доступные команды:
  ls/dir           - Показать содержимое текущей директории
  mkdir <name>     - Создать директорию
  rmdir <name>     - Удалить директорию
  cd <name>        - Сменить текущую директорию
  create <name>    - Создать файл
  read <name>      - Прочитать файл
  write <name> <text> - Записать текст в файл
  rm <name>        - Удалить файл
  cp <src> <dst>   - Копировать файл
  mv <src> <dst>   - Переместить файл
  rename <old> <new> - Переименовать файл
  zip <file>       - Заархивировать файл
  unzip <archive>  - Разархивировать архив
  quota            - Проверить использование квоты
  logout           - Выйти из учетной записи
  help             - Показать эту справку
  exit             - Выйти
        """)

if __name__ == "__main__":
    fm = PromptFileManager()
    fm.run()