# Stage 28 — Game Logic Architecture

## Scope

User request: map the game logic (match, training, etc.) for offline
play. Static RE from `.dynsym`.

## 1. Key insight: match engine is CLIENT-SIDE

The `match::` namespace (10,391 symbols, 332 classes) is a complete
football simulation running on the device:

| Class | Symbols | Role |
|-------|---------|------|
| `ai` | 1,825 | AI decision-making |
| `player` | 961 | player behavior |
| `registry` | 1,822 | entity registry |
| `anime` | 1,624 | animation |
| `camera` | 534 | cameras |
| `Match` | 40 | match controller |
| `Flow` | 185 | match flow/state |
| `Ball` | 32 | ball physics |
| `Human` | 37 | human input |

Plus `physx::` (6,572) for physics and `fox::` (3,619) for rendering.

**The server does NOT simulate matches.** It provides data; the
client simulates.

## 2. Server-side logic: `onlineapi::` (168 classes)

Each `Do*` class is one server operation. Sample:

- `DoTraining`, `DoQualityTraining` — training results
- `DoContractPlayer`, `DoScoutPlayer`, `DoObtainScoutPlayer` — transfers
- `DoItemPurchase`, `DoItemUse`, `DoItemExchange` — items
- `DoConstructFacility`, `DoCompletionFacility` — facilities
- `DoBidAuction`, `DoTradeScout` — auction/trading
- `AuthUser`, `CheckUpdate` — auth/version
- `ClassicTournament`, `AssociationCupSaveMyTeamInfo` — competitions

For offline play, the stub server must implement these operations.
They are discrete and independent — each can be stubbed one at a
time, starting with the boot sequence (`AuthUser` → `CheckUpdate` →
`top.php`).

## 3. What the stub needs (priority order)

1. **Auth/boot**: `AuthUser`, `CheckUpdate`, `top.php` — get the
   client past the title screen.
2. **Team data**: squad, players, formation — let the client display
   the team.
3. **Match setup**: opponent data — let the client start a match
   (simulation is local).
4. **Post-match**: result submission — persist outcome.
5. **Training/transfers**: `DoTraining`, `DoContractPlayer`, etc. —
   progression systems.

## 4. Scale assessment

- 168 `onlineapi::` operations to stub for full functionality.
- Match/training *simulation* is already on-device — no need to
  reimplement.
- Realistic path: iterate boot → team → match → progression,
  stubbing one operation at a time against the observed client
  behavior.

## 5. Not done

- Per-operation request/response schemas (need dynamic tracing).
- Which operations the boot sequence actually calls.
- Client-side validation that might reject stubbed data.
