
# Duplicate File Finder & Cleaner

A fast, lightweight, and memory-efficient Python command-line utility designed to find and optionally delete duplicate files across deep, nested directory structures.

## Features

- **Fast Two-Pass Scanning:** First filters files by byte size, then computes MD5 hashes only for files that share identical sizes. This dramatically speeds up scans on large directories.
- **Deep Directory Traversal:** Recursively scans through complex, nested folder structures using `os.walk()`.
- **Memory Efficient:** Reads files in 64 KB chunks, allowing it to hash large multi-gigabyte files without memory spikes or crashing.
- **Safe & Robust:**
  - Handles permission errors, broken symlinks, and OS restrictions gracefully without crashing.
  - Defaults to **dry-run mode** (read-only output) unless explicit deletion is enabled.
  - Automatically selects and retains the file with the shortest path string length as the original copy.
- **Clear Disk Cleanup Metrics:** Reports total files removed and space freed in MB after deletion.

---

## Requirements

- **Python 3.8+**
- Standard Python libraries only (`argparse`, `hashlib`, `os`, `sys`, `collections`) -- no external `pip` dependencies required.

---

## Installation

Clone or download the repository, or simply save `find_duplicates.py` to your working directory.

```bash
git clone [https://github.com/your-repo/duplicate-file-finder.git](https://github.com/your-repo/duplicate-file-finder.git)
cd duplicate-file-finder