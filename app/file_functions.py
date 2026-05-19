import os
from datetime import datetime
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# File handling functions for config and logs
def create_files(test=False):
    log_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    if test:
        create_file(directory=log_dir, file_name='tests.log')
    else: 
        create_file(directory=log_dir, file_name='finance.log')
    if not os.path.exists(os.path.join(BASE_DIR, 'config.txt')):
        create_file(file_name='config.txt', content='log-level: INFO')

# Delete old logs
def delete_old_backup_logs():
    log_dir = os.path.join(BASE_DIR, "backups", "logs")
    db_dir = os.path.join(BASE_DIR, "backups", "instance")
    if os.path.exists(log_dir):
        for file in os.listdir(log_dir):
            date = datetime.strptime(file.split('_')[1], "%Y%m%d")
            if (datetime.now() - date).days > 20:
                delete_file(directory=log_dir, file_name=file)
    if os.path.exists(db_dir):
        for file in os.listdir(db_dir):
            date = datetime.strptime(file.split('_')[1], "%Y%m%d")
            if (datetime.now() - date).days > 10:
                delete_file(directory=db_dir, file_name=file)

# Creates a file. Inputs are all strings: directory, file name, and content.
def create_file(directory: str | None=BASE_DIR, file_name: str | None=None, content: str | None=None):
    if directory is None or file_name is None:
        return False
    file_path = os.path.join(directory, file_name)
    with open(file_path, 'w') as f:
        if content is not None:
            f.write(content)
        f.close()
    return True

# Returns the idx of the content in the file or -1 if it doesnt exist
# Inputs are:
#    - strings directory, file name, and content. 
#    - starts_with, a bool for lookup based on the start of the line
def search_file(directory: str | None=BASE_DIR, file_name: str | None=None, 
                content: str | None=None, starts_with: bool | None=False):
    if directory is None or file_name is None or content is None:
        return -1
    file_path = os.path.join(directory, file_name)
    if os.path.exists(file_path):
        answer = -1
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if starts_with and lines[i].startswith(content):
                    answer = i
                    break
                if lines[i] == content:
                    answer = i
                    break
        f.close()
        return answer
    return -1

# Can append, or edit a specific idx of lines. uses search file to get specific lines
# Inputs are:
#    - strings directory, file name, and old and new content. 
#    - starts_with, a bool for lookup based on the start of the line.
def edit_file(directory: str | None=BASE_DIR, file_name: str | None=None, 
              old_content: str | None=None, new_content: str | None=None, 
              starts_with: bool | None=False):
    if directory is None or file_name is None or new_content is None:
        return False
    lines = None
    file_path = os.path.join(directory, file_name)
    if old_content is not None and new_content is not None:
        idx = search_file(directory, file_name, old_content, starts_with)
        if idx == -1:
            # content not found
            return False
        with open(file_path, 'r') as f:
            lines = f.readlines()
        f.close()
        lines[idx] = new_content
        with open(file_path, 'w') as f:
            f.writelines(lines)
        f.close()
        return True
    elif new_content is not None:
        with open(file_path, 'a') as f:
            f.write(new_content)
        f.close()
        return True
    return False

# Deletes a file. Inputs are all strings of directory and file name.
def delete_file(directory: str | None=None, file_name: str | None=None):
    if directory is None or file_name is None:
        return
    file_path = os.path.join(directory, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        print("File deleted successfully.")
    else:
        print("The file does not exist.")

# Returns either the entire content or specific line of the file based on line idx.
# Inputs are:
#    - strings of directory and file name 
#    - int of line idx.
def get_file_content(directory: str | None=None, file_name: str | None=None, 
                     line_idx: int | None=None):
    if file_name is None:
        return None
    if directory is None:
        directory = BASE_DIR
    file_path = os.path.join(directory, file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.readlines()
        f.close()
        if line_idx is not None and 0 <= line_idx < len(content):
            return content[line_idx].strip()
        return '\n'.join(content)
    else:
        print("The file does not exist.")
        return None
