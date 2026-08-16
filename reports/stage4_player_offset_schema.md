# Stage 4 Player Offset Schema

Scope: automated read-only disassembly of small `onlinemode::ParameterPlayerDefine` accessors. These are candidate in-memory backing-data offsets, not confirmed file offsets.

**Accessors selected:** 196

**Field access records:** 325

**Single-offset field candidates:** 73

## High-Confidence Offset Candidates

| Field | Offset | Widths | Reads | Writes | Notes |
|---|---:|---|---|---|---|
| `AppearanceId` | `0x1b0` | `u32` | `GetAppearanceId` | `SetAppearanceId` |  |
| `AssistSeason` | `0x174` | `u32` | `GetAssistSeason` | `SetAssistSeason` |  |
| `AssistSum` | `0x178` | `u32` | `GetAssistSum` | `SetAssistSum` |  |
| `AssociationRentalPlayer` | `0x334` | `u8` | `IsAssociationRentalPlayer` | `-` |  |
| `BonusWT` | `0x310` | `u32` | `GetBonusWT` | `SetBonusWT` |  |
| `ComTeam` | `0x348` | `u8` | `IsComTeam` | `-` |  |
| `ContractPeriod` | `0x1e0` | `u32` | `GetContractPeriod` | `SetContractPeriod` |  |
| `ContractPeriodMax` | `0x1dc` | `u32` | `GetContractPeriodMax` | `SetContractPeriodMax` |  |
| `ContractPeriodRequest` | `0x1e4` | `u32` | `GetContractPeriodRequest` | `SetContractPeriodRequest` |  |
| `ContractSalary` | `0x1f0` | `u32` | `GetContractSalary` | `-` |  |
| `ContractStatus` | `0x210` | `u32` | `GetContractStatus` | `SetContractStatus` |  |
| `CreateTime` | `0x218` | `u32` | `GetCreateTime` | `SetCreateTime` |  |
| `DeleteType` | `0x214` | `u32` | `GetDeleteType` | `SetDeleteType` |  |
| `DummyPlayerSerialId` | `0xe68` | `u64` | `SetDummyPlayerSerialId` | `-` |  |
| `EnableElite` | `0x337` | `u8` | `IsEnableElite` | `-` |  |
| `EnablePlayerInLegendTeam` | `0x314` | `u8` | `IsEnablePlayerInLegendTeam` | `SetEnablePlayerInLegendTeam` | bitfield |
| `FamePoint` | `0x318` | `u32` | `GetFamePoint` | `SetFamePoint` |  |
| `FeaturedId` | `0x358` | `u32` | `GetFeaturedId` | `SetFeaturedId` |  |
| `GameSeason` | `0x164` | `u32` | `GetGameSeason` | `SetGameSeason` |  |
| `GameSum` | `0x168` | `u32` | `GetGameSum` | `SetGameSum` |  |
| `GoalSeason` | `0x16c` | `u32` | `GetGoalSeason` | `SetGoalSeason` |  |
| `GoalSum` | `0x170` | `u32` | `GetGoalSum` | `SetGoalSum` |  |
| `GrowthStartAge` | `0x228` | `u8` | `GetGrowthStartAge` | `SetGrowthStartAge` |  |
| `GrowthType` | `0x31c` | `u32` | `GetGrowthType` | `SetGrowthType` |  |
| `Id` | `0x2c` | `u64` | `GetId` | `SetId` |  |
| `IdExclusionSeazonDataType` | `0x30` | `u32` | `GetIdExclusionSeazonDataType` | `-` | bitfield |
| `IsAssociationRentalPlayer` | `0x334` | `u8` | `-` | `SetIsAssociationRentalPlayer` | bitfield |
| `IsEnableElite` | `0x337` | `u8` | `-` | `SetIsEnableElite` | bitfield |
| `IsRegulationOut` | `0x340` | `u8` | `-` | `SetIsRegulationOut` | bitfield |
| `LegendStatus` | `0x1bc` | `u32` | `GetLegendStatus` | `SetLegendStatus` |  |
| `License` | `0x204` | `u32` | `GetLicense` | `SetLicense` |  |
| `LimitBreakNum` | `0x344` | `u32` | `GetLimitBreakNum` | `SetLimitBreakNum` |  |
| `LoanDealStatus` | `0x330` | `u32` | `GetLoanDealStatus` | `SetLoanDealStatus` |  |
| `MarketValue` | `0x1a0` | `u64` | `GetMarketValue` | `SetMarketValue` |  |
| `MasterId` | `0x1d0` | `u64` | `GetMasterId` | `SetMasterId` |  |
| `MomentumValue` | `0x35c` | `u32` | `GetMomentumValue` | `SetMomentumValue` |  |
| `MotivationTypeOnlineMode` | `0x20c` | `u8` | `GetMotivationTypeOnlineMode` | `-` |  |
| `MotivationTypeTmpdb` | `0xf4` | `u32` | `GetMotivationTypeTmpdb` | `-` | bitfield |
| `MotivationValue` | `0x20c` | `u8` | `GetMotivationValue` | `-` |  |
| `Nationality` | `0xf4` | `u64` | `SetNationality` | `SetNationality` |  |
| `NextSalary` | `0x1ec` | `u32` | `GetNextSalary` | `SetNextSalary` |  |
| `OrderNo` | `0x224` | `u32` | `GetOrderNo` | `SetOrderNo` |  |
| `OrderStatus` | `0x34c` | `u32` | `GetOrderStatus` | `SetOrderStatus` |  |
| `OriginalTeamId` | `0xdc` | `u32` | `GetOriginalTeamId` | `-` |  |
| `OverallFromServer` | `0x21c` | `u32` | `GetOverallFromServer` | `SetOverallFromServer` |  |
| `OverAllTeamWork` | `0x28` | `u32` | `GetOverAllTeamWork` | `-` | bitfield |
| `Playable` | `0x1d8` | `u32` | `GetPlayable` | `SetPlayable` |  |
| `PlayerCategory` | `0x208` | `u32` | `GetPlayerCategory` | `SetPlayerCategory` |  |
| `PlayerId` | `0x2c` | `u64` | `GetPlayerId` | `SetPlayerId` |  |
| `PlayStyle` | `0x18` | `u64` | `GetPlayStyle, SetPlayStyle` | `SetPlayStyle` | bitfield |
| `PlayStyleHas` | `0x338` | `u32` | `GetPlayStyleHas` | `SetPlayStyleHas` |  |
| `PointSeason` | `0x17c` | `u32` | `GetPointSeason` | `SetPointSeason` |  |
| `PointSum` | `0x180` | `u32` | `GetPointSum` | `SetPointSum` |  |
| `PositionAptitude` | `0x20` | `u64` | `SetPositionAptitude` | `-` | bitfield |
| `Rarity` | `0x1c0` | `u32` | `GetRarity` | `SetRarity` |  |
| `RedSeason` | `0x194` | `u32` | `GetRedSeason` | `SetRedSeason` |  |
| `RedSum` | `0x198` | `u32` | `GetRedSum` | `SetRedSum` |  |
| `RedSuspension` | `0x19c` | `u32` | `GetRedSuspension` | `SetRedSuspension` |  |
| `RegulationOut` | `0x340` | `u8` | `IsRegulationOut` | `-` |  |
| `RentalPlayerInfo` | `0x320` | `u8` | `GetRentalPlayerInfo` | `SetRentalPlayerInfo` |  |
| `Salary` | `0x1e8` | `u32` | `GetSalary` | `SetSalary` |  |
| `SameCode` | `0x1b4` | `u32` | `GetSameCode` | `SetSameCode` |  |
| `SellPrice` | `0x1a8` | `u32` | `GetSellPrice` | `SetSellPrice` |  |
| `SerialId` | `0x1c8` | `u64` | `GetSerialId` | `-` |  |
| `SquadPosition` | `0x220` | `u32` | `GetSquadPosition` | `SetSquadPosition` |  |
| `SumYellow` | `0x18c` | `u32` | `GetSumYellow` | `SetSumYellow` |  |
| `UniformNumber` | `0x1ac` | `u32` | `GetUniformNumber` | `SetUniformNumber` |  |
| `UseFameBooster` | `0x336` | `u8` | `-` | `SetUseFameBooster` | bitfield |
| `UserId` | `0x1b8` | `u32` | `GetUserId` | `SetUserId` |  |
| `Valid` | `0x1c8` | `u64` | `IsValid` | `-` |  |
| `YellowMaxTimes` | `0x190` | `u32` | `GetYellowMaxTimes` | `SetYellowMaxTimes` |  |
| `YellowSeason` | `0x184` | `u32` | `GetYellowSeason` | `SetYellowSeason` |  |
| `YellowSum` | `0x188` | `u32` | `GetYellowSum` | `SetYellowSum` |  |

## Outputs

- `analysis\stage4_player_schema\parameter_player_define_offsets.csv`
- `analysis\stage4_player_schema\parameter_player_define_offsets.json`
- `analysis\stage4_player_schema\player_offset_probe_disasm.txt`

## Next

- Manually review fields with multiple offsets or bitfield evidence.
- Map `PrepareDataFromJson*` JSON keys onto this in-memory schema.
- Only after a real record is found, test read-only binary-to-JSON parsing against known values.
