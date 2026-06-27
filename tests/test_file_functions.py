import app.file_functions as func
import os

TEST_DIR = os.path.dirname(__file__)
NAME = "testfile.txt"
TEST_FILE_PATH = os.path.join(TEST_DIR, NAME)

def makeFile():
    with open(TEST_FILE_PATH, 'w') as f:
        f.write("Content\n")
        f.close()

def fileExists():
    return os.path.exists(TEST_FILE_PATH)

def addLine():
    func.edit_file(directory=TEST_DIR, file_name=NAME, new_content="New content")

def deleteFile():
    if fileExists():
        os.remove(TEST_FILE_PATH)

def correctContent(content, idx: None=None):
    lines = None
    with open(TEST_FILE_PATH, 'r') as f:
        lines = f.readlines()
        f.close()
    if idx is not None:
        return lines[idx].strip() == content
    return content == ''.join(lines).strip()
        

def test_create_file():
    assert func.create_file(directory=TEST_DIR, file_name="testfile.txt", content="Content")
    assert fileExists()
    assert correctContent("Content", 0)
    deleteFile()
    assert func.create_file(directory=TEST_DIR, file_name="testfile.txt")
    assert fileExists()
    deleteFile()
    assert not func.create_file(directory=TEST_DIR, file_name=None, content="Content")
    assert not fileExists()
    assert not func.create_file()
    assert not fileExists()


def test_delete_file():
    makeFile()
    func.delete_file(TEST_DIR, NAME)
    assert not fileExists()
    makeFile()
    func.delete_file(TEST_FILE_PATH)
    assert fileExists()
    func.delete_file()
    assert fileExists()
    deleteFile()


def test_edit_file():
    makeFile()
    assert not func.edit_file(TEST_DIR, NAME)
    assert not func.edit_file()
    assert func.edit_file(directory=TEST_DIR, file_name=NAME, new_content="New content")
    assert correctContent("Content", 0)
    assert correctContent("New content", 1)
    assert func.edit_file(directory=TEST_DIR, file_name=NAME, old_content="New content", new_content="Newer content")
    assert correctContent("Content", 0)
    assert correctContent("Newer content", 1)
    assert func.edit_file(directory=TEST_DIR, file_name=NAME, old_content="Newer ", new_content="Starts with content", starts_with=True)
    assert correctContent("Content", 0)
    assert correctContent("Starts with content", 1)
    assert not func.edit_file(directory=TEST_DIR, file_name=NAME, old_content="Starts ", new_content="Unexistant old content")
    deleteFile()


def test_get_file_content():
    content = ""
    makeFile()
    content = func.get_file_content(TEST_DIR, NAME, 0)
    assert correctContent(content, 0)
    addLine()
    content = func.get_file_content(TEST_DIR, NAME, 1)
    assert correctContent(content, 1)
    content = func.get_file_content(TEST_DIR, NAME)
    assert correctContent("Content\nNew content")
    deleteFile()


def test_search_file():
    makeFile()
    assert -1 == func.search_file(TEST_DIR, NAME)
    assert -1 == func.search_file(TEST_DIR, NAME, "")
    assert -1 == func.search_file(TEST_DIR, NAME, "Con")
    assert 0 == func.search_file(TEST_DIR, NAME, "", True)
    assert 0 == func.search_file(TEST_DIR, NAME, "Con", True)
    assert 0 == func.search_file(TEST_DIR, NAME, "Content")
    addLine()
    assert 1 == func.search_file(TEST_DIR, NAME, "New", True)
    assert 1 == func.search_file(TEST_DIR, NAME, "New content")
    assert -1 == func.search_file(TEST_DIR, NAME, "New")
    deleteFile()