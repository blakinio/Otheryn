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

// A scheduler/dispatcher task scheduled against an instance can outlive that
// instance: the instance may close (or never leave Creating) before the task
// fires. InstanceManager has no visibility into scheduler-owned task handles
// and therefore cannot reach in and cancel them, so this wraps the callback
// side instead - it makes running the callback conditional on the instance
// still being Active at the moment the scheduler actually invokes it.
//
// This is deliberately a lazy liveness check rather than an active
// cancellation mechanism: it retains only an InstanceManager reference and an
// InstanceId, never a scheduler/dispatcher handle, so it stays valid to copy
// into a scheduled task without coupling this module to any particular
// scheduler implementation.
class InstanceScopedEvent {
public:
	InstanceScopedEvent(const InstanceManager &manager, InstanceId instanceId) noexcept :
		manager(manager), instanceId(instanceId) { }

	[[nodiscard]] bool isLive() const {
		return manager.getState(instanceId) == InstanceState::Active;
	}

	[[nodiscard]] InstanceId getInstanceId() const noexcept {
		return instanceId;
	}

	template <typename Callback>
	bool runIfLive(Callback callback) const {
		if (!isLive()) {
			return false;
		}
		callback();
		return true;
	}

private:
	const InstanceManager &manager;
	InstanceId instanceId;
};
