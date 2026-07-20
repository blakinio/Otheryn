#include <gtest/gtest.h>

#include "io/ioprey.hpp"

TEST(Oam022PreyReuseTest, PreservesWireEnumValues) {
	EXPECT_EQ(static_cast<uint8_t>(PreyAction_ListReroll), 0);
	EXPECT_EQ(static_cast<uint8_t>(PreyAction_BonusReroll), 1);
	EXPECT_EQ(static_cast<uint8_t>(PreyAction_MonsterSelection), 2);
	EXPECT_EQ(static_cast<uint8_t>(PreyAction_ListAll_Cards), 3);
	EXPECT_EQ(static_cast<uint8_t>(PreyAction_ListAll_Selection), 4);
	EXPECT_EQ(static_cast<uint8_t>(PreyAction_Option), 5);

	EXPECT_EQ(static_cast<uint8_t>(PreyOption_None), 0);
	EXPECT_EQ(static_cast<uint8_t>(PreyOption_AutomaticReroll), 1);
	EXPECT_EQ(static_cast<uint8_t>(PreyOption_Locked), 2);

	EXPECT_EQ(static_cast<uint8_t>(PreyBonus_Damage), 0);
	EXPECT_EQ(static_cast<uint8_t>(PreyBonus_Defense), 1);
	EXPECT_EQ(static_cast<uint8_t>(PreyBonus_Experience), 2);
	EXPECT_EQ(static_cast<uint8_t>(PreyBonus_Loot), 3);
	EXPECT_EQ(static_cast<uint8_t>(PreyBonus_None), 4);
}

TEST(Oam022PreyReuseTest, PreservesPreySlotStateHelpers) {
	PreySlot slot;

	EXPECT_FALSE(slot.isOccupied());
	EXPECT_FALSE(slot.canSelect());

	slot.state = PreyDataState_Selection;
	EXPECT_TRUE(slot.canSelect());

	slot.selectedRaceId = 123;
	slot.bonusTimeLeft = 60;
	EXPECT_TRUE(slot.isOccupied());

	slot.bonus = PreyBonus_Loot;
	slot.bonusPercentage = 37;
	slot.bonusRarity = 9;
	slot.option = PreyOption_Locked;
	slot.eraseBonus();

	EXPECT_EQ(slot.state, PreyDataState_Selection);
	EXPECT_EQ(slot.option, PreyOption_None);
	EXPECT_EQ(slot.selectedRaceId, 0);
	EXPECT_EQ(slot.bonusTimeLeft, 0);
	EXPECT_EQ(slot.bonus, PreyBonus_None);
	EXPECT_EQ(slot.bonusPercentage, 5);
	EXPECT_EQ(slot.bonusRarity, 1);
}

TEST(Oam022PreyReuseTest, PreservesTaskHuntingSlotStateHelpers) {
	TaskHuntingSlot slot;

	EXPECT_FALSE(slot.isOccupied());
	EXPECT_FALSE(slot.canSelect());

	slot.state = PreyTaskDataState_ListSelection;
	EXPECT_TRUE(slot.canSelect());

	slot.selectedRaceId = 321;
	slot.upgrade = true;
	slot.currentKills = 55;
	slot.rarity = 4;
	EXPECT_TRUE(slot.isOccupied());

	slot.eraseTask();

	EXPECT_FALSE(slot.isOccupied());
	EXPECT_TRUE(slot.canSelect());
	EXPECT_FALSE(slot.upgrade);
	EXPECT_EQ(slot.currentKills, 0);
	EXPECT_EQ(slot.rarity, 1);
}

TEST(Oam022PreyReuseTest, RemovesAllMatchingMonsterEntries) {
	PreySlot preySlot;
	preySlot.raceIdList = { 10, 20, 10, 30 };
	preySlot.removeMonsterType(10);
	EXPECT_EQ(preySlot.raceIdList, (std::vector<uint16_t> { 20, 30 }));

	TaskHuntingSlot taskSlot;
	taskSlot.raceIdList = { 40, 50, 40, 60 };
	EXPECT_TRUE(taskSlot.isCreatureOnList(40));
	taskSlot.removeMonsterType(40);
	EXPECT_FALSE(taskSlot.isCreatureOnList(40));
	EXPECT_EQ(taskSlot.raceIdList, (std::vector<uint16_t> { 50, 60 }));
}
