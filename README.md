# PES Club Manager (PESCM) Reverse Engineering Workspace

This workspace is dedicated to the static analysis, asset extraction, and in-memory schema recovery of the Android game **PES Club Manager** (Package: `jp.konami.pesclubmanager`, Version: `4.5.1`, Version Code: `104050101`). 

The analysis is performed completely **read-only**, without bypassing anti-cheat, executing the binary, modifying game clients, or accessing production servers.

---

## 📊 Project Status & Target Dashboard

| Domain | Status | Target Details | Confidence |
| :--- | :--- | :--- | :--- |
| **Game Engine** | 🟢 Identified | **Unreal Engine 4.22.3** (branch: `++UE4+Release-4.22`) | **CONFIRMED** |
| **Main OBB** | 🟢 Decoupled | ZIP container hosting `PesMobile-Android_ETC1.pak` | **CONFIRMED** |
| **Patch OBB** | 🟢 Decoupled | CRIWARE CPK container containing animation & definitions | **CONFIRMED** |
| **Native Libraries** | 🟡 Analyzed | Static exports mapping of `libUE4.so`, `libafp-core.so`, `libavs2-core.so` | **HIGH** |
| **Player Database** | 🟡 Discovered | In-memory schema mapped; file structure pending | **HIGH** |
| **Save Data** | ⚪ Investigation | Leads identified: `sys::SaveData` & `systemdata::SystemData` | **MEDIUM** |
| **Network Endpoints** | ⚪ Investigation | Static domain seeds identified; no dynamic probing done | **HIGH** |

---

## 📂 Workspace Layout

Below is a map of the workspace directory hierarchy:

```text
reverse_engineering/
├── README.md                           # This document (workspace index)
├── PES-CLUB-MANAGER-v4-5-1.apk         # Target game APK (unmodified)
├── apktool_3.0.3.jar                   # APK decompilation tool
├── Bytecode-Viewer-2.13.2.jar          # Java/dex decompiler and bytecode viewer
├── radare2/                            # radare2 static CLI binaries
├── Cutter/                             # Cutter GUI frontend for radare2
├── ghidra/                             # Ghidra project folder
├── original/                           # Pristine copies of APK & OBB files
│   ├── PES-CLUB-MANAGER-v4-5-1.apk
│   ├── main.104050101.jp.konami.pesclubmanager.obb
│   └── patch.104050101.jp.konami.pesclubmanager.obb
├── backups/                            # Safekeeping backup archives
├── jp.konami.pesclubmanager/            # Working directory for Android OBBs
├── extracted/                          # Outputs from extraction and unpacking
│   ├── apktool/                        # Decoded APK files (Smali, Manifest, Assets)
│   └── obb_main/                       # Unzipped contents of the main OBB
├── analysis/                           # Processed databases, logs, and exports
│   ├── stage3_asset_paths/             # Lists of asset paths extracted from containers
│   ├── stage4_player_schema/           # CSV/JSON mapping schemas for player fields
│   ├── cpk_listing/                    # CPK UTF table file maps
│   └── libUE4_arm64_exports.json       # Dump of all exported symbols from libUE4.so
├── scripts/                            # Python automation and parsing scripts
├── reports/                            # Markdown summaries documenting project stages
└── reverse-skill/                      # Local reverse engineering frameworks/rules
```

---

## 📑 Interactive Reports Index

Detailed technical reports documenting each phase of the project can be found under the [reports/](reports/) directory:

*   **🔍 Overview & Master Roadmap**
    *   [reports/reverse_engineering.md](reports/reverse_engineering.md): Master status checklist, initial findings, hypotheses, and next steps.
*   **📱 Package & Engine Analysis**
    *   [reports/apk_analysis.md](reports/apk_analysis.md): Package info, permissions, activities, services, deep links, and Smali bytecode structure.
    *   [reports/engine.md](reports/engine.md): Verification proof identifying Unreal Engine 4.22.3.
*   **🛠️ Native Library Static Analysis**
    *   [reports/native_analysis.md](reports/native_analysis.md): Analysis of target libraries (`libUE4.so`, `libafp-core.so`, `libavs2-core.so`) and exported symbol namespaces.
*   **📦 Asset Containers & Filesystems**
    *   [reports/obb_inventory.md](reports/obb_inventory.md): Magic byte checks and signatures verifying OBB formats.
    *   [reports/obb_contents.md](reports/obb_contents.md): Summary of content files in the main and patch OBB files.
    *   [reports/obb_extraction.md](reports/obb_extraction.md): Steps taken to successfully extract assets.
    *   [reports/cpk_inventory.md](reports/cpk_inventory.md): CRIWARE CPK structure, including `@UTF` headers, ITOC, ETOC, and GTOC index tables.
    *   [reports/pak_inventory.md](reports/pak_inventory.md): Struct verification of the Unreal Engine `.pak` reader.
    *   [reports/stage3_asset_path_inventory.md](reports/stage3_asset_path_inventory.md): Complete list of files found in OBB containers (totaling 49,556 main pak paths).
*   **🧬 Schema & Offset Recovery**
    *   [reports/stage4_player_symbol_schema.md](reports/stage4_player_symbol_schema.md): Complete C++ namespace mapping for `onlinemode::ParameterPlayerDefine`.
    *   [reports/stage4_player_offset_schema.md](reports/stage4_player_offset_schema.md): 73+ high-confidence field offsets (e.g., `AppearanceId`, `ContractSalary`, `Rarity`, `SquadPosition`) extracted from disassembling getter/setter models.

---

## 🔄 Reverse Engineering Chronology & Scripts

The analysis progressed through distinct chronological phases, each driven by dedicated Python automation scripts:

### 📍 Stage 1: File & Directory Inventory
*   **Goal**: Establish a baseline of original files, verify hashes, and create folders.
*   **Script**: [scripts/inventory.py](scripts/inventory.py)

### 📍 Stage 2: APK Decompilation & Static Symbol Discovery
*   **Goal**: Decompile the APK wrapper to inspect Android components and extract native dynamic symbols.
*   **Tools**: `apktool`, `radare2/rabin2`
*   **Result**: Dumped exports to [analysis/libUE4_arm64_exports.json](analysis/libUE4_arm64_exports.json).

### 📍 Stage 3: Asset Container Inspection & Parsing
*   **Goal**: Understand where the main game assets are stored. We verified that the main OBB is a ZIP container containing an Unreal `.pak` file, and the patch OBB is a CRIWARE CPK archive containing table definitions.
*   **Scripts**:
    *   [scripts/s3_01_obb_inventory.py](scripts/s3_01_obb_inventory.py): Detect file magic and compute OBB hashes.
    *   [scripts/s3_02_extract_main_obb.py](scripts/s3_02_extract_main_obb.py): Unzip the main OBB to [extracted/obb_main/](extracted/obb_main/).
    *   [scripts/s3_03_pak_reader.py](scripts/s3_03_pak_reader.py) & [scripts/s3_04_pak_reader_v2.py](scripts/s3_04_pak_reader_v2.py): Parse the Unreal `.pak` headers/indices without mounting the engine.
    *   [scripts/s3_05_cpk_inspect.py](scripts/s3_05_cpk_inspect.py): Read the custom binary `@UTF` table layout of the CRIWARE CPK file to list virtual files.
*   **Outputs**: [reports/stage3_asset_path_inventory.md](reports/stage3_asset_path_inventory.md) listing all unique assets.

### 📍 Stage 4: In-Memory Player Schema Offset Recovery
*   **Goal**: Recover the field layout for in-memory player attributes by disassembling accessor methods inside `libUE4.so`.
*   **Method**: Automate a radare2 script to search for assembly patterns matching backing pointer offset accessors:
    ```assembly
    ldr xN, [x0, 0x28]        ; Load backing player data struct pointer
    ldr w0, [xN, <offset>]    ; Access field at specific offset
    ```
*   **Scripts**:
    *   [scripts/s4_01_player_symbol_schema.py](scripts/s4_01_player_symbol_schema.py): Extract and filter player-specific C++ namespace symbol maps.
    *   [scripts/s4_02_extract_player_offsets.py](scripts/s4_02_extract_player_offsets.py): Automate radare2 disassembler, parse instructions, and compile target offsets.
*   **Outputs**: 
    *   JSON schema: [analysis/stage4_player_schema/parameter_player_define_offsets.json](analysis/stage4_player_schema/parameter_player_define_offsets.json)
    *   CSV schema: [analysis/stage4_player_schema/parameter_player_define_offsets.csv](analysis/stage4_player_schema/parameter_player_define_offsets.csv)
    *   Offset report: [reports/stage4_player_offset_schema.md](reports/stage4_player_offset_schema.md)

---

## 🛠️ Setup & Execution Guide

### Prerequisites
1. **Python 3.x**
2. **Java Runtime Environment (JRE)** (for decompiling via `apktool` / `Bytecode Viewer`)
3. **radare2 Command-Line Tools** (already bundled in the [radare2/](radare2/) folder for Windows)

### Execution Steps
To rerun any stage of the static analysis:

1. **Verify OBB Headers**:
   ```powershell
   python scripts/s3_01_obb_inventory.py
   ```
2. **Extract Main OBB Assets**:
   ```powershell
   python scripts/s3_02_extract_main_obb.py
   ```
3. **Parse OBB CPK Header**:
   ```powershell
   python scripts/s3_05_cpk_inspect.py
   ```
4. **Probe Player Schema Offsets**:
   Make sure `extracted/apktool/PES-CLUB-MANAGER-v4-5-1/` is populated with `libUE4.so` under `lib/arm64-v8a/`, then run:
   ```powershell
   python scripts/s4_01_player_symbol_schema.py
   python scripts/s4_02_extract_player_offsets.py
   ```

---

*Disclaimer: This repository does not distribute copyrighted game binaries. Paths and signatures are logged solely for research, documentation, and tooling analysis.*
