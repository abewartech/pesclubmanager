"""
Stage 3 - Step 2+3: Extract main OBB (ZIP) to extracted/obb_main/
Then write reports/obb_extraction.md
READ-ONLY on source. Output only to extracted/.
"""
import os, subprocess, sys

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEVENZIP = r"C:\Program Files\7-Zip\7z.exe"
MAIN_OBB = os.path.join(WORKSPACE, "original", "main.104050101.jp.konami.pesclubmanager.obb")
EXTRACT_DIR = os.path.join(WORKSPACE, "extracted", "obb_main")
REPORT = os.path.join(WORKSPACE, "reports", "obb_extraction.md")

def main():
    size = os.path.getsize(MAIN_OBB)
    print(f"[*] Main OBB: {MAIN_OBB}")
    print(f"[*] Size: {size:,} bytes ({size/1024/1024:.2f} MB)")
    print(f"[*] Extract target: {EXTRACT_DIR}")

    os.makedirs(EXTRACT_DIR, exist_ok=True)

    # Use 7z to extract (read-only source, output to target dir)
    print("[*] Running 7z extraction...")
    cmd = [SEVENZIP, "x", MAIN_OBB, f"-o{EXTRACT_DIR}", "-y", "-bb1"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    success = result.returncode == 0
    stdout_tail = result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout
    stderr_tail = result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr

    print(f"[*] Return code: {result.returncode}")
    if success:
        print("[+] Extraction SUCCESS")
    else:
        print("[!] Extraction FAILED or partial")

    # Count extracted files
    file_count = 0
    dir_count = 0
    total_size = 0
    for dirpath, dirs, files in os.walk(EXTRACT_DIR):
        dir_count += len(dirs)
        for fn in files:
            fp = os.path.join(dirpath, fn)
            try:
                total_size += os.path.getsize(fp)
            except:
                pass
            file_count += 1

    print(f"[*] Extracted: {file_count} files, {dir_count} dirs, {total_size/1024/1024:.1f} MB total")

    # Write report
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write("# OBB Extraction\n\n")
        f.write("## Main OBB\n\n")
        f.write(f"**Path:** `{os.path.relpath(MAIN_OBB, WORKSPACE)}`\n\n")
        f.write(f"**Size:** {size:,} bytes ({size/1024/1024:.2f} MB)\n\n")
        f.write(f"**Format:** ZIP (PK\\x03\\x04 magic confirmed)\n\n")
        f.write(f"**Extraction:** {'SUCCESS' if success else 'FAILED'}\n\n")
        f.write(f"**Output:** `extracted/obb_main/`\n\n")
        f.write(f"**Files extracted:** {file_count}\n\n")
        f.write(f"**Directories:** {dir_count}\n\n")
        f.write(f"**Total uncompressed size:** {total_size:,} bytes ({total_size/1024/1024:.1f} MB)\n\n")
        f.write("## Notes\n\n")
        f.write("- Source OBB untouched — extracted to separate directory only.\n")
        f.write("- 7z used in extract-only mode (`x` command, no modification flags).\n")
        f.write("- Original OBB files remain in `original/` unmodified.\n\n")
        f.write("## 7z Output (tail)\n\n")
        f.write("```\n")
        f.write(stdout_tail)
        f.write("\n```\n\n")
        if stderr_tail.strip():
            f.write("## 7z Stderr\n\n```\n")
            f.write(stderr_tail)
            f.write("\n```\n\n")

        f.write("## Patch OBB\n\n")
        patch_path = os.path.join(WORKSPACE, "original", "patch.104050101.jp.konami.pesclubmanager.obb")
        patch_size = os.path.getsize(patch_path)
        f.write(f"**Path:** `{os.path.relpath(patch_path, WORKSPACE)}`\n\n")
        f.write(f"**Size:** {patch_size:,} bytes ({patch_size/1024/1024:.2f} MB)\n\n")
        f.write(f"**Format:** CRIWARE CPK (`CPK ` magic — 0x43504B20)\n\n")
        f.write(f"**Extraction:** NOT ATTEMPTED — requires CPK-aware tool (not standard ZIP)\n\n")
        f.write(f"**Next step:** Analyze with scripts/s3_05_cpk_inspect.py\n\n")

    print(f"[+] Report: {REPORT}")

if __name__ == '__main__':
    main()
