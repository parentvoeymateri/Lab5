import os
from pathlib import Path
import shutil
import zipfile

class FileOperations:
    def __init__(self, root_dir, quota_mb=10):
        self.root_dir = Path(root_dir).resolve()
        self.quota_bytes = quota_mb * 1024 * 1024  # МБ в байты

    def get_directory_size(self, directory):
        total_size = 0
        for dirpath, _, filenames in os.walk(directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp) if os.path.exists(fp) else 0
        return total_size

    def check_quota(self, directory):
        size = self.get_directory_size(directory)
        print(f"Использовано: {size / (1024 * 1024):.2f} МБ из {self.quota_bytes / (1024 * 1024):.2f} МБ")
        return size < self.quota_bytes

    def list_dir(self, current_dir):
        try:
            for item in Path(current_dir).iterdir():
                print(item.name)
        except Exception as e:
            print(f"Ошибка при чтении директории: {e}")

    def create_directory(self, dir_name, current_dir):
        try:
            new_dir = Path(current_dir) / dir_name
            if self.root_dir in new_dir.resolve().parents or new_dir.resolve() == self.root_dir:
                new_dir.mkdir(exist_ok=True)
                print(f"Директория {dir_name} создана")
            else:
                print("Нельзя создать директорию за пределами рабочей директории")
        except Exception as e:
            print(f"Ошибка при создании директории: {e}")

    def remove_directory(self, dir_name, current_dir):
        try:
            dir_path = Path(current_dir) / dir_name
            if dir_path.exists() and dir_path.is_dir():
                shutil.rmtree(dir_path)
                print(f"Директория {dir_name} удалена")
            else:
                print("Директория не существует")
        except Exception as e:
            print(f"Ошибка при удалении директории: {e}")

    def change_directory(self, dir_name, current_dir):
        try:
            current_path = Path(current_dir).resolve()
            if dir_name == "..":
                new_dir = current_path.parent
            else:
                new_dir = current_path / dir_name
            if new_dir.exists() and new_dir.is_dir():
                resolved_new_dir = new_dir.resolve()
                print(f"Разрешенный путь: {resolved_new_dir}")
                return resolved_new_dir
            else:
                print(f"Директория {dir_name} не существует")
                return current_path
        except Exception as e:
            print(f"Ошибка при смене директории: {e}")
            return current_path

    def create_file(self, file_name, current_dir):
        try:
            file_path = Path(current_dir) / file_name
            if self.root_dir in file_path.resolve().parents or file_path.resolve() == self.root_dir:
                if self.check_quota(current_dir):
                    file_path.touch()
                    print(f"Файл {file_name} создан")
                else:
                    print("Превышена квота дискового пространства")
            else:
                print("Нельзя создать файл за пределами рабочей директории")
        except Exception as e:
            print(f"Ошибка при создании файла: {e}")

    def read_file(self, file_name, current_dir):
        try:
            file_path = Path(current_dir) / file_name
            if file_path.exists() and file_path.is_file():
                with open(file_path, 'r', encoding='utf-8') as f:
                    print(f.read())
            else:
                print("Файл не существует")
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")

    def write_file(self, file_name, text, current_dir):
        try:
            file_path = Path(current_dir) / file_name
            if self.root_dir in file_path.resolve().parents or file_path.resolve() == self.root_dir:
                if self.check_quota(current_dir):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                    print(f"Текст записан в файл {file_name}")
                else:
                    print("Превышена квота дискового пространства")
            else:
                print("Нельзя записать файл за пределами рабочей директории")
        except Exception as e:
            print(f"Ошибка при записи файла: {e}")

    def remove_file(self, file_name, current_dir):
        try:
            file_path = Path(current_dir) / file_name
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                print(f"Файл {file_name} удален")
            else:
                print("Файл не существует")
        except Exception as e:
            print(f"Ошибка при удалении файла: {e}")

    def copy_file(self, src_name, dst_name, current_dir):
        try:
            src_path = Path(current_dir) / src_name
            dst_path = Path(current_dir) / dst_name
            if src_path.exists() and src_path.is_file():
                if self.root_dir in dst_path.resolve().parents or dst_path.resolve() == self.root_dir:
                    if self.check_quota(current_dir):
                        shutil.copy2(src_path, dst_path)
                        print(f"Файл {src_name} скопирован в {dst_name}")
                    else:
                        print("Превышена квота дискового пространства")
                else:
                    print("Нельзя скопировать файл за пределы рабочей директории")
            else:
                print("Исходный файл не существует")
        except Exception as e:
            print(f"Ошибка при копировании файла: {e}")

    def move_file(self, src_name, dst_name, current_dir):
        try:
            src_path = Path(current_dir) / src_name
            dst_path = Path(current_dir) / dst_name
            if src_path.exists() and src_path.is_file():
                if self.root_dir in dst_path.resolve().parents or dst_path.resolve() == self.root_dir:
                    if self.check_quota(current_dir):
                        shutil.move(src_path, dst_path)
                        print(f"Файл {src_name} перемещен в {dst_name}")
                    else:
                        print("Превышена квота дискового пространства")
                else:
                    print("Нельзя переместить файл за пределы рабочей директории")
            else:
                print("Исходный файл не существует")
        except Exception as e:
            print(f"Ошибка при перемещении файла: {e}")

    def rename_file(self, old_name, new_name, current_dir):
        try:
            old_path = Path(current_dir) / old_name
            new_path = Path(current_dir) / new_name
            if old_path.exists() and old_path.is_file():
                if self.root_dir in new_path.resolve().parents or new_path.resolve() == self.root_dir:
                    old_path.rename(new_path)
                    print(f"Файл {old_name} переименован в {new_name}")
                else:
                    print("Нельзя переименовать файл за пределы рабочей директории")
            else:
                print("Исходный файл не существует")
        except Exception as e:
            print(f"Ошибка при переименовании файла: {e}")

    def zip_file(self, file_name, current_dir):
        try:
            file_path = Path(current_dir) / file_name
            if file_path.exists() and file_path.is_file():
                zip_path = file_path.with_suffix('.zip')
                if self.root_dir in zip_path.resolve().parents or zip_path.resolve() == self.root_dir:
                    if self.check_quota(current_dir):
                        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                            zf.write(file_path, file_name)
                        print(f"Файл {file_name} заархивирован в {zip_path.name}")
                    else:
                        print("Превышена квота дискового пространства")
                else:
                    print("Нельзя создать архив за пределами рабочей директории")
            else:
                print("Файл не существует")
        except Exception as e:
            print(f"Ошибка при архивации: {e}")

    def unzip_file(self, zip_name, current_dir):
        try:
            zip_path = Path(current_dir) / zip_name
            if zip_path.exists() and zip_path.suffix == '.zip':
                if self.check_quota(current_dir):
                    with zipfile.ZipFile(zip_path, 'r') as zf:
                        zf.extractall(current_dir)
                    print(f"Архив {zip_name} разархивирован")
                else:
                    print("Превышена квота дискового пространства")
            else:
                print("Архив не существует или не является ZIP-файлом")
        except Exception as e:
            print(f"Ошибка при разархивации: {e}")