/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/instance/instance_manager.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <stdexcept>
#endif

// Synchronous adapter between runtime objects exposing getID() and the
// pointer-free ownership registry. It keeps only the manager reference and
// never retains a Creature pointer/reference after a call returns.
class InstanceCreatureBinder {
public:
	explicit InstanceCreatureBinder(InstanceManager &manager) noexcept :
		manager(manager) {
	}

	InstanceCreatureBinder(const InstanceCreatureBinder &) = delete;
	InstanceCreatureBinder &operator=(const InstanceCreatureBinder &) = delete;

	bool bind(InstanceId instanceId, InstanceCreatureId creatureId) {
		return manager.registerCreature(instanceId, creatureId);
	}

	template <typename RuntimeCreature>
		requires requires(const RuntimeCreature &value) {
			value.getID();
		}
	bool bind(InstanceId instanceId, const RuntimeCreature &creature) {
		return bind(instanceId, static_cast<InstanceCreatureId>(creature.getID()));
	}

	// Uses the manager's authoritative reverse index rather than accepting a
	// caller-provided owner, so an object cannot accidentally unregister
	// another instance's creature.
	bool unbind(InstanceCreatureId creatureId) {
		const auto owner = manager.getCreatureOwner(creatureId);
		return owner && manager.unregisterCreature(*owner, creatureId);
	}

	template <typename RuntimeCreature>
		requires requires(const RuntimeCreature &value) {
			value.getID();
		}
	bool unbind(const RuntimeCreature &creature) {
		return unbind(static_cast<InstanceCreatureId>(creature.getID()));
	}

	bool inherit(InstanceCreatureId masterId, InstanceCreatureId summonId) {
		return manager.inheritCreatureOwnership(masterId, summonId);
	}

	template <typename MasterCreature, typename SummonCreature>
		requires requires(const MasterCreature &masterValue, const SummonCreature &summonValue) {
			masterValue.getID();
			summonValue.getID();
		}
	bool inherit(const MasterCreature &master, const SummonCreature &summon) {
		return inherit(
			static_cast<InstanceCreatureId>(master.getID()),
			static_cast<InstanceCreatureId>(summon.getID())
		);
	}

	// Applies ownership inheritance and a synchronous master-link operation as
	// one compensating transaction. A newly inherited owner is removed when the
	// operation returns false or throws. Ownership that existed before this call
	// is never removed by rollback.
	template <typename ApplyMasterLink>
	bool inheritAndApply(InstanceCreatureId masterId, InstanceCreatureId summonId, ApplyMasterLink applyMasterLink) {
		const auto previousOwner = ownerOf(summonId);
		if (!inherit(masterId, summonId)) {
			return false;
		}

		const auto inheritedOwner = ownerOf(summonId);
		const bool ownershipAddedByThisCall = !previousOwner.has_value() && inheritedOwner.has_value();

		try {
			if (static_cast<bool>(applyMasterLink())) {
				return true;
			}
		} catch (...) {
			if (ownershipAddedByThisCall) {
				rollbackInheritedOwnership(summonId, *inheritedOwner);
			}
			throw;
		}

		if (ownershipAddedByThisCall) {
			rollbackInheritedOwnership(summonId, *inheritedOwner);
		}
		return false;
	}

	template <typename MasterCreature, typename SummonCreature, typename ApplyMasterLink>
		requires requires(const MasterCreature &masterValue, const SummonCreature &summonValue) {
			masterValue.getID();
			summonValue.getID();
		}
	bool inheritAndApply(const MasterCreature &master, const SummonCreature &summon, ApplyMasterLink applyMasterLink) {
		return inheritAndApply(
			static_cast<InstanceCreatureId>(master.getID()),
			static_cast<InstanceCreatureId>(summon.getID()),
			applyMasterLink
		);
	}

	[[nodiscard]] InstanceCreatureRelation relation(InstanceCreatureId firstId, InstanceCreatureId secondId) const {
		return manager.getCreatureRelation(firstId, secondId);
	}

	template <typename FirstCreature, typename SecondCreature>
		requires requires(const FirstCreature &firstValue, const SecondCreature &secondValue) {
			firstValue.getID();
			secondValue.getID();
		}
	[[nodiscard]] InstanceCreatureRelation relation(const FirstCreature &first, const SecondCreature &second) const {
		return relation(
			static_cast<InstanceCreatureId>(first.getID()),
			static_cast<InstanceCreatureId>(second.getID())
		);
	}

	[[nodiscard]] bool canInteract(InstanceCreatureId firstId, InstanceCreatureId secondId) const {
		return manager.canCreaturesInteract(firstId, secondId);
	}

	template <typename FirstCreature, typename SecondCreature>
		requires requires(const FirstCreature &firstValue, const SecondCreature &secondValue) {
			firstValue.getID();
			secondValue.getID();
		}
	[[nodiscard]] bool canInteract(const FirstCreature &first, const SecondCreature &second) const {
		return canInteract(
			static_cast<InstanceCreatureId>(first.getID()),
			static_cast<InstanceCreatureId>(second.getID())
		);
	}

	[[nodiscard]] std::optional<InstanceId> ownerOf(InstanceCreatureId creatureId) const {
		return manager.getCreatureOwner(creatureId);
	}

	template <typename RuntimeCreature>
		requires requires(const RuntimeCreature &value) {
			value.getID();
		}
	[[nodiscard]] std::optional<InstanceId> ownerOf(const RuntimeCreature &creature) const {
		return ownerOf(static_cast<InstanceCreatureId>(creature.getID()));
	}

private:
	void rollbackInheritedOwnership(InstanceCreatureId creatureId, InstanceId expectedOwner) {
		const auto currentOwner = ownerOf(creatureId);
		if (!currentOwner) {
			return;
		}
		if (*currentOwner != expectedOwner) {
			throw std::logic_error("creature ownership changed during master-link transaction");
		}
		if (!manager.unregisterCreature(expectedOwner, creatureId)) {
			throw std::logic_error("failed to rollback inherited creature ownership");
		}
	}

	InstanceManager &manager;
};
