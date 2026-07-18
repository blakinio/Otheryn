/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

// Player.hpp already includes the achievement
#include "creatures/players/player.hpp"

#include "game/game.hpp"
#include "kv/kv.hpp"

#include <limits>

PlayerAchievement::PlayerAchievement(Player &player) :
	m_player(player) { }

bool PlayerAchievement::add(uint16_t id, bool message /* = true*/, uint32_t timestamp /* = 0*/) {
	if (isUnlocked(id)) {
		return false;
	}

	const auto &achievement = g_game().getAchievementById(id);
	if (achievement.id == 0) {
		return false;
	}

	if (message) {
		m_player.sendTextMessage(MESSAGE_EVENT_ADVANCE, fmt::format("Congratulations! You earned the achievement {}.", achievement.name));
	}

	addPoints(achievement.points);
	int toSaveTimeStamp = timestamp != 0 ? timestamp : (OTSYS_TIME() / 1000);
	getUnlockedKV()->set(achievement.name, toSaveTimeStamp);
	m_achievementsUnlocked.emplace_back(achievement.id, toSaveTimeStamp);
	m_achievementsUnlocked.shrink_to_fit();
	return true;
}

bool PlayerAchievement::remove(uint16_t id) {
	if (!isUnlocked(id)) {
		return false;
	}

	const auto achievement = g_game().getAchievementById(id);
	if (achievement.id == 0) {
		return false;
	}

	if (auto it = std::ranges::find_if(m_achievementsUnlocked, [id](auto achievement_it) {
			return achievement_it.first == id;
		});
	    it != m_achievementsUnlocked.end()) {
		getUnlockedKV()->remove(achievement.name);
		m_achievementsUnlocked.erase(it);
		removePoints(achievement.points);
		m_achievementsUnlocked.shrink_to_fit();
		return true;
	}

	return false;
}

bool PlayerAchievement::isUnlocked(uint16_t id) const {
	if (id == 0) {
		return false;
	}

	if (auto it = std::ranges::find_if(m_achievementsUnlocked, [id](auto achievement_it) {
			return achievement_it.first == id;
		});
	    it != m_achievementsUnlocked.end()) {
		return true;
	}

	return false;
}

uint16_t PlayerAchievement::getPoints() const {
	const auto kvScoped = m_player.kv()->scoped("achievements")->get("points");
	return kvScoped ? static_cast<uint16_t>(kvScoped->getNumber()) : 0;
}

std::optional<uint16_t> PlayerAchievement::calculateUnlockedPoints() const {
	uint32_t totalPoints = 0;
	for (const auto &unlockedAchievement : m_achievementsUnlocked) {
		const auto achievement = g_game().getAchievementById(unlockedAchievement.first);
		if (achievement.id == 0) {
			g_logger().error("[{}] - Achievement ID {} not found; point reconciliation aborted.", __FUNCTION__, unlockedAchievement.first);
			return std::nullopt;
		}

		totalPoints += achievement.points;
		if (totalPoints > std::numeric_limits<uint16_t>::max()) {
			g_logger().error("[{}] - Achievement point total {} exceeds uint16_t; reconciliation aborted.", __FUNCTION__, totalPoints);
			return std::nullopt;
		}
	}

	return static_cast<uint16_t>(totalPoints);
}

bool PlayerAchievement::reconcilePoints() const {
	const auto authoritativePoints = calculateUnlockedPoints();
	if (!authoritativePoints.has_value()) {
		return false;
	}

	const auto storedPoints = getPoints();
	if (storedPoints != authoritativePoints.value()) {
		m_player.kv()->scoped("achievements")->set("points", authoritativePoints.value());
	}

	return true;
}

void PlayerAchievement::addPoints(uint16_t toAddPoints) const {
	const auto oldPoints = getPoints();
	m_player.kv()->scoped("achievements")->set("points", oldPoints + toAddPoints);
}

void PlayerAchievement::removePoints(uint16_t points) const {
	const auto oldPoints = getPoints();
	m_player.kv()->scoped("achievements")->set("points", oldPoints - std::min<uint16_t>(oldPoints, points));
}

std::vector<std::pair<uint16_t, uint32_t>> PlayerAchievement::getUnlockedAchievements() const {
	return m_achievementsUnlocked;
}

void PlayerAchievement::loadUnlockedAchievements() {
	m_achievementsUnlocked.clear();
	bool hasUnresolvedAchievement = false;
	const auto &unlockedAchievements = getUnlockedKV()->keys();
	g_logger().debug("[{}] - Loading unlocked achievements: {}", __FUNCTION__, unlockedAchievements.size());
	for (const auto &achievementName : unlockedAchievements) {
		const Achievement &achievement = g_game().getAchievementByName(achievementName);
		if (achievement.id == 0) {
			g_logger().error("[{}] - Achievement {} not found; preserving stored point aggregate.", __FUNCTION__, achievementName);
			hasUnresolvedAchievement = true;
			continue;
		}

		g_logger().debug("[{}] - Achievement {} found for player {}.", __FUNCTION__, achievementName, m_player.getName());
		m_achievementsUnlocked.emplace_back(achievement.id, getUnlockedKV()->get(achievementName)->getNumber());
	}

	if (hasUnresolvedAchievement) {
		return;
	}

	if (!reconcilePoints()) {
		g_logger().error("[{}] - Failed to reconcile achievement points for player {}.", __FUNCTION__, m_player.getName());
	}
}

void PlayerAchievement::sendUnlockedSecretAchievements() const {
	std::vector<std::pair<Achievement, uint32_t>> achievementsUnlocked;
	uint16_t unlockedSecret = 0;
	for (const auto &[achievId, achievCreatedTime] : getUnlockedAchievements()) {
		const auto &achievement = g_game().getAchievementById(achievId);
		if (achievement.id == 0) {
			continue;
		}

		if (achievement.secret) {
			unlockedSecret++;
		}

		achievementsUnlocked.emplace_back(achievement, achievCreatedTime);
	}

	m_player.sendCyclopediaCharacterAchievements(unlockedSecret, achievementsUnlocked);
}

const std::shared_ptr<KV> &PlayerAchievement::getUnlockedKV() {
	if (m_unlockedKV == nullptr) {
		m_unlockedKV = m_player.kv()->scoped("achievements")->scoped("unlocked");
	}

	return m_unlockedKV;
}
