#include "config/configmanager.hpp"
#include "modules/module_registry.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <algorithm>
	#include <array>
	#include <chrono>
	#include <filesystem>
	#include <fstream>
	#include <functional>
	#include <string>
	#include <thread>
#endif

#include <gtest/gtest.h>

namespace {
	class TemporaryModuleProfileConfig final {
	public:
		TemporaryModuleProfileConfig() {
			const auto timestamp = std::chrono::steady_clock::now().time_since_epoch().count();
			const auto threadId = std::hash<std::thread::id> {}(std::this_thread::get_id());
			path = std::filesystem::temp_directory_path() / ("mge_003_module_profile_" + std::to_string(timestamp) + "_" + std::to_string(threadId) + ".lua");
			std::ofstream output(path, std::ios::trunc);
			output << "-- current profile defaults\n";
		}

		~TemporaryModuleProfileConfig() {
			std::error_code error;
			std::filesystem::remove(path, error);
		}

		[[nodiscard]] const std::filesystem::path &getPath() const {
			return path;
		}

	private:
		std::filesystem::path path;
	};

	[[nodiscard]] const ModuleValidationIssue* findIssue(const ModuleValidationResult &result, ModuleValidationCode code) {
		const auto found = std::find_if(result.issues.begin(), result.issues.end(), [code](const ModuleValidationIssue &issue) {
			return issue.code == code;
		});
		return found == result.issues.end() ? nullptr : &*found;
	}

	[[nodiscard]] size_t startupIndex(const ModuleValidationResult &result, ModuleId id) {
		const auto found = std::find(result.startupOrder.begin(), result.startupOrder.end(), id);
		return static_cast<size_t>(std::distance(result.startupOrder.begin(), found));
	}
}

TEST(Mge003ModuleRegistryTest, CurrentCatalogAndSelectionValidateAgainstCurrentProtocol) {
	const auto &registry = ModuleRegistry::current();
	const auto selection = ModuleRegistry::currentSelection();
	const auto result = registry.validate(selection, ProtocolProfileRegistry::getCurrentProfile());

	ASSERT_TRUE(result.ok()) << formatModuleValidationIssues(result);
	EXPECT_EQ(result.startupOrder.size(), selection.size());
	for (const auto id : selection) {
		const auto* descriptor = registry.find(id);
		ASSERT_NE(descriptor, nullptr);
		for (const auto dependency : descriptor->dependencies) {
			EXPECT_LT(startupIndex(result, dependency), startupIndex(result, id));
		}
	}
}

TEST(Mge003ModuleRegistryTest, DuplicateDescriptorIsRejectedDeterministically) {
	const std::array<ModuleDescriptor, 2> descriptors { {
		{ .id = ModuleId::EngineRuntime },
		{ .id = ModuleId::EngineRuntime },
	} };
	const std::array selection { ModuleId::EngineRuntime };

	const auto result = ModuleRegistry(descriptors).validate(selection, 0);
	ASSERT_FALSE(result.ok());
	const auto* issue = findIssue(result, ModuleValidationCode::DuplicateDescriptor);
	ASSERT_NE(issue, nullptr);
	EXPECT_EQ(issue->message, "module descriptor 'engine-runtime' is registered more than once");
}

TEST(Mge003ModuleRegistryTest, UnknownDependencyIsRejectedDeterministically) {
	const std::array dependencies { ModuleId::Players };
	const std::array<ModuleDescriptor, 1> descriptors { {
		{ .id = ModuleId::World, .dependencies = dependencies },
	} };
	const std::array selection { ModuleId::World };

	const auto result = ModuleRegistry(descriptors).validate(selection, 0);
	ASSERT_FALSE(result.ok());
	const auto* issue = findIssue(result, ModuleValidationCode::UnknownDependency);
	ASSERT_NE(issue, nullptr);
	EXPECT_EQ(issue->message, "module 'world' depends on unregistered module 'players'");
}

TEST(Mge003ModuleRegistryTest, DependencyCycleIsRejectedDeterministically) {
	const std::array engineDependencies { ModuleId::Scheduler };
	const std::array schedulerDependencies { ModuleId::EngineRuntime };
	const std::array<ModuleDescriptor, 2> descriptors { {
		{ .id = ModuleId::EngineRuntime, .dependencies = engineDependencies },
		{ .id = ModuleId::Scheduler, .dependencies = schedulerDependencies },
	} };
	const std::array selection { ModuleId::EngineRuntime, ModuleId::Scheduler };

	const auto result = ModuleRegistry(descriptors).validate(selection, 0);
	ASSERT_FALSE(result.ok());
	const auto* issue = findIssue(result, ModuleValidationCode::DependencyCycle);
	ASSERT_NE(issue, nullptr);
	EXPECT_EQ(issue->message, "module 'scheduler' forms a dependency cycle through 'engine-runtime'");
}

TEST(Mge003ModuleRegistryTest, UnknownAndDuplicateSelectionsAreRejected) {
	const std::array<ModuleDescriptor, 1> descriptors { {
		{ .id = ModuleId::EngineRuntime },
	} };
	const std::array selection { ModuleId::EngineRuntime, ModuleId::EngineRuntime, ModuleId::Scheduler };

	const auto result = ModuleRegistry(descriptors).validate(selection, 0);
	EXPECT_NE(findIssue(result, ModuleValidationCode::DuplicateSelection), nullptr);
	EXPECT_NE(findIssue(result, ModuleValidationCode::UnknownSelection), nullptr);
}

TEST(Mge003ModuleRegistryTest, MissingRequiredModuleIsRejected) {
	const std::array<ModuleDescriptor, 1> descriptors { {
		{ .id = ModuleId::EngineRuntime, .requirement = ModuleRequirement::CoreRequired },
	} };
	const std::array<ModuleId, 0> selection {};

	const auto result = ModuleRegistry(descriptors).validate(selection, 0);
	const auto* issue = findIssue(result, ModuleValidationCode::MissingRequiredModule);
	ASSERT_NE(issue, nullptr);
	EXPECT_EQ(issue->message, "required module 'engine-runtime' is not selected");
}

TEST(Mge003ModuleRegistryTest, MissingSelectedDependencyIsRejected) {
	const std::array dependencies { ModuleId::EngineRuntime };
	const std::array<ModuleDescriptor, 2> descriptors { {
		{ .id = ModuleId::EngineRuntime },
		{ .id = ModuleId::Scheduler, .dependencies = dependencies },
	} };
	const std::array selection { ModuleId::Scheduler };

	const auto result = ModuleRegistry(descriptors).validate(selection, 0);
	const auto* issue = findIssue(result, ModuleValidationCode::MissingDependency);
	ASSERT_NE(issue, nullptr);
	EXPECT_EQ(issue->message, "module 'scheduler' requires selected dependency 'engine-runtime'");
}

TEST(Mge003ModuleRegistryTest, MissingProtocolCapabilityIsRejected) {
	const std::array<ModuleDescriptor, 1> descriptors { {
		{
			.id = ModuleId::Market,
			.requiredCapabilities = moduleCapabilityMask(ModuleCapability::MarketProtocol),
		},
	} };
	const std::array selection { ModuleId::Market };

	const auto result = ModuleRegistry(descriptors).validate(selection, 0);
	const auto* issue = findIssue(result, ModuleValidationCode::MissingCapability);
	ASSERT_NE(issue, nullptr);
	EXPECT_EQ(issue->capability, ModuleCapability::MarketProtocol);
	EXPECT_EQ(issue->message, "module 'market' requires protocol capability 'market-protocol'");
}

TEST(Mge003ModuleRegistryTest, StartupOrderIsDependencyFirstAndStable) {
	const std::array schedulerDependencies { ModuleId::EngineRuntime };
	const std::array networkDependencies { ModuleId::Scheduler };
	const std::array<ModuleDescriptor, 3> descriptors { {
		{ .id = ModuleId::NetworkTransport, .dependencies = networkDependencies },
		{ .id = ModuleId::Scheduler, .dependencies = schedulerDependencies },
		{ .id = ModuleId::EngineRuntime },
	} };
	const std::array selection { ModuleId::NetworkTransport, ModuleId::Scheduler, ModuleId::EngineRuntime };
	const ModuleRegistry registry(descriptors);

	const auto first = registry.validate(selection, 0);
	const auto second = registry.validate(selection, 0);
	ASSERT_TRUE(first.ok());
	EXPECT_EQ(first.startupOrder, second.startupOrder);
	EXPECT_EQ(first.startupOrder, (std::vector<ModuleId> { ModuleId::EngineRuntime, ModuleId::Scheduler, ModuleId::NetworkTransport }));
}

TEST(Mge003ModuleRegistryTest, ConfigManagerPublishesValidatedImmutableCurrentSelection) {
	TemporaryModuleProfileConfig configFile;
	ConfigManager manager;
	manager.setConfigFileLua(configFile.getPath().string());
	ASSERT_TRUE(manager.load());

	const auto profile = manager.getGameProfile();
	ASSERT_NE(profile, nullptr);
	const auto currentSelection = ModuleRegistry::currentSelection();
	EXPECT_EQ(profile->enabledModules, (std::vector<ModuleId>(currentSelection.begin(), currentSelection.end())));
	const auto result = ModuleRegistry::current().validate(profile->enabledModules, ProtocolProfileRegistry::getCurrentProfile());
	EXPECT_TRUE(result.ok()) << formatModuleValidationIssues(result);
}

TEST(Mge003ModuleRegistryTest, CurrentSelectionRejectsProtocolWithoutWheelCapability) {
	const auto* legacyProfile = ProtocolProfileRegistry::getProfile(ProtocolProfileId::Tibia1100);
	ASSERT_NE(legacyProfile, nullptr);

	const auto result = ModuleRegistry::current().validate(ModuleRegistry::currentSelection(), *legacyProfile);
	const auto* issue = findIssue(result, ModuleValidationCode::MissingCapability);
	ASSERT_NE(issue, nullptr);
	EXPECT_EQ(issue->module, ModuleId::Wheel);
	EXPECT_EQ(issue->capability, ModuleCapability::WheelProtocol);
}
