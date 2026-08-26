# Stage 6.2 JSON Key Mapping

## Scope

This read-only static artifact combines Stage 4 JSON literal references, key correlations, native accessor offset evidence, and the Stage 4 offset report. It does not trace code at runtime, instrument processes, or establish an on-disk player layout.

## Confidence Rules

- `HIGH`: a JSON key has a direct native field candidate and one or more concrete in-memory offsets.
- `MEDIUM`: grouped ability/skill/position evidence, or a direct field candidate without a recovered offset.
- `LOW`: a native offset field has no Stage 4 JSON-key correlation; these are separate candidates, not mappings.
- `UNKNOWN`: a JSON-like key has no field mapping and remains preserved for later analysis.

## Summary

- PrepareDataFromJson functions: 1
- JSON keys: 105
- JSON keys with candidates: 97
- Unknown JSON keys: 8
- Native-only field candidates: 60

## High-Confidence JSON Mappings

| json_key | field_candidate | offsets | setter_functions | accessor_functions |
| --- | --- | --- | --- | --- |
| age | Age | 0x18, 0x1c | SetAge | GetAge |
| camulative_yellow_cards | SumYellow | 0x18c | SetSumYellow | GetSumYellow |
| condition_status | Condition | 0xf4, 0xf7 | SetCondition | GetCondition |
| contract_period | ContractPeriod | 0x1e0 | SetContractPeriod | GetContractPeriod |
| contract_period_max | ContractPeriodMax | 0x1dc | SetContractPeriodMax | GetContractPeriodMax |
| contract_period_request | ContractPeriodRequest | 0x1e4 | SetContractPeriodRequest | GetContractPeriodRequest |
| contract_status | ContractStatus | 0x210 | SetContractStatus | GetContractStatus |
| deleted | DeleteType | 0x214 | SetDeleteType | GetDeleteType |
| injury | InjuryLength | 0xf4, 0xf8 | SetInjuryLength | GetInjuryLength |
| legend_status | LegendStatus | 0x1bc | SetLegendStatus | GetLegendStatus |
| licence | License | 0x204 | SetLicense | GetLicense |
| master_id | MasterId | 0x1d0 | SetMasterId | GetMasterId |
| motivation | MotivationValue | 0x20c | - | GetMotivationValue |
| name | Name | 0x38 | SetName | - |
| nationality | Nationality | 0xf4 | SetNationality | - |
| next_salary | NextSalary | 0x1ec | SetNextSalary | GetNextSalary |
| original_team_id | OriginalTeamId | 0xdc | - | GetOriginalTeamId |
| playstyle | PlayStyle | 0x18 | SetPlayStyle | GetPlayStyle |
| price | MarketValue | 0x1a0 | SetMarketValue | GetMarketValue |
| rarity | Rarity | 0x1c0 | SetRarity | GetRarity |
| record_assist_season | AssistSeason | 0x174 | SetAssistSeason | GetAssistSeason |
| record_assist_total | AssistSum | 0x178 | SetAssistSum | GetAssistSum |
| record_average_rating_season | PointSeason | 0x17c | SetPointSeason | GetPointSeason |
| record_average_rating_total | PointSum | 0x180 | SetPointSum | GetPointSum |
| record_goal_season | GoalSeason | 0x16c | SetGoalSeason | GetGoalSeason |
| record_goal_total | GoalSum | 0x170 | SetGoalSum | GetGoalSum |
| record_match_season | GameSeason | 0x164 | SetGameSeason | GetGameSeason |
| record_match_total | GameSum | 0x168 | SetGameSum | GetGameSum |
| record_red_card_season | RedSeason | 0x194 | SetRedSeason | GetRedSeason |
| record_red_card_total | RedSum | 0x198 | SetRedSum | GetRedSum |
| ... | 8 more rows omitted | | | |

## Unknown JSON Keys

`LeftRight`, `durability`, `e_09`, `energy`, `er_home_10`, `height`, `stability`, `weight`

## Native-Only Candidate Fields

| field_candidate | offsets | setter_functions | accessor_functions |
| --- | --- | --- | --- |
| AppearanceId | 0x1b0 | SetAppearanceId | GetAppearanceId |
| AssociationRentalPlayer | 0x334 | - | IsAssociationRentalPlayer |
| BonusWT | 0x310 | SetBonusWT | GetBonusWT |
| ComTeam | 0x348 | - | IsComTeam |
| CreateTime | 0x218 | SetCreateTime | GetCreateTime |
| CupEntryRuleStatus | 0x378, 0x380, 0x388 | SetCupEntryRuleStatus | GetCupEntryRuleStatus |
| CupEntryRuleStatusList | 0x380 | SetCupEntryRuleStatusList | GetCupEntryRuleStatusList |
| EnableElite | 0x337 | - | IsEnableElite |
| EnablePlayerInLegendTeam | 0x314 | SetEnablePlayerInLegendTeam | IsEnablePlayerInLegendTeam |
| FamePoint | 0x318 | SetFamePoint | GetFamePoint |
| FeaturedId | 0x358 | SetFeaturedId | GetFeaturedId |
| GrowthListBase | 0x230 | SetGrowthListBase | GetGrowthListBase |
| GrowthListTraining | 0x248 | SetGrowthListTraining | GetGrowthListTraining |
| GrowthStartAge | 0x228 | SetGrowthStartAge | GetGrowthStartAge |
| GrowthType | 0x31c | SetGrowthType | GetGrowthType |
| Id | 0x2c | SetId | GetId |
| IdExclusionSeazonDataType | 0x30 | - | GetIdExclusionSeazonDataType |
| IsAssociationRentalPlayer | 0x334 | SetIsAssociationRentalPlayer | - |
| IsComTeam | 0x348 | SetIsComTeam | - |
| IsEnableElite | 0x337 | SetIsEnableElite | - |
| IsRegulationOut | 0x340 | SetIsRegulationOut | - |
| LimitBreakNum | 0x344 | SetLimitBreakNum | GetLimitBreakNum |
| LoanDealStatus | 0x330 | SetLoanDealStatus | GetLoanDealStatus |
| MilestoneList | 0x360 | SetMilestoneList | GetMilestoneList |
| MomentumValue | 0x35c | SetMomentumValue | GetMomentumValue |
| MotivationTypeOnlineMode | 0x20c | - | GetMotivationTypeOnlineMode |
| MotivationTypeTmpdb | 0xf4 | - | GetMotivationTypeTmpdb |
| NameSimple | 0x1, 0x38, 0x88, 0xf7 | - | GetNameSimple |
| OrderNo | 0x224 | SetOrderNo | GetOrderNo |
| OrderStatus | 0x34c | SetOrderStatus | GetOrderStatus |
| ... | 30 more rows omitted | | | |

## Outputs

- `analysis/stage6/player_json_key_mapping.json`
- `analysis/stage6/mapping_confidence_report.csv`
- `analysis/stage6/new_fields_candidates.json`
- `analysis/stage6/prepare_data_from_json_address.txt`

## Boundary

Offsets in this report are candidate in-memory backing-data offsets recovered from accessors. They are not file offsets, a player binary table format, or authority to edit save data or game assets.
