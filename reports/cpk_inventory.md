# CPK Inventory

## Patch OBB (CRIWARE CPK)

**Path:** `original/patch.104050101.jp.konami.pesclubmanager.obb`

**Size:** 873,229,528 bytes (832.78 MB)

**SHA-256:** `e6b194d430b7b095e6179645714d5da429e6566205eb7ccde7ea6169505ff1db`

**Magic:** `CPK ` (bytes: `43 50 4B 20`) — CRIWARE CPK container confirmed


## Structure Analysis

| Offset | Identifier | Value | Notes |
|--------|------------|-------|-------|
| 0x0000 | Magic | `CPK ` | CRIWARE CPK confirmed |
| 0x0004 | Unk | `0x00000000` | Reserved |
| 0x0008 | UTF block size | `832` bytes | Size of encrypted @UTF at 0x10 |
| 0x0010 | @UTF header | ENCRYPTED | XOR-encrypted; key[0:4]=`5F CB A7 B3` |
| 0x07FF | `ITOC` | 4-byte sig | Index Table of Contents section present |
| 0x0800 | `TOC ` | 4-byte sig | Table of Contents section present |
| 0x0808 | TOC data size | `1232` bytes | |
| 0x0810 | TOC @UTF | ENCRYPTED | Same XOR pattern as 0x10 |

## Encryption Analysis

The CPK @UTF tables are **XOR-encrypted** using CRIWARE's proprietary algorithm.

**Key bytes recovered (partial):** `5F CB A7 B3` (positions 0-3)

**Key derivation:** Unknown — standard CRIWARE LFSR (0x4E6F*seed+0x5D) does not match.
Period-4 key produces `@UTF` magic correctly but yields implausible table sizes.
Period-8 key extension: no plausible @UTF structure found.

**Same XOR stream** applies to both CPK header UTF (0x10) and TOC UTF (0x810).

**Implication:** To decrypt, the full key derivation algorithm or source key material is required.

**Unencrypted data:** The actual file payloads within the CPK may be unencrypted (only headers encrypted).


## TOC/ITOC Sections Found

| Section | Offset | Size field |
|---------|--------|------------|
| ITOC | 0x07FF | — |
| TOC | 0x0800 | 1232 bytes |


## String Scan Results

5,237 strings matched player/team/parameter keywords — all from Adobe XMP metadata
embedded in PNG texture files stored inside the CPK. No CPK file listing available
without decrypting the @UTF index tables.


## Recommended Next Steps

1. **Obtain the full XOR key** — can be found in `libafp-core.so` or `libavs2-core.so`
   static strings or initialization code (CRIWARE's ACE library initializes the CPK key)
2. **Use community tools** (cpkmakec, CriPackedFileMaker) if the game uses default key
3. **Dump at runtime** — the game mounts the CPK and has the decrypted file list in memory
4. **Search libafp-core.so for key bytes** `5F CB A7 B3` or adjacent key schedule code
