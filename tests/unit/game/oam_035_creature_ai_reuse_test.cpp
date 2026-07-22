#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>

namespace {
	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(OAM035_SOURCE_DIR) + "/" + relativePath);
		EXPECT_TRUE(input.is_open()) << relativePath;
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}
} // namespace

TEST(Oam035CreatureAiReuseTest, PreservesIndependentMonsterRuntimeLifecycleSurface) {
	const auto header = readSource("src/creatures/monsters/monster.hpp");
	ASSERT_FALSE(header.empty());

	EXPECT_NE(header.find("class Monster final : public Creature"), std::string::npos);
	EXPECT_NE(header.find("void onThink(uint32_t interval) override;"), std::string::npos);
	EXPECT_NE(header.find("bool setAttackedCreature(const std::shared_ptr<Creature> &creature) override;"), std::string::npos);
	EXPECT_NE(header.find("bool setFollowCreature(const std::shared_ptr<Creature> &creature) override;"), std::string::npos);
	EXPECT_NE(header.find("bool searchTarget(TargetSearchType_t searchType = TARGETSEARCH_DEFAULT);"), std::string::npos);
	EXPECT_NE(header.find("bool selectTarget(const std::shared_ptr<Creature> &creature);"), std::string::npos);
	EXPECT_NE(header.find("void updateTargetList();"), std::string::npos);
	EXPECT_NE(header.find("void onThinkTarget(uint32_t interval);"), std::string::npos);
	EXPECT_NE(header.find("void onThinkDefense(uint32_t interval);"), std::string::npos);
}

TEST(Oam035CreatureAiReuseTest, PreservesModularAsyncComputeWiring) {
	const auto header = readSource("src/creatures/monsters/monster.hpp");
	const auto source = readSource("src/creatures/monsters/monster.cpp");
	ASSERT_FALSE(header.empty());
	ASSERT_FALSE(source.empty());

	EXPECT_NE(header.find("bool requestFollowPathCompute(const std::shared_ptr<Creature> &followCreature, const FindPathParams &params, bool executeOnFollow);"), std::string::npos);
	EXPECT_NE(header.find("bool requestTargetSearchCompute(TargetSearchType_t searchType);"), std::string::npos);
	EXPECT_NE(header.find("void requestCombatIntention(uint32_t interval, const std::shared_ptr<Creature> &target);"), std::string::npos);
	EXPECT_NE(header.find("MonsterRelevanceState computeRelevance;"), std::string::npos);

	EXPECT_NE(source.find("#include \"creatures/monsters/monster_combat_intention.hpp\""), std::string::npos);
	EXPECT_NE(source.find("#include \"creatures/monsters/monster_pathfinding.hpp\""), std::string::npos);
	EXPECT_NE(source.find("#include \"creatures/monsters/monster_targeting.hpp\""), std::string::npos);
	EXPECT_NE(source.find("#include \"game/scheduling/monster_compute_service.hpp\""), std::string::npos);
}
