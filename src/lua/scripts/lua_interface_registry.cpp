/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "lua/scripts/luascript.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <mutex>
	#include <unordered_set>
	#include <vector>
#endif

namespace {
	struct LuaScriptInterfaceRegistry {
		std::mutex mutex;
		std::unordered_set<LuaScriptInterface*> interfaces;
	};

	LuaScriptInterfaceRegistry &getLuaScriptInterfaceRegistry() {
		static LuaScriptInterfaceRegistry registry;
		return registry;
	}
}

LuaScriptInterface::RegistryEntry::RegistryEntry(LuaScriptInterface* initOwner) :
	owner(initOwner) {
	auto &registry = getLuaScriptInterfaceRegistry();
	std::scoped_lock lock(registry.mutex);
	registry.interfaces.insert(owner);
}

LuaScriptInterface::RegistryEntry::~RegistryEntry() {
	auto &registry = getLuaScriptInterfaceRegistry();
	std::scoped_lock lock(registry.mutex);
	registry.interfaces.erase(owner);
}

std::vector<LuaScriptInterface*> LuaScriptInterface::getRegisteredInterfaces() {
	auto &registry = getLuaScriptInterfaceRegistry();
	std::scoped_lock lock(registry.mutex);
	return std::vector<LuaScriptInterface*>(registry.interfaces.begin(), registry.interfaces.end());
}
