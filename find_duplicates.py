import argparse
import hashlib
import os
import sys
from collections import defaultdict


def get_file_hash(filepath, chunk_size=65536):
    """Generates an MD5 hash for a file, reading in chunks for memory efficiency."""
    hasher = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (PermissionError, OSError):
        return None


def find_duplicates(root_dir):
    """Traverses deep directory structures and identifies duplicate files."""
    size_map = defaultdict(list)
    duplicates = defaultdict(list)

    print(f"Scanning directory tree at: {root_dir}...")

    # Pass 1: Group files by size
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)

            if not os.path.islink(filepath):
                try:
                    file_size = os.path.getsize(filepath)
                    size_map[file_size].append(filepath)
                except (PermissionError, OSError):
                    continue

    # Pass 2: Hash files sharing the exact same size
    candidate_groups = [
        paths for paths in size_map.values() if len(paths) > 1
    ]
    total_candidates = sum(len(paths) for paths in candidate_groups)
    print(
        f"Found {len(candidate_groups)} potential duplicate size groups ({total_candidates} files). Hashing content..."
    )

    for paths in candidate_groups:
        hash_map = defaultdict(list)
        for filepath in paths:
            file_hash = get_file_hash(filepath)
            if file_hash:
                hash_map[file_hash].append(filepath)

        for file_hash, matched_paths in hash_map.items():
            if len(matched_paths) > 1:
                duplicates[file_hash] = matched_paths

    return duplicates


def main():
    parser = argparse.ArgumentParser(
        description="Find and optionally remove duplicate files in a directory."
    )
    parser.add_argument(
        "directory",
        type=str,
        help="Path to the directory you want to scan for duplicates",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Automatically delete duplicate files, leaving only one copy.",
    )

    args = parser.parse_args()
    target_directory = os.path.abspath(args.directory)

    if not os.path.isdir(target_directory):
        print(
            f"Error: Path '{target_directory}' is not a valid directory.",
            file=sys.stderr,
        )
        sys.exit(1)

    duplicate_results = find_duplicates(target_directory)

    if not duplicate_results:
        print("\nNo duplicate files found.")
        return

    print(f"\nFound {len(duplicate_results)} sets of duplicate files:\n")

    deleted_count = 0
    freed_space = 0

    for idx, (file_hash, paths) in enumerate(duplicate_results.items(), 1):
        # Keep the path with the shortest file path string length as the original
        paths_sorted = sorted(paths, key=len)
        original = paths_sorted[0]
        duplicates_to_remove = paths_sorted[1:]

        print(f"Group {idx} (MD5: {file_hash}):")
        print(f"  [KEEP]   {original}")

        for dup_path in duplicates_to_remove:
            if args.delete:
                try:
                    file_size = os.path.getsize(dup_path)
                    os.remove(dup_path)
                    print(f"  [DELETED] {dup_path}")
                    deleted_count += 1
                    freed_space += file_size
                except (PermissionError, OSError) as e:
                    print(f"  [ERROR] Could not delete {dup_path}: {e}")
            else:
                print(f"  [DUPLICATE] {dup_path}")

        print("-" * 50)

    if args.delete:
        mb_freed = freed_space / (1024 * 1024)
        print(
            f"\nDeletion Complete! Removed {deleted_count} duplicate files and freed {mb_freed:.2f} MB."
        )


if __name__ == "__main__":
    main()