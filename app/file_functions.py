import os
from datetime import datetime
import shutil
import logging
from flask import session

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
logger = logging.getLogger("FinanceLogger")

# File handling functions for config and logs
#    - test param creates a test.log file instead of finance.log
def create_files(test=False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    if test:
        if not os.path.exists(os.path.join(log_dir, 'tests.log')):
            create_file(directory=log_dir, file_name='tests.log', content=f"Test log file created at {timestamp}\n")
    else: 
        if not os.path.exists(os.path.join(log_dir, 'finance.log')):
            create_file(directory=log_dir, file_name='finance.log', content=f"Finance log file created at {timestamp}\n")
    if not os.path.exists(os.path.join(BASE_DIR, 'config.txt')):
        create_file(file_name='config.txt', content='log-level: INFO')


# Delete old logs
def delete_old_backups():
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
def create_file(directory: str | None=BASE_DIR, file_name: str | None=None,
                content: str | None=None):
    if directory is None or file_name is None:
        return False
    # do exist_ok check
    file_path = os.path.join(directory, file_name)
    with open(file_path, 'w') as f:
        if content is not None:
            f.write(content + '\n')
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
                if lines[i].strip() == content.strip():
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
    logger.debug(f"edit_file entered in file_functions.py")
    if directory is None or file_name is None or new_content is None:
        return False
    lines = None
    file_path = os.path.join(directory, file_name)
    try:
        if old_content is not None:
            idx = search_file(directory, file_name, old_content, starts_with)
            if idx == -1:
                logger.warning(f"Content '{old_content}' not found in file '{file_path}'. Cannot edit.")
                logger.debug(f"edit_file exited with failure in file_functions.py")
                return False
            with open(file_path, 'r') as f:
                lines = f.readlines()
            f.close()
            lines[idx] = new_content
            with open(file_path, 'w') as f:
                f.writelines(lines)
            f.close()
            logger.info(f"File {file_path} edited successfully.")
            logger.debug(f"edit_file exited with success in file_functions.py")
            return True
        else:
            with open(file_path, 'a') as f:
                f.write(new_content + '\n')
            f.close()
            logger.info(f"Content appended to file '{file_path}' successfully.")
            logger.debug(f"edit_file exited with success in file_functions.py")
            return True
    except Exception as e:
        logger.error(f"Failed to edit file '{file_path}': {e}")
        logger.debug(f"edit_file exited with failure in file_functions.py")
        return False


# Deletes a file. Inputs are all strings of directory and file name.
def delete_file(directory: str | None=None, file_name: str | None=None):
    logger.debug(f"delete_file entered in file_functions.py")
    if directory is None or file_name is None:
        logger.warning(f"Directory or file name not provided for delete_file function.")
        logger.debug(f"delete_file exited with failure in file_functions.py")
        return
    file_path = os.path.join(directory, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"File '{file_path}' deleted successfully.")
    else:
        logger.warning(f"The file '{file_path}' does not exist.")
    logger.debug(f"delete_file exited in file_functions.py")


# Returns either the entire content or specific line of the file based on line idx.
# Inputs are:
#    - strings of directory and file name 
#    - int of line idx.
def get_file_content(directory: str | None=BASE_DIR, file_name: str | None=None, 
                     line_idx: int | None=None):
    logger.debug(f"get_file_content entered in file_functions.py")
    if file_name is None:
        logger.warning(f"File name not provided for get_file_content function.")
        logger.debug(f"get_file_content exited with failure in file_functions.py")
        return None
    file_path = os.path.join(directory, file_name)
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.readlines()
            f.close()
            if line_idx is not None and 0 <= line_idx < len(content):
                return content[line_idx].strip()
            return '\n'.join(content)
        else:
            logger.warning(f"The file '{file_path}' does not exist.")
            logger.debug(f"get_file_content exited with failure in file_functions.py")
            return None
    except Exception as e:
        logger.error(f"Failed to read file '{file_path}': {e}")
        logger.debug(f"get_file_content exited with failure in file_functions.py")
        return None


# Backs up source to directory and saves file as filetype
def doBackup(source, dir, filetype):
    logger.debug("doBackup entered in file_functions.py")
    os.makedirs(dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = f"{dir}/backup_{timestamp}.{filetype}"
    shutil.copy2(source, dest)
    logger.info(f"{filetype} backed up to {dest}")
    logger.debug("doBackup exited in file_functions.py")


# Saves current db and log files to backups folder.
def backup_db_and_logs():
    logger.debug(f"backup_db_and_logs entered in file_functions.py")
    source1 = os.path.join(BASE_DIR, 'instance', 'finance.db')
    source2 = os.path.join(BASE_DIR, 'logs', 'finance.log')
    db_backup_dir = os.path.join(BACKUP_DIR, 'instance')
    log_backup_dir = os.path.join(BACKUP_DIR, 'logs')
    try:
        doBackup(source1, db_backup_dir, 'db')
        doBackup(source2, log_backup_dir, 'log')
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        logger.debug("backup_db_and_logs exited with failure in file_functions.py")
        return False
    logger.debug(f"backup_db_and_logs exited in file_functions.py")
    return True


#-------------------------------
# Creates a new log file and backs up the old one
def make_new_log_file():
    logger.debug(f"make_new_log_file entered in file_functions.py")
    log_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "finance.log")
    if os.path.exists(log_file):
        doBackup(log_file, os.path.join(BACKUP_DIR, "logs"), "log")
    try:
        with open(log_file, 'w') as f:
            f.write(f"New log file created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    except Exception as e:
        logger.error(f"Failed to create new log file: {e}")
        logger.debug(f"make_new_log_file exited with failure in file_functions.py.")
        return False
    logger.debug(f"make_new_log_file exited with success in file_functions.py.")
    return True