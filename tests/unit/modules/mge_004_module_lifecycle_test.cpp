#include "modules/module_lifecycle.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <array>
	#include <stdexcept>
	#include <string>
	#include <vector>
#endif

#include <gtest/gtest.h>

namespace {
	struct LifecycleFixture {
		std::array<ModuleId, 1> schedulerDependencies { ModuleId::EngineRuntime };
		std::array<ModuleId, 1> networkDependencies { ModuleId::Scheduler };
		std::array<ModuleDescriptor, 3> descriptors { {
			{ .id = ModuleId::EngineRuntime, .requirement = ModuleRequirement::CoreRequired },
			{ .id = ModuleId::Scheduler, .requirement = ModuleRequirement::CoreRequired, .dependencies = schedulerDependencies },
			{ .id = ModuleId::NetworkTransport, .requirement = ModuleRequirement::CoreRequired, .dependencies = networkDependencies },
		} };
		std::array<ModuleId, 3> selection { ModuleId::NetworkTransport, ModuleId::Scheduler, ModuleId::EngineRuntime };
		ModuleRegistry registry { descriptors };
	};

	ModuleLifecycleParticipant participant(ModuleId id, std::string name, std::vector<std::string> &events, bool failStart = false, bool failStop = false) {
		return ModuleLifecycleParticipant {
			.id = id,
			.name = std::move(name),
			.start = [&events, id, failStart] {
				events.emplace_back("start:" + std::string(moduleIdName(id)));
				if (failStart) {
					throw std::runtime_error("start failure");
				} },
			.stop = [&events, id, failStop] {
				events.emplace_back("stop:" + std::string(moduleIdName(id)));
				if (failStop) {
					throw std::runtime_error("stop failure");
				} },
		};
	}
}

TEST(Mge004ModuleLifecycleTest, StartsInDependencyOrderAndStopsInReverseOrder) {
	LifecycleFixture fixture;
	ModuleCompositionRoot root(fixture.selection, 0, fixture.registry);
	std::vector<std::string> events;
	std::string error;

	ASSERT_TRUE(root.registerParticipant(participant(ModuleId::NetworkTransport, "network", events), error));
	ASSERT_TRUE(root.registerParticipant(participant(ModuleId::EngineRuntime, "engine", events), error));
	ASSERT_TRUE(root.registerParticipant(participant(ModuleId::Scheduler, "scheduler", events), error));
	ASSERT_TRUE(root.start(error)) << error;
	EXPECT_TRUE(root.isReady());
	EXPECT_EQ(events, (std::vector<std::string> {
						  "start:engine-runtime",
						  "start:scheduler",
						  "start:network-transport",
					  }));

	root.stop();
	EXPECT_EQ(root.getState(), ModuleLifecycleState::Stopped);
	EXPECT_EQ(events, (std::vector<std::string> {
						  "start:engine-runtime",
						  "start:scheduler",
						  "start:network-transport",
						  "stop:network-transport",
						  "stop:scheduler",
						  "stop:engine-runtime",
					  }));
}

TEST(Mge004ModuleLifecycleTest, StartupFailureRollsBackOnlySuccessfullyStartedParticipants) {
	LifecycleFixture fixture;
	ModuleCompositionRoot root(fixture.selection, 0, fixture.registry);
	std::vector<std::string> events;
	std::string error;

	ASSERT_TRUE(root.registerParticipant(participant(ModuleId::EngineRuntime, "engine", events), error));
	ASSERT_TRUE(root.registerParticipant(participant(ModuleId::Scheduler, "scheduler", events, true), error));
	ASSERT_TRUE(root.registerParticipant(participant(ModuleId::NetworkTransport, "network", events), error));
	EXPECT_FALSE(root.start(error));
	EXPECT_EQ(root.getState(), ModuleLifecycleState::Failed);
	EXPECT_FALSE(root.isReady());
	EXPECT_TRUE(root.getStartedModules().empty());
	EXPECT_EQ(error, "module 'scheduler' participant 'scheduler' failed to start: start failure");
	EXPECT_EQ(events, (std::vector<std::string> {
						  "start:engine-runtime",
						  "start:scheduler",
						  "stop:engine-runtime",
					  }));
}

TEST(Mge004ModuleLifecycleTest, StopIsIdempotentAndContinuesAfterStopFailure) {
	LifecycleFixture fixture;
	ModuleCompositionRoot root(fixture.selection, 0, fixture.registry);
	std::vector<std::string> events;
	std::string error;

	ASSERT_TRUE(root.registerParticipant(participant(ModuleId::EngineRuntime, "engine", events, false, true), error));
	ASSERT_TRUE(root.registerParticipant(participant(ModuleId::Scheduler, "scheduler", events), error));
	ASSERT_TRUE(root.start(error));
	root.stop();
	root.stop();

	EXPECT_EQ(events, (std::vector<std::string> {
						  "start:engine-runtime",
						  "start:scheduler",
						  "stop:scheduler",
						  "stop:engine-runtime",
					  }));
	ASSERT_EQ(root.getShutdownErrors().size(), 1);
	EXPECT_EQ(root.getShutdownErrors().front(), "module 'engine-runtime' participant 'engine' failed to stop: stop failure");
}

TEST(Mge004ModuleLifecycleTest, RejectsDuplicateUnselectedAndLateRegistration) {
	LifecycleFixture fixture;
	ModuleCompositionRoot root(fixture.selection, 0, fixture.registry);
	std::vector<std::string> events;
	std::string error;

	ASSERT_TRUE(root.registerParticipant(participant(ModuleId::EngineRuntime, "engine", events), error));
	EXPECT_FALSE(root.registerParticipant(participant(ModuleId::EngineRuntime, "duplicate", events), error));
	EXPECT_EQ(error, "module 'engine-runtime' already has a lifecycle participant");
	EXPECT_FALSE(root.registerParticipant(participant(ModuleId::Players, "players", events), error));
	EXPECT_EQ(error, "module 'players' is not selected by the game profile");
	ASSERT_TRUE(root.start(error));
	EXPECT_FALSE(root.registerParticipant(participant(ModuleId::Scheduler, "late", events), error));
	EXPECT_EQ(error, "module lifecycle registration is closed");
}

TEST(Mge004ModuleLifecycleTest, ReadinessIsPublishedOnlyAfterEveryParticipantStarts) {
	LifecycleFixture fixture;
	ModuleCompositionRoot root(fixture.selection, 0, fixture.registry);
	std::vector<std::string> events;
	std::string error;
	bool sawStartingState = false;

	ASSERT_TRUE(root.registerParticipant(ModuleLifecycleParticipant {
											 .id = ModuleId::EngineRuntime,
											 .name = "engine",
											 .start = [&root, &sawStartingState] { sawStartingState = root.getState() == ModuleLifecycleState::Starting && !root.isReady(); },
											 .stop = [] {},
										 },
	                                     error));
	ASSERT_TRUE(root.start(error));
	EXPECT_TRUE(sawStartingState);
	EXPECT_TRUE(root.isReady());
	root.stop();
	EXPECT_FALSE(root.isReady());
}

TEST(Mge004ModuleLifecycleTest, SeparateRootsDoNotShareMutableLifecycleState) {
	LifecycleFixture fixture;
	ModuleCompositionRoot first(fixture.selection, 0, fixture.registry);
	ModuleCompositionRoot second(fixture.selection, 0, fixture.registry);
	std::vector<std::string> firstEvents;
	std::vector<std::string> secondEvents;
	std::string error;

	ASSERT_TRUE(first.registerParticipant(participant(ModuleId::EngineRuntime, "first", firstEvents), error));
	ASSERT_TRUE(second.registerParticipant(participant(ModuleId::EngineRuntime, "second", secondEvents), error));
	ASSERT_TRUE(first.start(error));
	EXPECT_TRUE(first.isReady());
	EXPECT_EQ(second.getState(), ModuleLifecycleState::Configuring);
	EXPECT_TRUE(secondEvents.empty());

	first.stop();
	ASSERT_TRUE(second.start(error));
	EXPECT_TRUE(second.isReady());
	EXPECT_EQ(secondEvents, (std::vector<std::string> { "start:engine-runtime" }));
}

TEST(Mge004ModuleLifecycleTest, RejectsInvalidGraphBeforeLifecycleConfiguration) {
	LifecycleFixture fixture;
	const std::array<ModuleId, 1> invalidSelection { ModuleId::NetworkTransport };

	EXPECT_THROW(
		ModuleCompositionRoot(invalidSelection, 0, fixture.registry),
		std::invalid_argument
	);
}
