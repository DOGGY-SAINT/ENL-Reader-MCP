# EndNote MCP Service

This project provides an automated service for reading EndNote `.enl` libraries and exposing their contents via the MCP (Modular Command Protocol) interface. It enables structured, programmatic access to bibliographic data and PDF full texts for downstream LLMs or automation clients.

## Features
- **Automatic EndNote Library Parsing**: Reads `.enl` (SQLite) files and associated `.Data` folders.
- **MCP Tool Interface**: Exposes all functions as MCP tools for easy integration with LLMs or workflow engines.
- **List All References**: Enumerate all bibliographic entries with metadata.
- **Fuzzy Search**: Search references by (partial) title or keywords, supporting both English and Chinese.
- **PDF Full Text Extraction**: Retrieve and extract the full text of attached PDF files by paper title.

## Typical Usage
- List all papers: `list_papers()`
- Fuzzy search: `search_papers('distillation')`
- Extract full text: `read_paper('Paper Title')`

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

## Running the Server
Start the MCP server with the required arguments:
```bash
python server.py --enl-file <path-to-your.enl> --data-folder <path-to-your.Data> [--enable-log]
# or using short options:
python server.py -e <path-to-your.enl> -d <path-to-your.Data> -l
```
- `--enl-file`, `-e`: Path to the EndNote `.enl` file (required)
- `--data-folder`, `-d`: Path to the EndNote `.Data` folder (required)
- `--enable-log`, `-l`: Enable detailed log output (optional)

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
        "-l"
      ]
    }
  }
}
```
- Replace `<path-to-your-clone>` with the actual path where you cloned this repository.
- Adjust the paths to your `.enl` file and `.Data`