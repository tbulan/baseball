import os
from datetime import datetime

# ==========================================
# 基礎設定區 (Configuration)
# ==========================================
# 要掃描的根目錄，預設為腳本所在目錄
ROOT_DIR = '.'

# 略過不掃描的目錄 (例如：.git, node_modules, 虛擬環境等)
IGNORED_DIRS = {
    '.git', '.svn', '.vscode', '.idea', '__pycache__',
    'node_modules', 'venv', 'env', 'dist', 'build', '.pytest_cache'
}

# 略過不讀取內容的檔案副檔名 (通常是二進位檔或非純文字檔)
IGNORED_EXTENSIONS = {
    '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib', '.exe', '.bin',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg', '.webp',
    '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z',
    '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac',
    '.woff', '.woff2', '.ttf', '.eot'
}

# 特定不讀取的檔案名稱
IGNORED_FILES = {
    'project_bundle.txt', '.DS_Store', 'package-lock.json', 'yarn.lock', '00.py'
}


def should_ignore_dir(dir_name):
    """判斷目錄是否應該被略過"""
    return dir_name in IGNORED_DIRS or dir_name.startswith('.')


def should_ignore_file(file_name):
    """判斷檔案是否應該被『完全』略過 (不列入打包且不佔位，例如：設定檔)"""
    return file_name in IGNORED_FILES

def is_binary_or_ignored_ext(file_name):
    """判斷檔案是否為二進位檔或非純文字檔 (需要被打包產生 XML 佔位符，但略過內容讀取)"""
    ext = os.path.splitext(file_name)[1].lower()
    return ext in IGNORED_EXTENSIONS


def generate_tree(dir_path, prefix=''):
    """生成目錄樹狀結構的字串"""
    tree_str = ""

    try:
        # 取得目錄下的所有項目並排序
        items = os.listdir(dir_path)
        items.sort()

        # 過濾掉需要忽略的項目
        valid_items = []
        for item in items:
            full_path = os.path.join(dir_path, item)
            if os.path.isdir(full_path):
                if not should_ignore_dir(item):
                    valid_items.append((item, True))  # (名稱, 是否為目錄)
            else:
                if item not in IGNORED_FILES:  # 樹狀圖中依然可以顯示不讀取內容的檔案(例如圖片檔名)，但特定設定檔可過濾
                    valid_items.append((item, False))

        # 建立樹狀圖字串
        for i, (item_name, is_dir) in enumerate(valid_items):
            is_last = (i == len(valid_items) - 1)
            connector = '└── ' if is_last else '├── '

            tree_str += f"{prefix}{connector}{item_name}\n"

            if is_dir:
                extension = '    ' if is_last else '│   '
                tree_str += generate_tree(os.path.join(dir_path, item_name), prefix + extension)

    except PermissionError:
        tree_str += f"{prefix}└── [Permission Denied]\n"

    return tree_str


def build_bundle(output_filename="project_bundle.txt"):
    """讀取檔案並產生打包的 txt 檔"""
    print(f"開始掃描目錄: {os.path.abspath(ROOT_DIR)}")

    with open(output_filename, 'w', encoding='utf-8') as outfile:
        # 1. 寫入 AI 讀取指令 (Meta-Prompt)
        outfile.write(
            "[System Directive] 請注意：在解析或盤點圖片素材與檔案時，請務必將程式碼內的資源引用需求與下方的「專案樹狀結構圖 (directory_tree)」進行交叉比對。只要樹狀圖中或下方 <files> 區塊中有對應的檔案實體 (包含 type=\"binary\" 的標記)，請直接視為「已具備」，切勿僅憑程式碼內的預留位置或相對路徑就判定缺失。\n\n")

        # 寫入時間戳記
        outfile.write(f"Project Bundle Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # 專案根標籤
        outfile.write("<project>\n")

        # 3. 寫入樹狀結構，改用 XML 標籤
        outfile.write("<directory_tree>\n")
        outfile.write(f"{os.path.basename(os.path.abspath(ROOT_DIR))}/\n")
        outfile.write(generate_tree(ROOT_DIR))
        outfile.write("</directory_tree>\n\n")

        # 寫入檔案內容區塊標籤
        outfile.write("<files>\n")

        for root, dirs, files in os.walk(ROOT_DIR):
            # 原地修改 dirs 以略過不需要掃描的目錄
            dirs[:] = [d for d in dirs if not should_ignore_dir(d)]

            for file in files:
                # 1. 如果是完全不需要的檔案 (如 .DS_Store)，直接略過
                if should_ignore_file(file):
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, ROOT_DIR)
                # 將 Windows 路徑的 backslash 轉為 forward slash，確保跨平台路徑一致性
                rel_path = rel_path.replace('\\', '/')

                # 2. 如果是二進位檔或不讀取內容的檔案 (如圖片、字體) -> 輸出佔位符
                if is_binary_or_ignored_ext(file):
                    outfile.write(f'<file path="{rel_path}" type="binary">[Asset Exists - Content Skipped]</file>\n')
                    print(f"已標記 (佔位): {rel_path}")
                    continue

                # 3. 如果是純文字檔 -> 讀取內容並包裝在 XML 標籤內
                outfile.write(f'<file path="{rel_path}">\n')

                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        outfile.write(content)
                        # 確保檔案內容結尾有換行，避免破壞結束標籤
                        if not content.endswith('\n'):
                            outfile.write('\n')
                except UnicodeDecodeError:
                    outfile.write("[Error: Unable to read file content (might be binary or wrong encoding)]\n")
                except Exception as e:
                    outfile.write(f"[Error: {str(e)}]\n")

                outfile.write("</file>\n")
                print(f"已打包: {rel_path}")

        # 寫入結尾標籤
        outfile.write("</files>\n")
        outfile.write("</project>\n")

    print(f"\n打包完成！檔案已儲存為: {output_filename}")

if __name__ == "__main__":
    build_bundle()