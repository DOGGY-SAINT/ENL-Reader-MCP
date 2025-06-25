# EndNote MCP Service

This project provides an automated service for reading EndNote `.enl` libraries and exposing their contents via the MCP (Modular Command Protocol) interface. It enables structured, programmatic access to bibliographic data and PDF full texts for downstream LLMs or automation clients.

## Features
- **Automatic EndNote Library Parsing**: Reads `.enl` (SQLite) files and associated `.Data` folders.
- **MCP Tool Interface**: Exposes all functions as MCP tools for easy integration with LLMs or workflow engines.
- **List All References**: Enumerate all bibliographic entries with metadata.
- **Fuzzy Search**: Search references by (partial) title or keywords, supporting both English and Chinese.
- **PDF Full Text Extraction**: Retrieve and extract the full text of attached PDF files by paper title.
- **Backup Mode & Manual Refresh**: Optionally operate on a `.enl.backup` file for safer access, with both automatic and manual refresh support.

## Typical Usage
- List all papers: `list_papers()`
- Fuzzy search: `search_papers('distillation')`
- Extract full text: `read_paper('Paper Title')`
- Manually refresh backup: `refresh_backup()`

## Application Scenarios
- LLM-based literature review and knowledge extraction
- Automated research assistants
- Academic data mining and analysis

## Requirements
- Python 3.10+
- EndNote `.enl` file and corresponding `.Data` folder
- MCP/fastmcp runtime environment

## Installation
1. Install [uv](https://github.com/astral-sh/uv) if you don't have it:
   ```bash
   pip install uv
   # or see https://github.com/astral-sh/uv for other installation methods
   ```
2. Install dependencies using uv (recommended):
   ```bash
   uv pip install -r requirements.txt
   ```
   The main dependencies are:
   - fastmcp>=2.8.1
   - pypdf>=5.6.0

   A requirements.txt file is provided for compatibility, but uv is the recommended tool for dependency management.

## Configuration
You need to provide the path to your EndNote `.enl` file and the corresponding `.Data` folder. Optionally, you can enable detailed logging.

You may also enable backup mode with the `--use-backup` or `-b` option. When enabled, all database operations are performed on a `.enl.backup` file, which is automatically refreshed from the original `.enl` file at startup. You can manually refresh the backup at any time using the `refresh_backup()` MCP tool.

> **Why Backup Mode?**
>
> EndNote software locks the `.enl` file while it is running, preventing other programs from accessing it. This means that when you are viewing or editing references in EndNote, this tool cannot operate on the original `.enl` file. To solve this, backup mode was introduced: all operations are performed on a `.enl.backup` copy. **When you need to refresh the backup, you must first close EndNote** to release the file lock; otherwise, the refresh will fail.

## Running the Server
Start the MCP server with the required arguments:
```bash
python server.py --enl-file <path-to-your.enl> --data-folder <path-to-your.Data> [--enable-log] [--use-backup]
# or using short options:
python server.py -e <path-to-your.enl> -d <path-to-your.Data> -l -b
```
- `--enl-file`, `-e`: Path to the EndNote `.enl` file (required)
- `--data-folder`, `-d`: Path to the EndNote `.Data` folder (required)
- `--enable-log`, `-l`: Enable detailed log output (optional)
- `--use-backup`, `-b`: Use `.enl.backup` for all DB operations (optional, enables backup mode; the backup is auto-refreshed at startup)

When backup mode is enabled, all operations are performed on the `.enl.backup` file. The backup is automatically refreshed from the original `.enl` file at server startup, and you can manually refresh it at any time using the `refresh_backup()` tool.

## MCP Server Configuration

To integrate this service with MCP-compatible clients or orchestration tools, you can define an entry in your `mcp.json` configuration. Example:

```json
{
  "mcpServers": {
    "enl_reader_mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "<path-to-your-clone>",
        "-m",
        "server",
        "-e",
        "E:/EndNoteLib/your_library.enl",
        "-d",
        "E:/EndNoteLib/your_library.Data",
        "-l",
        "-b"
      ]
    }
  }
}
```
- Replace `<path-to-your-clone>` with the actual path where you cloned this repository.
- Adjust the paths to your `.enl` file and `.Data`
- Add `-b` to enable backup mode if desired. When enabled, the service will operate on a `.enl.backup` file and support manual refresh via the `refresh_backup` tool.

## MCP Tools

- `list_papers(offset=0, limit=10)`: List all references with pagination.
- `search_papers(query)`: Fuzzy search references by title or keywords.
- `read_paper(title)`: Get metadata and PDF full text by (fuzzy) title.
- `refresh_backup()`: Manually refresh the `.enl.backup` file (only available when backup mode is enabled; has no effect if backup mode is off).

**Note:** The `refresh_backup` tool is only effective when backup mode is enabled. Backup mode is recommended for scenarios requiring read-only or safer access to the EndNote library.