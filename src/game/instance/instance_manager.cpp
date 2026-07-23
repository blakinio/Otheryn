/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/instance/instance_manager.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <algorithm>
	#include <stdexcept>
	#include <utility>
#endif

InstanceManager::InstanceManager(std::vector<InstanceMapRegion> regions) :
	regionPool(std::move(regions)) {
}

InstanceManager::CreateResult InstanceManager::createInstance(const InstanceDefinition &definition) {
	std::scoped_lock lock(mutex);

	const auto reservation = regionPool.reserve();
	if (!reservation.ok || !reservation.region) {
		return {
			.ok = false,
			.id = InstanceId::Invalid,
			.error = reservation.error.empty() ? "no available instance regions" : reservation.error,
		};
	}

	InstanceRecord record;
	record.id = static_cast<InstanceId>(nextInstanceId++);
	record.region = *reservation.region;
	record.state = InstanceState::Creating;
	record.definition = definition;
	if (definition.timeout.count() > 0) {
		record.expiresAt = std::chrono::steady_clock::now() + definition.timeout;
	}

	const auto id = record.id;
	try {
		instances.emplace(id, std::move(record));
	} catch (...) {
		regionPool.release(reservation.slot);
		throw;
	}
	return { .ok = true, .id = id, .error = {} };
}

bool InstanceManager::activate(InstanceId id) {
	std::scoped_lock lock(mutex);
	const auto it = instances.find(id);
	if (it == instances.end() || it->second.state != InstanceState::Creating) {
		return false;
	}
	it->second.state = InstanceState::Active;
	return true;
}

bool InstanceManager::close(InstanceId id) {
	InstanceCleanupCallback callback;
	InstanceMapRegion region;

	{
		std::scoped_lock lock(mutex);
		const auto it = instances.find(id);
		if (it == instances.end()) {
			return false;
		}
		if (it->second.state == InstanceState::Closing || it->second.state == InstanceState::Destroyed) {
			return true;
		}

		it->second.state = InstanceState::Closing;
		callback = it->second.cleanupCallback;
		region = it->second.region;
	}

	// Caller-supplied cleanup runs outside the manager lock. A thrown exception
	// intentionally leaves the record Closing and the region reserved, which
	// quarantines potentially dirty map space until the later recovery layer
	// handles it explicitly.
	if (callback) {
		callback(id, region);
	}

	{
		std::scoped_lock lock(mutex);
		const auto it = instances.find(id);
		if (it == instances.end()) {
			throw std::logic_error("instance disappeared during close");
		}
		if (!it->second.creatureIds.empty()) {
			throw std::logic_error("instance cleanup left registered creatures");
		}
		if (!regionPool.release(region.slot)) {
			throw std::logic_error("failed to release reserved instance region");
		}
		it->second.state = InstanceState::Destroyed;
	}

	return true;
}

void InstanceManager::setCleanupCallback(InstanceId id, InstanceCleanupCallback callback) {
	std::scoped_lock lock(mutex);
	const auto it = instances.find(id);
	if (it != instances.end()) {
		it->second.cleanupCallback = std::move(callback);
	}
}

bool InstanceManager::canAcceptCreatureLocked(const InstanceRecord &record) const noexcept {
	return record.state == InstanceState::Creating || record.state == InstanceState::Active;
}

bool InstanceManager::registerCreatureLocked(InstanceRecord &record, InstanceCreatureId creatureId) {
	const auto ownerIt = creatureOwners.find(creatureId);
	if (ownerIt != creatureOwners.end()) {
		return ownerIt->second == record.id && record.creatureIds.contains(creatureId);
	}

	const auto [insertedOwnerIt, insertedOwner] = creatureOwners.emplace(creatureId, record.id);
	if (!insertedOwner) {
		return false;
	}

	try {
		record.creatureIds.insert(creatureId);
	} catch (...) {
		creatureOwners.erase(insertedOwnerIt);
		throw;
	}
	return true;
}

bool InstanceManager::registerCreature(InstanceId id, InstanceCreatureId creatureId) {
	if (id == InstanceId::Invalid || creatureId == INVALID_INSTANCE_CREATURE_ID) {
		return false;
	}

	std::scoped_lock lock(mutex);
	const auto instanceIt = instances.find(id);
	if (instanceIt == instances.end() || !canAcceptCreatureLocked(instanceIt->second)) {
		return false;
	}

	return registerCreatureLocked(instanceIt->second, creatureId);
}

bool InstanceManager::unregisterCreature(InstanceId id, InstanceCreatureId creatureId) {
	if (id == InstanceId::Invalid || creatureId == INVALID_INSTANCE_CREATURE_ID) {
		return false;
	}

	std::scoped_lock lock(mutex);
	const auto instanceIt = instances.find(id);
	if (instanceIt == instances.end() || instanceIt->second.state == InstanceState::Destroyed) {
		return false;
	}

	const auto ownerIt = creatureOwners.find(creatureId);
	if (ownerIt == creatureOwners.end() || ownerIt->second != id) {
		return false;
	}

	instanceIt->second.creatureIds.erase(creatureId);
	creatureOwners.erase(ownerIt);
	return true;
}

bool InstanceManager::inheritCreatureOwnership(InstanceCreatureId masterId, InstanceCreatureId summonId) {
	if (masterId == INVALID_INSTANCE_CREATURE_ID || summonId == INVALID_INSTANCE_CREATURE_ID || masterId == summonId) {
		return false;
	}

	std::scoped_lock lock(mutex);
	const auto masterOwnerIt = creatureOwners.find(masterId);
	const auto summonOwnerIt = creatureOwners.find(summonId);

	if (masterOwnerIt == creatureOwners.end()) {
		// The normal world remains the default ownership domain. A summon that
		// already belongs to an instance may not cross that boundary by taking
		// an unowned master.
		return summonOwnerIt == creatureOwners.end();
	}

	const auto instanceIt = instances.find(masterOwnerIt->second);
	if (instanceIt == instances.end() || !canAcceptCreatureLocked(instanceIt->second)) {
		return false;
	}

	return registerCreatureLocked(instanceIt->second, summonId);
}

InstanceCreatureRelation InstanceManager::getCreatureRelation(InstanceCreatureId firstId, InstanceCreatureId secondId) const {
	if (firstId == INVALID_INSTANCE_CREATURE_ID || secondId == INVALID_INSTANCE_CREATURE_ID) {
		return InstanceCreatureRelation::Isolated;
	}

	std::scoped_lock lock(mutex);
	const auto firstOwnerIt = creatureOwners.find(firstId);
	const auto secondOwnerIt = creatureOwners.find(secondId);

	if (firstOwnerIt == creatureOwners.end() && secondOwnerIt == creatureOwners.end()) {
		return InstanceCreatureRelation::SameWorld;
	}
	if (firstOwnerIt == creatureOwners.end() || secondOwnerIt == creatureOwners.end() || firstOwnerIt->second != secondOwnerIt->second) {
		return InstanceCreatureRelation::Isolated;
	}

	const auto instanceIt = instances.find(firstOwnerIt->second);
	if (instanceIt == instances.end() || !canAcceptCreatureLocked(instanceIt->second)) {
		return InstanceCreatureRelation::Isolated;
	}
	return InstanceCreatureRelation::SameInstance;
}

bool InstanceManager::canCreaturesInteract(InstanceCreatureId firstId, InstanceCreatureId secondId) const {
	return getCreatureRelation(firstId, secondId) != InstanceCreatureRelation::Isolated;
}

std::optional<InstanceId> InstanceManager::getCreatureOwner(InstanceCreatureId creatureId) const {
	if (creatureId == INVALID_INSTANCE_CREATURE_ID) {
		return std::nullopt;
	}

	std::scoped_lock lock(mutex);
	const auto it = creatureOwners.find(creatureId);
	if (it == creatureOwners.end()) {
		return std::nullopt;
	}
	return it->second;
}

std::vector<InstanceCreatureId> InstanceManager::getRegisteredCreatureIds(InstanceId id) const {
	std::scoped_lock lock(mutex);
	const auto it = instances.find(id);
	if (it == instances.end()) {
		return {};
	}

	std::vector<InstanceCreatureId> ids(it->second.creatureIds.begin(), it->second.creatureIds.end());
	std::ranges::sort(ids);
	return ids;
}

std::size_t InstanceManager::registeredCreatureCount(InstanceId id) const {
	std::scoped_lock lock(mutex);
	const auto it = instances.find(id);
	if (it == instances.end()) {
		return 0;
	}
	return it->second.creatureIds.size();
}

std::optional<InstanceState> InstanceManager::getState(InstanceId id) const {
	std::scoped_lock lock(mutex);
	const auto it = instances.find(id);
	if (it == instances.end()) {
		return std::nullopt;
	}
	return it->second.state;
}

std::optional<InstanceSlotId> InstanceManager::getSlot(InstanceId id) const {
	const auto region = getRegion(id);
	if (!region) {
		return std::nullopt;
	}
	return region->slot;
}

std::optional<InstanceMapRegion> InstanceManager::getRegion(InstanceId id) const {
	std::scoped_lock lock(mutex);
	const auto it = instances.find(id);
	if (it == instances.end()) {
		return std::nullopt;
	}
	return it->second.region;
}

std::size_t InstanceManager::closeExpiredInstances(std::chrono::steady_clock::time_point now) {
	std::vector<InstanceId> expired;
	{
		std::scoped_lock lock(mutex);
		for (const auto &[id, record] : instances) {
			if (record.definition.timeout.count() <= 0) {
				continue;
			}
			if (record.state == InstanceState::Closing || record.state == InstanceState::Destroyed) {
				continue;
			}
			if (now >= record.expiresAt) {
				expired.push_back(id);
			}
		}
	}

	for (const auto id : expired) {
		close(id);
	}
	return expired.size();
}

std::size_t InstanceManager::activeInstanceCount() const {
	std::scoped_lock lock(mutex);
	std::size_t count = 0;
	for (const auto &[id, record] : instances) {
		if (record.state == InstanceState::Creating || record.state == InstanceState::Active) {
			++count;
		}
	}
	return count;
}

std::size_t InstanceManager::availableSlotCount() const {
	return regionPool.availableCount();
}

std::size_t InstanceManager::totalSlotCount() const {
	return regionPool.totalCount();
}
