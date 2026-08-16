# Stage 4 Player Symbol Schema

Scope: exported native symbol analysis only. Field names below are candidates, not confirmed binary offsets/types.

**Symbols analyzed:** 703

**ParameterPlayerDefine field candidates:** 151

## Category Counts

| Category | Count |
|---|---:|
| `Set` | 301 |
| `Get` | 182 |
| `other` | 162 |
| `Is` | 49 |
| `Has` | 4 |
| `Prepare` | 3 |
| `Clear` | 2 |

## Top Owners

| Owner | Count |
|---|---:|
| `onlinemode::ParameterPlayerDefine` | 275 |
| `menu::utility` | 81 |
| `menu` | 43 |
| `menu::util` | 26 |
| `menu::CommonPlayerList` | 24 |
| `tmpdb::Player` | 18 |
| `menu::squadutil` | 14 |
| `menu::SquadNewMain` | 11 |
| `onlinemode` | 9 |
| `game_mode::MatchListener` | 8 |
| `menusystem::NodeRectIconOverAllPositionSmart` | 7 |
| `onlinemode::ParameterAssociationCup` | 7 |
| `game_mode` | 6 |
| `menu::LoanDealStart` | 6 |
| `menu::SquadNewSub` | 6 |
| `menu::TrainerPlayerList` | 6 |
| `menu::CommonPlayerParameterPage1` | 5 |
| `menu::DeliveryWork` | 5 |
| `menu::SquadSetplay` | 5 |
| `mode` | 5 |

## High-Signal Field Candidates

| Field candidate | Getter | Setter | Predicate/Other evidence |
|---|---|---|---|
| `AbilityParameter` | `GetAbilityParameter` | `SetAbilityParameter` | `-` |
| `AbilityParameterFromDB` | `-` | `SetAbilityParameterFromDB` | `-` |
| `Age` | `GetAge` | `SetAge` | `-` |
| `AppearanceId` | `GetAppearanceId` | `SetAppearanceId` | `-` |
| `AppearanceParameter` | `GetAppearanceParameter` | `SetAppearanceParameter` | `-` |
| `AssistSeason` | `GetAssistSeason` | `SetAssistSeason` | `-` |
| `AssistSum` | `GetAssistSum` | `SetAssistSum` | `-` |
| `AssociationRentalPlayer` | `-` | `-` | `IsAssociationRentalPlayer` |
| `AssoCrashRegulationIn` | `-` | `-` | `IsAssoCrashRegulationIn` |
| `BonusWT` | `GetBonusWT` | `SetBonusWT` | `-` |
| `CaptainOverAll` | `GetCaptainOverAll` | `-` | `-` |
| `ClassicTournamentLatestSeasonPlayer` | `-` | `-` | `IsClassicTournamentLatestSeasonPlayer` |
| `ComTeam` | `-` | `-` | `IsComTeam` |
| `Condition` | `GetCondition` | `SetCondition` | `-` |
| `ContractPeriod` | `GetContractPeriod` | `SetContractPeriod` | `-` |
| `ContractPeriodMax` | `GetContractPeriodMax` | `SetContractPeriodMax` | `-` |
| `ContractPeriodRequest` | `GetContractPeriodRequest` | `SetContractPeriodRequest` | `-` |
| `ContractSalary` | `GetContractSalary` | `-` | `-` |
| `ContractSalaryListFromJson` | `-` | `SetContractSalaryListFromJson` | `-` |
| `ContractStatus` | `GetContractStatus` | `SetContractStatus` | `-` |
| `CreateTime` | `GetCreateTime` | `SetCreateTime` | `-` |
| `CupEntryRuleStatus` | `GetCupEntryRuleStatus` | `SetCupEntryRuleStatus` | `-` |
| `CupEntryRuleStatusList` | `GetCupEntryRuleStatusList` | `SetCupEntryRuleStatusList` | `-` |
| `CupEntryRuleStatusListFromJson` | `-` | `SetCupEntryRuleStatusListFromJson` | `-` |
| `Data` | `GetData` | `SetData` | `-` |
| `DeleteType` | `GetDeleteType` | `SetDeleteType` | `-` |
| `DevelopmentType` | `GetDevelopmentType` | `SetDevelopmentType` | `-` |
| `DummyPlayerSerialId` | `-` | `SetDummyPlayerSerialId` | `-` |
| `ElitePlayer` | `-` | `-` | `IsElitePlayer` |
| `EnableElite` | `-` | `-` | `IsEnableElite` |
| `EnablePlayerInLegendTeam` | `-` | `SetEnablePlayerInLegendTeam` | `IsEnablePlayerInLegendTeam` |
| `FamePoint` | `GetFamePoint` | `SetFamePoint` | `-` |
| `FeaturedId` | `GetFeaturedId` | `SetFeaturedId` | `-` |
| `FeaturedIdInfo` | `GetFeaturedIdInfo` | `-` | `-` |
| `GameSeason` | `GetGameSeason` | `SetGameSeason` | `-` |
| `GameSum` | `GetGameSum` | `SetGameSum` | `-` |
| `GoalSeason` | `GetGoalSeason` | `SetGoalSeason` | `-` |
| `GoalSum` | `GetGoalSum` | `SetGoalSum` | `-` |
| `GrowthGraphParameter` | `-` | `SetGrowthGraphParameter` | `-` |
| `GrowthListBase` | `GetGrowthListBase` | `SetGrowthListBase` | `-` |
| `GrowthListTraining` | `GetGrowthListTraining` | `SetGrowthListTraining` | `-` |
| `GrowthStartAge` | `GetGrowthStartAge` | `SetGrowthStartAge` | `-` |
| `GrowthType` | `GetGrowthType` | `SetGrowthType` | `-` |
| `Id` | `GetId` | `SetId` | `-` |
| `IdExclusionSeazonDataType` | `GetIdExclusionSeazonDataType` | `-` | `-` |
| `InjuryLength` | `GetInjuryLength` | `SetInjuryLength` | `-` |
| `IsAssociationRentalPlayer` | `-` | `SetIsAssociationRentalPlayer` | `-` |
| `IsComTeam` | `-` | `SetIsComTeam` | `-` |
| `IsEnableElite` | `-` | `SetIsEnableElite` | `-` |
| `IsRegulationOut` | `-` | `SetIsRegulationOut` | `-` |
| `KickerOverAll` | `GetKickerOverAll` | `-` | `-` |
| `LegendReserveTeamPriorityForSort` | `GetLegendReserveTeamPriorityForSort` | `-` | `-` |
| `LegendStatus` | `GetLegendStatus` | `SetLegendStatus` | `-` |
| `License` | `GetLicense` | `SetLicense` | `-` |
| `LimitBreakNum` | `GetLimitBreakNum` | `SetLimitBreakNum` | `-` |
| `LimitBreakNumMax` | `GetLimitBreakNumMax` | `-` | `-` |
| `LimitBreakParaMax` | `GetLimitBreakParaMax` | `-` | `-` |
| `LimitBreakParaMaxNext` | `GetLimitBreakParaMaxNext` | `-` | `-` |
| `LimitBreakParaMaxNow` | `GetLimitBreakParaMaxNow` | `-` | `-` |
| `LimitBreakParaMaxOriginal` | `GetLimitBreakParaMaxOriginal` | `-` | `-` |
| `LoanDealStatus` | `GetLoanDealStatus` | `SetLoanDealStatus` | `-` |
| `MarketValue` | `GetMarketValue` | `SetMarketValue` | `-` |
| `MasterId` | `GetMasterId` | `SetMasterId` | `-` |
| `MilestoneList` | `GetMilestoneList` | `SetMilestoneList` | `-` |
| `MilestoneListFromJson` | `-` | `SetMilestoneListFromJson` | `-` |
| `MomentumValue` | `GetMomentumValue` | `SetMomentumValue` | `-` |
| `MotivationTypeOnlineMode` | `GetMotivationTypeOnlineMode` | `-` | `-` |
| `MotivationTypeTmpdb` | `GetMotivationTypeTmpdb` | `-` | `-` |
| `MotivationValue` | `GetMotivationValue` | `SetMotivationValue` | `-` |
| `MultiPositionAptitude` | `-` | `-` | `HasMultiPositionAptitude` |
| `Name` | `GetName` | `SetName` | `-` |
| `NameEditedForRc` | `-` | `-` | `IsNameEditedForRc` |
| `NamePrint` | `GetNamePrint` | `SetNamePrint` | `-` |
| `NameSimple` | `GetNameSimple` | `-` | `-` |
| `Nationality` | `GetNationality` | `SetNationality` | `-` |
| `NextSalary` | `GetNextSalary` | `SetNextSalary` | `-` |
| `OnlineCupSeasonRegulationInAll` | `-` | `-` | `IsOnlineCupSeasonRegulationInAll` |
| `OnlineCupSeasonRegulationInLatest` | `-` | `-` | `IsOnlineCupSeasonRegulationInLatest` |
| `OrderNo` | `GetOrderNo` | `SetOrderNo` | `-` |
| `OrderStatus` | `GetOrderStatus` | `SetOrderStatus` | `-` |
| `OriginalName` | `GetOriginalName` | `SetOriginalName` | `-` |
| `OriginalNameJp` | `GetOriginalNameJp` | `SetOriginalNameJp` | `-` |
| `OriginalTeamId` | `GetOriginalTeamId` | `-` | `-` |
| `OverAll` | `GetOverAll` | `-` | `-` |
| `OverallArrayFromString` | `GetOverallArrayFromString` | `-` | `-` |
| `OverallFromServer` | `GetOverallFromServer` | `SetOverallFromServer` | `-` |
| `OverAllTeamWork` | `GetOverAllTeamWork` | `-` | `-` |
| `ParamFromTmpdb` | `GetParamFromTmpdb` | `SetParamFromTmpdb` | `-` |
| `Phy` | `GetPhy` | `-` | `-` |
| `PhyRank` | `GetPhyRank` | `-` | `-` |
| `Playable` | `GetPlayable` | `SetPlayable` | `-` |
| `Player` | `-` | `SetPlayer` | `-` |
| `PlayerCategory` | `GetPlayerCategory` | `SetPlayerCategory` | `-` |
| `PlayerId` | `GetPlayerId` | `SetPlayerId` | `-` |
| `PlayerType` | `GetPlayerType` | `-` | `-` |
| `PlayStyle` | `GetPlayStyle` | `SetPlayStyle` | `-` |
| `PlayStyleForCom` | `-` | `-` | `HasPlayStyleForCom` |
| `PlayStyleHas` | `GetPlayStyleHas` | `SetPlayStyleHas` | `-` |
| `PlayStyleHasNum` | `GetPlayStyleHasNum` | `-` | `-` |
| `PlayStyleIndex` | `GetPlayStyleIndex` | `-` | `-` |
| `PointSeason` | `GetPointSeason` | `SetPointSeason` | `-` |
| `PointSum` | `GetPointSum` | `SetPointSum` | `-` |
| `PositionAptitude` | `GetPositionAptitude` | `SetPositionAptitude` | `HasPositionAptitude` |
| `QualityByIndex` | `-` | `SetQualityByIndex` | `-` |
| `QualityDataAll` | `GetQualityDataAll` | `SetQualityDataAll` | `ClearQualityDataAll` |
| `QualityDataByIndex` | `GetQualityDataByIndex` | `-` | `-` |
| `QualityDataByType` | `GetQualityDataByType` | `-` | `-` |
| `QualityDataCount` | `GetQualityDataCount` | `-` | `-` |
| `QualityDataCountSet` | `GetQualityDataCountSet` | `-` | `-` |
| `QualityDataCountUnlock` | `GetQualityDataCountUnlock` | `-` | `-` |
| `QualityPriorityForSort` | `GetQualityPriorityForSort` | `-` | `-` |
| `Rarity` | `GetRarity` | `SetRarity` | `-` |
| `RealLatestPlayer` | `-` | `-` | `IsRealLatestPlayer` |
| `RedSeason` | `GetRedSeason` | `SetRedSeason` | `-` |
| `RedSum` | `GetRedSum` | `SetRedSum` | `-` |
| `RedSuspension` | `GetRedSuspension` | `SetRedSuspension` | `-` |
| `RegisteredPosition` | `GetRegisteredPosition` | `SetRegisteredPosition` | `-` |
| `RegulationOut` | `-` | `-` | `IsRegulationOut` |
| `RentalPlayerInfo` | `GetRentalPlayerInfo` | `SetRentalPlayerInfo` | `-` |
| `RentalReturnInfo` | `GetRentalReturnInfo` | `SetRentalReturnInfo` | `-` |

## Outputs

- `analysis\stage4_player_schema\parameter_player_define_symbols.csv`
- `analysis\stage4_player_schema\player_schema_candidates.json`

## Next Analysis

- Disassemble tiny getters/setters to recover field offsets.
- Use large `PrepareDataFromJson*` methods to map JSON keys to these fields.
- Cross-check any local extracted records before enabling write/edit behavior.
