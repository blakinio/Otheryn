/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/instance/instance_id.hpp"
#include "game/instance/instance_region_pool.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <chrono>
	#include <cstdint>
	#include <functional>
	#include <mutex>
	#include <optional>
	#include <string>
	#include <unordered_map>
	#include <unordered_set>
	#include <vector>
#endif

enum class InstanceState : uint8_t {
	Creating,
	Active,
	Closing,
	Destroyed,
};

struct InstanceDefinition {
	std::string name;
	// 0 means no automatic timeout; the instance only closes when close()
	// is called explicitly.
	std::chrono::seconds timeout { 0 };
};

using InstanceCleanupCallback = std::function<void(InstanceId, const InstanceMapRegion &)>;

// Creature ids are the stable runtime ids assigned by Creature::setID(). Zero
// is never accepted because it means the creature has not entered the runtime
// identity registry yet.
using InstanceCreatureId = uint32_t;
constexpr InstanceCreatureId INVALID_INSTANCE_CREATURE_ID = 0;

enum class InstanceCreatureRelation : uint8_t {
	// Both runtime ids are currently outside every instance.
	SameWorld,
	// Both runtime ids are owned by the same active instance boundary.
	SameInstance,
	// Invalid ids, one owned/one unowned, or different instance owners.
	Isolated,
};

// Owns the configured map-region pool and the lifecycle of instances that
// reserve those regions. Deliberately a plain, constructor-instantiated class
// rather than a g_x() singleton.
class InstanceManager {
public:
	// Takes ownership of the complete configured region set. Construction
	// validates the regions through InstanceRegionPool before any instance can
	// be created.
	explicit InstanceManager(std::vector<InstanceMapRegion> regions);

	// non-copyable: owns unique region reservations and per-instance state.
	InstanceManager(const InstanceManager &) = delete;
	InstanceManager &operator=(const InstanceManager &) = delete;

	struct CreateResult {
		bool ok = false;
		InstanceId id = InstanceId::Invalid;
		std::string error;
	};

	// Reserves a free configured region and creates the instance in the
	// Creating state. Fails if every region is already reserved.
	[[nodiscard]] CreateResult createInstance(const InstanceDefinition &definition);

	// Creating -> Active. Returns false without changing anything if the
	// instance is unknown or not currently Creating.
	bool activate(InstanceId id);

	// Idempotent: {Creating, Active} -> Closing -> Destroyed. The cleanup
	// callback runs outside the manager lock exactly once and receives the
	// concrete reserved region. The region is returned to the pool only after
	// cleanup completes and every registered creature identity has been
	// removed. If cleanup throws or leaves creature ids behind, the instance
	// remains Closing and the region stays quarantined.
	bool close(InstanceId id);

	// Replaces the cleanup callback for an instance. No-op if the instance is
	// unknown. Safe to call before or after activate().
	void setCleanupCallback(InstanceId id, InstanceCleanupCallback callback);

	// Registers a stable creature runtime id with one Creating or Active
	// instance. Registration is idempotent for the same owner and rejects ids
	// already owned by another instance. No Creature pointer is retained.
	bool registerCreature(InstanceId id, InstanceCreatureId creatureId);

	// Removes a creature identity from its owner. This remains available while
	// the instance is Closing so the cleanup callback can drain the registry.
	bool unregisterCreature(InstanceId id, InstanceCreatureId creatureId);

	// Applies summon ownership atomically from stable runtime identities.
	// An unowned master accepts only an unowned summon and remains a no-op.
	// An owned master registers an unowned summon to the same instance.
	// Cross-instance ownership, invalid ids and Closing/Destroyed owners fail.
	bool inheritCreatureOwnership(InstanceCreatureId masterId, InstanceCreatureId summonId);

	// Central fail-closed ownership relation used by later visibility,
	// targeting and combat wiring. No map or Creature pointer access occurs.
	[[nodiscard]] InstanceCreatureRelation getCreatureRelation(InstanceCreatureId firstId, InstanceCreatureId secondId) const;
	[[nodiscard]] bool canCreaturesInteract(InstanceCreatureId firstId, InstanceCreatureId secondId) const;

	[[nodiscard]] std::optional<InstanceId> getCreatureOwner(InstanceCreatureId creatureId) const;
	[[nodiscard]] std::vector<InstanceCreatureId> getRegisteredCreatureIds(InstanceId id) const;
	[[nodiscard]] std::size_t registeredCreatureCount(InstanceId id) const;

	[[nodiscard]] std::optional<InstanceState> getState(InstanceId id) const;
	[[nodiscard]] std::optional<InstanceSlotId> getSlot(InstanceId id) const;
	[[nodiscard]] std::optional<InstanceMapRegion> getRegion(InstanceId id) const;

	// Closes every instance whose definition timeout has elapsed as of `now`.
	// Instances with timeout == 0 are never touched. Goes through the same
	// idempotent close() path.
	std::size_t closeExpiredInstances(std::chrono::steady_clock::time_point now = std::chrono::steady_clock::now());

	[[nodiscard]] std::size_t activeInstanceCount() const;
	[[nodiscard]] std::size_t availableSlotCount() const;
	[[nodiscard]] std::size_t totalSlotCount() const;

private:
	struct InstanceRecord {
		InstanceId id = InstanceId::Invalid;
		InstanceMapRegion region;
		InstanceState state = InstanceState::Creating;
		InstanceDefinition definition;
		std::chrono::steady_clock::time_point expiresAt {};
		InstanceCleanupCallback cleanupCallback;
		std::unordered_set<InstanceCreatureId> creatureIds;
	};

	[[nodiscard]] bool canAcceptCreatureLocked(const InstanceRecord &record) const noexcept;
	bool registerCreatureLocked(InstanceRecord &record, InstanceCreatureId creatureId);

	mutable std::mutex mutex;
	InstanceRegionPool regionPool;
	std::unordered_map<InstanceId, InstanceRecord> instances;
	std::unordered_map<InstanceCreatureId, InstanceId> creatureOwners;
	uint32_t nextInstanceId = 1;
};
