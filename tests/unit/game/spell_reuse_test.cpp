/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 */

#include <gtest/gtest.h>

#include "creatures/combat/spells.hpp"

TEST(SpellReuseTest, PreservesDeterministicConfigurationSurface) {
	InstantSpell spell;
	spell.setName("OAM Spell");
	spell.setSpellId(60123);
	spell.setWords("exori oam");
	spell.setLevel(45);
	spell.setMagicLevel(9);
	spell.setMana(120);
	spell.setManaPercent(15);
	spell.setSoulCost(3);
	spell.setCooldown(1500);
	spell.setSecondaryCooldown(500);
	spell.setGroupCooldown(2000);
	spell.setRange(7);
	spell.setNeedTarget(true);
	spell.setNeedWeapon(true);
	spell.setNeedLearn(true);
	spell.setBlockingSolid(true);
	spell.setBlockingCreature(true);
	spell.setAggressive(false);
	spell.setAllowOnSelf(false);
	spell.setLockedPZ(true);
	spell.setPremium(true);
	spell.setEnabled(false);
	spell.addVocMap(4, true);

	EXPECT_TRUE(spell.isInstant());
	EXPECT_EQ(spell.getName(), "OAM Spell");
	EXPECT_EQ(spell.getSpellId(), 60123);
	EXPECT_EQ(spell.getWords(), "exori oam");
	EXPECT_EQ(spell.getLevel(), 45);
	EXPECT_EQ(spell.getMagicLevel(), 9);
	EXPECT_EQ(spell.getMana(), 120);
	EXPECT_EQ(spell.getManaPercent(), 15);
	EXPECT_EQ(spell.getSoulCost(), 3);
	EXPECT_EQ(spell.getCooldown(), 1500);
	EXPECT_EQ(spell.getSecondaryCooldown(), 500);
	EXPECT_EQ(spell.getGroupCooldown(), 2000);
	EXPECT_EQ(spell.getRange(), 7);
	EXPECT_TRUE(spell.getNeedTarget());
	EXPECT_TRUE(spell.getNeedWeapon());
	EXPECT_TRUE(spell.getNeedLearn());
	EXPECT_TRUE(spell.getBlockingSolid());
	EXPECT_TRUE(spell.getBlockingCreature());
	EXPECT_FALSE(spell.getAggressive());
	EXPECT_FALSE(spell.getAllowOnSelf());
	EXPECT_TRUE(spell.getLockedPZ());
	EXPECT_TRUE(spell.isPremium());
	EXPECT_FALSE(spell.isEnabled());
	ASSERT_TRUE(spell.getVocMap().contains(4));
	EXPECT_TRUE(spell.getVocMap().at(4));
}

TEST(SpellReuseTest, PreservesInstantSpellRegistryLookup) {
	Spells spells;
	auto instant = std::make_shared<InstantSpell>();
	instant->setName("OAM Registry Spell");
	instant->setWords("exori oam registry");

	spells.setInstantSpell(instant->getWords(), instant);

	EXPECT_TRUE(spells.hasInstantSpell("exori oam registry"));
	EXPECT_EQ(spells.getInstantSpell("exori oam registry"), instant);
	EXPECT_EQ(spells.getInstantSpellByName("oam registry spell"), instant);
	EXPECT_EQ(spells.getSpellByName("OAM REGISTRY SPELL"), instant);
}
