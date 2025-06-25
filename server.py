import os
import sqlite3
from typing import List, Dict, Any
from pypdf import PdfReader
from fastmcp import FastMCP
from models import Reference
import config
import shutil
import time

# 1. Initialize FastMCP server
mcp = FastMCP("EndNote Library Reader")

# 2. Helper functions (database connection, PDF parsing, etc.)
def get_db_connection():
    """Get and return a configured database connection."""
    if config.ENABLE_LOG:
        print(f"[DB] Attempting to connect to database: {config.ENL_FILE_PATH}")
    try:
        conn = sqlite3.connect(f'file:{config.ENL_FILE_PATH}?mode=ro', uri=True)
        conn.row_factory = sqlite3.Row
        if config.ENABLE_LOG:
            print(f"[DB] Database connection successful: {config.ENL_FILE_PATH}")
        return conn
    except sqlite3.Error as e:
        if config.ENABLE_LOG:
            print(f"[DB] Database connection error: {e}")
        return None

def _build_reference_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert a database row to a dictionary for serialization."""
    ref = Reference(
        id=row['id'],
        title=row['title'],
        author=row['author'],
        year=row['year'],
        journal=row['secondary_title'],
        abstract=row['abstract'],
        filepath=row['filepath']
    )
    d = ref.model_dump()
    # keywords field compatibility
    d['keywords'] = row['keywords'] if 'keywords' in row.keys() else None
    return d

# 3. Define MCP tools
@mcp.tool(description="Return references in the EndNote library with pagination. Use offset (int, default 0) and limit (int, default 10) to fetch a page of results. Returns a list of dicts with fields: id, title, author, year, journal, abstract, keywords, filepath. Typical: list_papers(offset=0, limit=10).")
def list_papers(offset: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
    """
    List references in the EndNote library with pagination.
    Args:
        offset (int): The starting index of the page (default 0, must be >=0).
        limit (int): The number of results per page (default 10, must be >0).
    Returns:
        List[Dict[str, Any]]: List of references, each with fields: id, title, author, year, journal, abstract, keywords, filepath.
    Typical usage:
        list_papers(offset=0, limit=10)
    """
    if config.ENABLE_LOG:
        print(f"[TOOL] list_papers(offset={offset}, limit={limit}) called")
    if not isinstance(offset, int) or offset < 0:
        offset = 0
    if not isinstance(limit, int) or limit <= 0:
        limit = 10
    conn = get_db_connection()
    if not conn:
        return []
    references = []
    try:
        cursor = conn.cursor()
        query = """
        SELECT r.id, r.title, r.author, r.year, r.secondary_title, r.abstract, r.keywords, f.file_path AS filepath
        FROM refs r LEFT JOIN file_res f ON r.id = f.refs_id ORDER BY r.id DESC LIMIT ? OFFSET ?;
        """
        if config.ENABLE_LOG:
            print(f"[DB] Executing SQL: {query.strip()} | Params: limit={limit}, offset={offset}")
        cursor.execute(query, (limit, offset))
        rows = cursor.fetchall()
        for row in rows:
            references.append(_build_reference_from_row(row))
    except Exception as e:
        if config.ENABLE_LOG:
            print(f"[DB] list_papers exception: {e}")
    finally:
        conn.close()
    return references

@mcp.tool(description="Fuzzy search references by title in the EndNote library. Use when the user only knows part of the title or keywords, or wants to find related topics. Parameter: query (string, case-insensitive, supports Chinese/English). Returns a list of dicts with fields: id, title, author, year, journal, abstract, keywords, filepath. Typical: search_papers('distillation').")
def search_papers(query: str) -> List[Dict[str, Any]]:
    """
    Fuzzy search references by title in the EndNote library.
    Args:
        query (str): Title keyword(s) to search for (case-insensitive, supports Chinese/English, fuzzy match).
    Returns:
        List[Dict[str, Any]]: List of references, each with fields: id, title, author, year, journal, abstract, keywords, filepath.
    Typical usage:
        search_papers('distillation')
    """
    if config.ENABLE_LOG:
        print(f"[TOOL] search_papers(query={query}) called")
    conn = get_db_connection()
    if not conn:
        return []
    references = []
    try:
        cursor = conn.cursor()
        sql_query = """
        SELECT r.id, r.title, r.author, r.year, r.secondary_title, r.abstract, r.keywords, f.file_path AS filepath
        FROM refs r LEFT JOIN file_res f ON r.id = f.refs_id WHERE r.title LIKE ? ORDER BY r.year DESC;
        """
        if config.ENABLE_LOG:
            print(f"[DB] Executing SQL: {sql_query.strip()} | Params: query=%{query}%")
        cursor.execute(sql_query, (f'%{query}%',))
        rows = cursor.fetchall()
        for row in rows:
            references.append(_build_reference_from_row(row))
    except Exception as e:
        if config.ENABLE_LOG:
            print(f"[DB] search_papers exception: {e}")
    finally:
        conn.close()
    return references

@mcp.tool(description="Find a paper by (fuzzy) title and return its metadata and PDF full text. Use when the user needs the full content and bibliographic info of a paper. Parameter: title (string, case-insensitive, fuzzy match). Returns a dict with fields: id, title, author, year, journal, abstract, keywords, filepath, text. Typical: read_paper('Knowledge Distillation Review').")
def read_paper(title: str) -> dict:
    """
    Find a paper by (fuzzy) title and return its metadata and PDF full text.
    Args:
        title (str): Title keyword(s) to search for (case-insensitive, fuzzy match).
    Returns:
        dict: Paper metadata and content, with fields: id, title, author, year, journal, abstract, keywords, filepath, text (PDF full text or error message).
    Typical usage:
        read_paper('Knowledge Distillation Review')
    """
    if config.ENABLE_LOG:
        print(f"[TOOL] read_paper(title={title}) called")
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed."}
    try:
        cursor = conn.cursor()
        sql_query = """
        SELECT r.id, r.title, r.author, r.year, r.secondary_title, r.abstract, r.keywords, f.file_path AS filepath
        FROM refs r LEFT JOIN file_res f ON r.id = f.refs_id WHERE r.title LIKE ? LIMIT 1;
        """
        if config.ENABLE_LOG:
            print(f"[DB] Executing SQL: {sql_query.strip()} | Params: title=%{title}%")
        cursor.execute(sql_query, (f'%{title}%',))
        row = cursor.fetchone()
        if not row or not row['filepath']:
            if config.ENABLE_LOG:
                print(f"[DB] No matching paper found or no PDF: title={title}")
            return {"error": f"No paper found with title containing '{title}' or no PDF attached."}
        sanitized_path = row['filepath'].replace('internal-pdf://', '').strip()
        full_path = os.path.join(config.DATA_FOLDER_PATH, 'PDF', sanitized_path)
        if config.ENABLE_LOG:
            print(f"[TOOL] PDF path resolved: {full_path}")
        try:
            reader = PdfReader(full_path)
            text = "".join(page.extract_text() or "" for page in reader.pages)
        except FileNotFoundError:
            text = f"Error: File not found at {full_path}."
            if config.ENABLE_LOG:
                print(f"[TOOL] PDF file not found: {full_path}")
        except Exception as e:
            text = f"Error parsing PDF: {e}"
            if config.ENABLE_LOG:
                print(f"[TOOL] PDF parsing exception: {e}")
        return {
            "id": row['id'],
            "title": row['title'],
            "author": row['author'],
            "year": row['year'],
            "journal": row['secondary_title'],
            "abstract": row['abstract'],
            "keywords": row['keywords'] if 'keywords' in row.keys() else None,
            "filepath": row['filepath'],
            "text": text
        }
    except Exception as e:
        if config.ENABLE_LOG:
            print(f"[DB] read_paper exception: {e}")
        return {"error": f"Exception: {e}"}
    finally:
        conn.close()

@mcp.tool(
    name="refresh_backup",
    description="Manually refresh the .enl.backup file (only available when backup mode is enabled). No effect if backup mode is off. You must close EndNote before refreshing, otherwise the operation will fail due to file locking."
)
def refresh_backup() -> dict:
    """
    Manually refresh the .enl.backup file (only available when backup mode is enabled).
    Returns:
        dict: {status, message, timestamp, filesize}
    """
    if not getattr(config, 'USE_BACKUP', False):
        return {
            "status": "skipped",
            "message": "Backup mode is not enabled. Cannot refresh .enl.backup. Please use the --use-backup option.",
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "filesize": None
        }
    src = config.ENL_FILE_PATH[:-7]  # remove .backup
    dst = config.ENL_FILE_PATH
    try:
        shutil.copy2(src, dst)
        size = os.path.getsize(dst)
        msg = f".enl.backup refreshed successfully, size {size} bytes."
        if config.ENABLE_LOG:
            print(f"[TOOL] refresh_backup: {msg}")
        return {
            "status": "success",
            "message": msg,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "filesize": size
        }
    except Exception as e:
        err = f"Failed to refresh .enl.backup: {e}"
        if config.ENABLE_LOG:
            print(f"[TOOL] refresh_backup: {err}")
        return {
            "status": "error",
            "message": err,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "filesize": None
        }

# 4. Start the server
if __name__ == "__main__":
    config.parse_args()
    # Print registered tools with full parameter signatures
    registered_tools = [
        "list_papers(offset: int = 0, limit: int = 10)",
        "search_papers(query: str)",
        "read_paper(title: str)",
        "refresh_backup()"
    ]
    if config.ENABLE_LOG:
        print("[LOG] EndNote MCP Server is starting...")
        print(f"[LOG] ENL_FILE_PATH: {config.ENL_FILE_PATH}")
        print(f"[LOG] DATA_FOLDER_PATH: {config.DATA_FOLDER_PATH}")
        print(f"[LOG] ENABLE_LOG: {config.ENABLE_LOG}")
        print("[LOG] Registered tools:")
        for tool in registered_tools:
            print(f"- {tool}")
        print("[LOG] Server is ready and waiting for client connections...")
    else:
        print("EndNote MCP Server is starting...")
        print("Registered tools:")
        for tool in registered_tools:
            print(f"- {tool}")
        print("\nServer is ready and waiting for client connections...")
    mcp.run()
