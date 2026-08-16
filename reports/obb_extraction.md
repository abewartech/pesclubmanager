# OBB Extraction

## Main OBB

**Path:** `original\main.104050101.jp.konami.pesclubmanager.obb`

**Size:** 789,485,556 bytes (752.91 MB)

**Format:** ZIP (PK\x03\x04 magic confirmed)

**Extraction:** SUCCESS

**Output:** `extracted/obb_main/`

**Files extracted:** 1

**Directories:** 3

**Total uncompressed size:** 789,485,288 bytes (752.9 MB)

## Notes

- Source OBB untouched — extracted to separate directory only.
- 7z used in extract-only mode (`x` command, no modification flags).
- Original OBB files remain in `original/` unmodified.

## 7z Output (tail)

```

7-Zip 24.09 (x64) : Copyright (c) 1999-2024 Igor Pavlov : 2024-11-29

Scanning the drive for archives:
1 file, 789485556 bytes (753 MiB)

Extracting archive: C:\Users\rahma\Documents\projects\abe\reverse_engineering\original\main.104050101.jp.konami.pesclubmanager.obb
--
Path = C:\Users\rahma\Documents\projects\abe\reverse_engineering\original\main.104050101.jp.konami.pesclubmanager.obb
Type = zip
Physical Size = 789485556

- PesMobile\Content\Paks\PesMobile-Android_ETC1.pak
Everything is Ok

Size:       789485288
Compressed: 789485556

```

## Patch OBB

**Path:** `original\patch.104050101.jp.konami.pesclubmanager.obb`

**Size:** 873,229,528 bytes (832.78 MB)

**Format:** CRIWARE CPK (`CPK ` magic — 0x43504B20)

**Extraction:** NOT ATTEMPTED — requires CPK-aware tool (not standard ZIP)

**Next step:** Analyze with scripts/s3_05_cpk_inspect.py

