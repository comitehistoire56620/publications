# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "typer",
# ]
# ///
import re
from pathlib import Path
import typer

app = typer.Typer()

@app.command()
def main(year: str):
    """
    Generate a summary for the given year for the printable version.
    """
    repo_root = Path(__file__).parent.parent
    summary_path = repo_root / "src" / "SUMMARY.md"
    output_path = repo_root / "src" / "SUMMARY_PRINT.md"
    
    if not summary_path.exists():
        print(f"Error: {summary_path} not found")
        raise typer.Exit(code=1)
        
    content = summary_path.read_text(encoding="utf-8")
    
    # Regex to find the year section.
    # It searches for "- [Year](...)" and captures lines until the next "- [" or end of string.
    # Adjust regex based on actual file structure (indented lists).
    
    # Find the start of the year section
    year_pattern = re.compile(rf"^\s*-\s*\[{year}\].*?$", re.MULTILINE)
    match = year_pattern.search(content)
    
    if not match:
        print(f"Error: Could not find section for year {year} in SUMMARY.md")
        raise typer.Exit(code=1)
    
    start_index = match.start()
    
    # Find the start of the next section (next pattern like "- [...") 
    # We strip the current line to check indentation logic validation if needed, 
    # but simple split might work if structure is consistent.
    
    # Simpler approach: Iterate lines
    lines = content.splitlines()
    year_lines = []
    in_year = False
    base_indent = -1
    
    for line in lines:
        stripped = line.strip()
        # Check for year start
        if re.match(rf"-\s*\[{year}\]", stripped):
            in_year = True
            year_lines.append(f"# {year} - Printable Version")
            # Calculate base indent of the year line to know when we exit
            base_indent = len(line) - len(line.lstrip())
            continue
            
        if in_year:
            if not stripped:
                continue
                
            current_indent = len(line) - len(line.lstrip())
            
            # If we hit a line with same or less indent than the year line, we are done
            # (assuming standard mdbook summary structure where children are indented)
            # BUT: The year line is "- [2024](...)", children are "    - [Post](...)"
            if current_indent <= base_indent:
                break
                
            # Add the line to our new summary
            # We likely want to dedent one level so they become top level chapters in the new summary
            # or keep them as is?
            # If we keep them as indented, they need a parent.
            # Let's unindent them to make them top-level items in the print book.
            
            # Remove 4 spaces (or 2) of indentation
            # Assuming 4 spaces for markdown list indentation
            if line.startswith("    "):
                year_lines.append(line[4:])
            elif line.startswith("\t"):
                 year_lines.append(line[1:])
            else:
                # If structure is weird, just keep it, but it might break hierarchy
                year_lines.append(line)

    if not year_lines:
         print(f"Error: No content found for year {year}")
         raise typer.Exit(code=1)
         
    # Write the new summary
    output_content = "\n".join(year_lines)
    output_path.write_text(output_content, encoding="utf-8")
    print(f"Successfully generated {output_path} for year {year}")

if __name__ == "__main__":
    app()
