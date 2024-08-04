import os
import threading
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import customtkinter as ctk
from pymem import Pymem
from pymem.process import inject_dll
file_patterns = ['Tirify.Common.dll']
observer = Observer()
path_file = os.path.join(os.path.expanduser('~'), 'Documents', 'rust_path.txt')
def animate_title(root, title_text):
    def update_title():
        current_text = ''
        for char in title_text:
            current_text += char
            root.title(current_text)
            threading.Event().wait(0.1)
    threading.Thread(target=update_title, daemon=True).start()
class FileDeleteHandler(FileSystemEventHandler):
    def __init__(self, file_patterns):
        self.file_patterns = file_patterns
    def on_created(self, event):
        for pattern in self.file_patterns:
            if event.src_path.endswith(pattern):
                try:
                    os.remove(event.src_path)
                    print(f'suc del: {event.src_path}')
                except Exception as e:
                    print(f'error del {event.src_path}: {e}')
def start_monitoring(path, start_button):
    if not path:
        print('Не указан путь к папке Rust')
        return
    monitor_path = os.path.join(path, 'RustClient_Data', 'Plugins', 'x86_64')
    if not os.path.exists(monitor_path):
        print(f'Путь не существует: {monitor_path}')
        return
    initial_file_path = os.path.join(monitor_path, 'Tirify.Common.dll')
    if os.path.exists(initial_file_path):
        try:
            os.remove(initial_file_path)
            print('Файл: inithook')
        except Exception as e:
            print('Ошибка')
    event_handler = FileDeleteHandler(file_patterns)
    observer.schedule(event_handler, monitor_path, recursive=False)
    threading.Thread(target=run_observer, daemon=True).start()
    start_button.configure(text='Bypass Enable\nDont close application', fg_color='green', state='disabled')
def run_observer():
    observer.start()
def save_path(path):
    with open(path_file, 'w') as file:
        file.write(path)
def load_path():
    if os.path.exists(path_file):
        with open(path_file, 'r') as file:
            return file.read().strip()
    else:
        return ''
def open_rust():
    rust_folder = ''
    if os.path.exists(path_file):
        with open(path_file, 'r') as f:
            rust_folder = f.readline().strip()
    else:
        app = ctk.CTk()
        app.attributes('-topmost', True)
        rust_folder = ctk.filedialog.askdirectory(title='Select folder with Rust')
        app.destroy()
        if not rust_folder:
            return ''
        save_path(rust_folder)
    bat_content = f'@echo off\ncd /d "{rust_folder}"\nstart "" "Rust.exe"\ntimeout /t 5 /nobreak >nul\nstart "" "RustClient.exe"\n'
    with open(os.path.join(os.path.expanduser('~/Documents'), 'start_rust.bat'), 'w') as bat_file:
        bat_file.write(bat_content)
    subprocess.Popen([os.path.join(os.path.expanduser('~/Documents'), 'start_rust.bat')], shell=True)
    return rust_folder
def close_rust():
    processes_to_close = ['EasyAntiCheat.exe', 'Rust.exe', 'RustClient.exe']
    for process_name in processes_to_close:
        try:
            subprocess.run(['taskkill', '/F', '/IM', process_name], check=True)
            print(f'Процесс {process_name} завершен')
        except subprocess.CalledProcessError:
            print(f'Не удалось завершить процесс {process_name}')
def open_github():
    subprocess.run(['start', 'https://github.com/spacecollapse'], shell=True)
def open_discord():
    subprocess.run(['start', 'https://discord.gg/tYpSxkRzbD'], shell=True)
def open_help():
    subprocess.run(['start', 'https://github.com/spacecollapse/requirements'], shell=True)
def inject_other():
    app = ctk.CTk()
    app.attributes('-topmost', True)
    dll_path = ctk.filedialog.askopenfilename(title='Select dll for injection', filetypes=[('DLL Files', '*.dll')])
    app.destroy()
    if not dll_path:
        print('Файл DLL не выбран.')
        return
    process_name = 'RustClient.exe'
    try:
        open_process = Pymem(process_name)
        inject_dll(open_process.process_handle, dll_path.encode('UTF-8'))
    except Exception as e:
        print(f'Произошла ошибка: {e}')
def delete_files():
    documents_path = os.path.expanduser('~/Documents')
    files_to_delete = ['rust_path.txt', 'start_rust.bat']
    for filename in files_to_delete:
        file_path = os.path.join(documents_path, filename)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            else:
                print(f'Файл не найден: {file_path}')
        except Exception as e:
            print(f'Ошибка при удалении {e}')
def main():
    root = ctk.CTk()
    root.geometry('375x350')
    root.resizable(False, False)
    title_text = 'Bypass Alkad EAC by usehvh :3'
    animate_title(root, title_text)
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(pady=20, padx=10)
    start_button = ctk.CTkButton(main_frame, text='Enable bypass', command=lambda: start_monitoring(load_path() or open_rust(), start_button))
    start_button.grid(row=0, column=0, columnspan=2, pady=10)
    inject_button = ctk.CTkButton(main_frame, text='Select dll for injection', fg_color='#d500ff', command=inject_other)
    inject_button.grid(row=1, column=0, columnspan=2, pady=10)
    open_rust_button = ctk.CTkButton(main_frame, text='Open Rust', command=open_rust)
    open_rust_button.grid(row=2, column=0, padx=10, pady=5, sticky='ew')
    close_rust_button = ctk.CTkButton(main_frame, text='Close Rust', command=close_rust)
    close_rust_button.grid(row=2, column=1, padx=10, pady=5, sticky='ew')
    link_frame = ctk.CTkFrame(root)
    link_frame.pack(pady=5, padx=10)
    first_row_frame = ctk.CTkFrame(link_frame)
    first_row_frame.pack(pady=10, padx=10)
    github_button = ctk.CTkButton(first_row_frame, text='Reset Settings', fg_color='#572020', command=delete_files)
    github_button.pack(side='left', padx=10)
    discord_button = ctk.CTkButton(first_row_frame, text='Components for cheats', fg_color='#572020', command=open_help)
    discord_button.pack(side='left', padx=10)
    second_row_frame = ctk.CTkFrame(link_frame)
    second_row_frame.pack(pady=10, padx=10)
    button3 = ctk.CTkButton(second_row_frame, text='Github', fg_color='#4B0082', command=open_github)
    button3.pack(side='left', padx=10)
    button4 = ctk.CTkButton(second_row_frame, text='Discord', fg_color='#4B0082', command=open_discord)
    button4.pack(side='left', padx=10)
    label = ctk.CTkLabel(root, text='alkad eac bypass', font=('Arial', 30, 'bold'))
    label.pack(padx=10, pady=10)
    if load_path():
        start_monitoring(load_path(), start_button)
    root.mainloop()
if __name__ == '__main__':
    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme('dark-blue')
    main()
