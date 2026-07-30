#include <errmsg.h>
#include <mysql.h>

#include "database/database_outage_recovery_evidence.hpp"

#include <chrono>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>

using namespace std::chrono_literals;

namespace {
	struct DatabaseConfig final {
		std::string host;
		std::string user;
		std::string password;
		std::string database;
		unsigned int port = 0;
	};

	[[nodiscard]] std::string requiredEnvironment(const char* name) {
		const char* value = std::getenv(name);
		if (value == nullptr) {
			throw std::runtime_error(std::string("missing environment variable: ") + name);
		}
		return value;
	}

	[[nodiscard]] DatabaseConfig readConfig() {
		const auto parsedPort = std::stoul(requiredEnvironment("PRS003EB_DB_PORT"));
		if (parsedPort == 0 || parsedPort > 65535) {
			throw std::runtime_error("PRS003EB_DB_PORT is outside the TCP port range");
		}
		return DatabaseConfig {
			.host = requiredEnvironment("PRS003EB_DB_HOST"),
			.user = requiredEnvironment("PRS003EB_DB_USER"),
			.password = requiredEnvironment("PRS003EB_DB_PASSWORD"),
			.database = requiredEnvironment("PRS003EB_DB_NAME"),
			.port = static_cast<unsigned int>(parsedPort),
		};
	}

	void require(bool condition, std::string_view message) {
		if (!condition) {
			throw std::runtime_error(std::string(message));
		}
	}

	class Connection final {
	public:
		explicit Connection(const DatabaseConfig &config) {
			handle_ = mysql_init(nullptr);
			if (handle_ == nullptr) {
				throw std::runtime_error("mysql_init failed");
			}
			if (mysql_real_connect(
					handle_,
					config.host.c_str(),
					config.user.c_str(),
					config.password.c_str(),
					config.database.c_str(),
					config.port,
					nullptr,
					0
				)
			    == nullptr) {
				const std::string message = mysql_error(handle_);
				mysql_close(handle_);
				handle_ = nullptr;
				throw std::runtime_error("mysql_real_connect failed: " + message);
			}
		}

		~Connection() {
			if (handle_ != nullptr) {
				mysql_close(handle_);
			}
		}

		Connection(const Connection &) = delete;
		Connection &operator=(const Connection &) = delete;
		Connection(Connection &&) = delete;
		Connection &operator=(Connection &&) = delete;

		[[nodiscard]] MYSQL* get() const noexcept {
			return handle_;
		}

	private:
		MYSQL* handle_ = nullptr;
	};

	struct OperationEvidence final {
		bool succeeded = false;
		unsigned int nativeError = 0;
		uint32_t attempts = 0;
	};

	[[nodiscard]] OperationEvidence executeOnce(MYSQL* handle, std::string_view sql) {
		OperationEvidence evidence;
		++evidence.attempts;
		if (mysql_real_query(handle, sql.data(), sql.size()) != 0) {
			evidence.nativeError = mysql_errno(handle);
			return evidence;
		}

		MYSQL_RES* result = mysql_store_result(handle);
		if (result != nullptr) {
			mysql_free_result(result);
		} else if (mysql_field_count(handle) != 0) {
			evidence.nativeError = mysql_errno(handle);
			return evidence;
		}
		evidence.succeeded = true;
		return evidence;
	}

	void executeRequired(MYSQL* handle, std::string_view sql) {
		const auto evidence = executeOnce(handle, sql);
		if (!evidence.succeeded) {
			throw std::runtime_error(
				"required disposable SQL failed with native error " + std::to_string(evidence.nativeError)
			);
		}
	}

	[[nodiscard]] uint64_t scalarUnsigned(MYSQL* handle, std::string_view sql) {
		if (mysql_real_query(handle, sql.data(), sql.size()) != 0) {
			throw std::runtime_error("scalar query failed with native error " + std::to_string(mysql_errno(handle)));
		}
		MYSQL_RES* result = mysql_store_result(handle);
		if (result == nullptr) {
			throw std::runtime_error("mysql_store_result returned null for scalar query");
		}
		MYSQL_ROW row = mysql_fetch_row(result);
		if (row == nullptr || row[0] == nullptr) {
			mysql_free_result(result);
			throw std::runtime_error("scalar query returned no value");
		}
		const auto value = std::stoull(row[0]);
		mysql_free_result(result);
		return value;
	}

	void killConnection(MYSQL* control, unsigned long connectionId) {
		executeRequired(control, "KILL CONNECTION " + std::to_string(connectionId));
	}

	[[nodiscard]] std::string markerPredicate(std::string_view marker) {
		return "marker = '" + std::string(marker) + "'";
	}

	[[nodiscard]] uint64_t countMarker(const DatabaseConfig &config, std::string_view marker) {
		Connection audit(config);
		return scalarUnsigned(
			audit.get(),
			"SELECT COUNT(*) FROM prs003e_b_recovery_probe WHERE " + markerPredicate(marker)
		);
	}

	void deleteMarker(const DatabaseConfig &config, std::string_view marker) {
		Connection cleanup(config);
		executeRequired(
			cleanup.get(),
			"DELETE FROM prs003e_b_recovery_probe WHERE " + markerPredicate(marker)
		);
	}

	void prepareDisposableSchema(const DatabaseConfig &config) {
		Connection connection(config);
		executeRequired(
			connection.get(),
			"CREATE TABLE IF NOT EXISTS prs003e_b_recovery_probe ("
			"marker VARCHAR(64) NOT NULL PRIMARY KEY"
			") ENGINE=InnoDB"
		);
		executeRequired(connection.get(), "TRUNCATE TABLE prs003e_b_recovery_probe");
	}

	struct ProbeRun final {
		DatabaseRecoveryProbeAttempt attempt;
		uint32_t readAttempts = 0;
		uint32_t beginAttempts = 0;
		uint32_t writeAttempts = 0;
		uint32_t rollbackAttempts = 0;
		uint64_t beforeRows = 0;
		uint64_t afterRows = 0;
	};

	[[nodiscard]] ProbeRun successfulProbe(const DatabaseConfig &config, std::string_view marker) {
		ProbeRun run;
		run.beforeRows = countMarker(config, marker);
		Connection probe(config);
		const auto read = executeOnce(probe.get(), "SELECT 1");
		const auto begin = executeOnce(probe.get(), "START TRANSACTION");
		OperationEvidence write;
		OperationEvidence rollback;
		if (begin.succeeded) {
			write = executeOnce(
				probe.get(),
				"INSERT INTO prs003e_b_recovery_probe(marker) VALUES ('" + std::string(marker) + "')"
			);
			rollback = executeOnce(probe.get(), "ROLLBACK");
		}
		run.afterRows = countMarker(config, marker);
		run.readAttempts = read.attempts;
		run.beginAttempts = begin.attempts;
		run.writeAttempts = write.attempts;
		run.rollbackAttempts = rollback.attempts;
		run.attempt = DatabaseRecoveryProbeAttempt {
			.readSucceeded = read.succeeded,
			.transactionBeginSucceeded = begin.succeeded,
			.transactionWriteSucceeded = write.succeeded,
			.transactionRollbackSucceeded = rollback.succeeded,
			.probeObjectUnchanged = run.beforeRows == run.afterRows,
		};
		return run;
	}

	[[nodiscard]] ProbeRun failedReadProbe(const DatabaseConfig &config) {
		Connection probe(config);
		const auto read = executeOnce(probe.get(), "SELECT * FROM prs003e_b_missing_probe_table");
		return ProbeRun {
			.attempt = DatabaseRecoveryProbeAttempt {
				.readSucceeded = read.succeeded,
				.probeObjectUnchanged = true,
			},
			.readAttempts = read.attempts,
		};
	}

	[[nodiscard]] ProbeRun failedBeginProbe(const DatabaseConfig &config, std::string_view marker) {
		ProbeRun run;
		run.beforeRows = countMarker(config, marker);
		Connection probe(config);
		Connection control(config);
		const auto read = executeOnce(probe.get(), "SELECT 1");
		killConnection(control.get(), mysql_thread_id(probe.get()));
		const auto begin = executeOnce(probe.get(), "START TRANSACTION");
		run.afterRows = countMarker(config, marker);
		run.readAttempts = read.attempts;
		run.beginAttempts = begin.attempts;
		run.attempt = DatabaseRecoveryProbeAttempt {
			.readSucceeded = read.succeeded,
			.transactionBeginSucceeded = begin.succeeded,
			.probeObjectUnchanged = run.beforeRows == run.afterRows,
		};
		return run;
	}

	[[nodiscard]] ProbeRun failedWriteProbe(const DatabaseConfig &config, std::string_view marker) {
		Connection seed(config);
		executeRequired(
			seed.get(),
			"INSERT INTO prs003e_b_recovery_probe(marker) VALUES ('" + std::string(marker) + "')"
		);

		ProbeRun run;
		run.beforeRows = countMarker(config, marker);
		Connection probe(config);
		const auto read = executeOnce(probe.get(), "SELECT 1");
		const auto begin = executeOnce(probe.get(), "START TRANSACTION");
		const auto write = executeOnce(
			probe.get(),
			"INSERT INTO prs003e_b_recovery_probe(marker) VALUES ('" + std::string(marker) + "')"
		);
		const auto rollback = executeOnce(probe.get(), "ROLLBACK");
		run.afterRows = countMarker(config, marker);
		deleteMarker(config, marker);
		run.readAttempts = read.attempts;
		run.beginAttempts = begin.attempts;
		run.writeAttempts = write.attempts;
		run.rollbackAttempts = rollback.attempts;
		run.attempt = DatabaseRecoveryProbeAttempt {
			.readSucceeded = read.succeeded,
			.transactionBeginSucceeded = begin.succeeded,
			.transactionWriteSucceeded = write.succeeded,
			.transactionRollbackSucceeded = rollback.succeeded,
			.probeObjectUnchanged = run.beforeRows == run.afterRows,
		};
		return run;
	}

	[[nodiscard]] ProbeRun failedRollbackProbe(const DatabaseConfig &config, std::string_view marker) {
		ProbeRun run;
		run.beforeRows = countMarker(config, marker);
		Connection probe(config);
		Connection control(config);
		const auto read = executeOnce(probe.get(), "SELECT 1");
		const auto begin = executeOnce(probe.get(), "START TRANSACTION");
		const auto write = executeOnce(
			probe.get(),
			"INSERT INTO prs003e_b_recovery_probe(marker) VALUES ('" + std::string(marker) + "')"
		);
		killConnection(control.get(), mysql_thread_id(probe.get()));
		const auto rollback = executeOnce(probe.get(), "ROLLBACK");
		run.afterRows = countMarker(config, marker);
		run.readAttempts = read.attempts;
		run.beginAttempts = begin.attempts;
		run.writeAttempts = write.attempts;
		run.rollbackAttempts = rollback.attempts;
		run.attempt = DatabaseRecoveryProbeAttempt {
			.readSucceeded = read.succeeded,
			.transactionBeginSucceeded = begin.succeeded,
			.transactionWriteSucceeded = write.succeeded,
			.transactionRollbackSucceeded = rollback.succeeded,
			.probeObjectUnchanged = run.beforeRows == run.afterRows,
		};
		return run;
	}

	struct UnknownOutcomeEvidence final {
		uint32_t mutationAttempts = 0;
		uint32_t commitAttempts = 0;
		unsigned int commitError = 0;
		uint64_t persistedRows = 0;
	};

	[[nodiscard]] UnknownOutcomeEvidence failedGameplayCommit(const DatabaseConfig &config, std::string_view marker) {
		Connection gameplay(config);
		Connection control(config);
		executeRequired(gameplay.get(), "START TRANSACTION");
		const auto mutation = executeOnce(
			gameplay.get(),
			"INSERT INTO prs003e_b_recovery_probe(marker) VALUES ('" + std::string(marker) + "')"
		);
		require(mutation.succeeded, "unknown-outcome setup mutation failed");
		killConnection(control.get(), mysql_thread_id(gameplay.get()));
		const auto commit = executeOnce(gameplay.get(), "COMMIT");
		return UnknownOutcomeEvidence {
			.mutationAttempts = mutation.attempts,
			.commitAttempts = commit.attempts,
			.commitError = commit.nativeError,
			.persistedRows = countMarker(config, marker),
		};
	}

	[[nodiscard]] DatabaseRecoveryProbeAttempt successfulAttempt() {
		return DatabaseRecoveryProbeAttempt {
			.readSucceeded = true,
			.transactionBeginSucceeded = true,
			.transactionWriteSucceeded = true,
			.transactionRollbackSucceeded = true,
			.probeObjectUnchanged = true,
		};
	}

	void verifyFiniteTrackerContract() {
		bool invalidRejected = false;
		try {
			DatabaseOutageRecoveryEvidence invalid({ 0, 1, 1ms });
			(void)invalid;
		} catch (const std::invalid_argument &) {
			invalidRejected = true;
		}
		require(invalidRejected, "bounds: zero required successes were accepted");

		DatabaseOutageRecoveryEvidence tracker({ 2, 4, 50ms });
		const auto started = tracker.begin(100ms);
		require(started.deadline == 150ms, "deadline: fixed candidate deadline mismatch");
		const auto first = tracker.recordProbe(successfulAttempt(), 110ms);
		require(first.action == DatabaseRecoveryEvidenceAction::Continue, "window: one success was sufficient");

		auto readFailure = successfulAttempt();
		readFailure.readSucceeded = false;
		const auto failed = tracker.recordProbe(readFailure, 120ms);
		require(failed.reason == DatabaseRecoveryEvidenceReason::ReadFailed, "window: read failure reason mismatch");
		require(failed.consecutiveSuccesses == 0U, "window: failure did not reset consecutive successes");
		require(failed.deadline == started.deadline, "window: failure extended the deadline");

		const auto expired = tracker.recordProbe(successfulAttempt(), 150ms);
		require(expired.reason == DatabaseRecoveryEvidenceReason::DeadlineExpired, "deadline: exact deadline did not expire");
		require(expired.deadlineExpired, "deadline: expiration evidence missing");

		DatabaseOutageRecoveryEvidence budget({ 3, 3, 100ms });
		(void)budget.begin(0ms);
		(void)budget.recordProbe(successfulAttempt(), 10ms);
		(void)budget.recordProbe(readFailure, 20ms);
		const auto exhausted = budget.recordProbe(successfulAttempt(), 30ms);
		require(exhausted.action == DatabaseRecoveryEvidenceAction::Stop, "budget: finite attempt limit did not stop");
		require(exhausted.attemptBudgetExhausted, "budget: exhaustion evidence missing");
	}

	void verifySyntheticFailureReasons() {
		struct FailureCase final {
			DatabaseRecoveryProbeAttempt attempt;
			DatabaseRecoveryEvidenceReason reason;
		};
		const FailureCase cases[] = {
			{ { false, true, true, true, true }, DatabaseRecoveryEvidenceReason::ReadFailed },
			{ { true, false, true, true, true }, DatabaseRecoveryEvidenceReason::TransactionBeginFailed },
			{ { true, true, false, true, true }, DatabaseRecoveryEvidenceReason::TransactionWriteFailed },
			{ { true, true, true, false, true }, DatabaseRecoveryEvidenceReason::TransactionRollbackFailed },
			{ { true, true, true, true, false }, DatabaseRecoveryEvidenceReason::ProbeObjectChanged },
		};
		for (const auto &failureCase : cases) {
			DatabaseOutageRecoveryEvidence tracker({ 2, 3, 100ms });
			(void)tracker.begin(0ms);
			const auto decision = tracker.recordProbe(failureCase.attempt, 10ms);
			require(decision.reason == failureCase.reason, "synthetic failure reason mismatch");
		}
	}

	void verifyStateOwnerContract() {
		DatabaseOutageStateMachine degraded({ 100ms, 100ms });
		const auto failure = degraded.runtimeFailure(
			1,
			DatabaseOutageFailureReason::QueryFailed,
			DatabaseOutageCommitOutcome::KnownNotCommitted,
			0ms
		);
		require(failure.after.state == DatabaseOutageState::Degraded, "state owner: initial failure did not enter degraded");

		DatabaseOutageRecoveryEvidence tracker({ 2, 3, 100ms });
		(void)tracker.begin(10ms);
		(void)tracker.recordProbe(successfulAttempt(), 20ms);
		const auto ready = tracker.recordProbe(successfulAttempt(), 30ms);
		require(ready.action == DatabaseRecoveryEvidenceAction::PublishRecoveryEvidenceAccepted, "state owner: completed window did not request publication");
		const auto published = tracker.publishIfReady(degraded, 2, 40ms);
		require(published.has_value(), "state owner: publication was not emitted");
		require(published->disposition == DatabaseOutageEventDisposition::AcceptedNoStateChange, "state owner: evidence publication was rejected");
		require(published->after.state == DatabaseOutageState::Degraded, "state owner: evidence changed degraded state");
		require(published->after.recoveryEvidenceAccepted, "state owner: evidence flag was not accepted");
		require(!tracker.publishIfReady(degraded, 3, 50ms).has_value(), "state owner: evidence published more than once");
		require(tracker.summary().acceptedPublications == 1U, "state owner: accepted publication count mismatch");

		(void)tracker.qualifyingFailure();
		const auto laterFailure = degraded.runtimeFailure(
			3,
			DatabaseOutageFailureReason::RecoveryProbeFailed,
			DatabaseOutageCommitOutcome::KnownNotCommitted,
			60ms
		);
		require(!laterFailure.after.recoveryEvidenceAccepted, "state owner: later failure did not invalidate evidence");
		require(!tracker.summary().evidenceAccepted, "tracker: later failure did not invalidate local evidence");

		DatabaseOutageStateMachine maintenance({ 100ms, 100ms });
		const auto entered = maintenance.operatorEnterMaintenance(1, 0ms);
		require(entered.after.state == DatabaseOutageState::Maintenance, "maintenance: operator transition failed");
		DatabaseOutageRecoveryEvidence maintenanceTracker({ 1, 1, 100ms });
		(void)maintenanceTracker.begin(10ms);
		(void)maintenanceTracker.recordProbe(successfulAttempt(), 20ms);
		const auto maintenancePublication = maintenanceTracker.publishIfReady(maintenance, 2, 30ms);
		require(maintenancePublication.has_value(), "maintenance: publication missing");
		require(maintenancePublication->after.state == DatabaseOutageState::Maintenance, "maintenance: evidence changed state automatically");
	}

	void verifyActualFailureEvidence(const DatabaseConfig &config) {
		const auto read = failedReadProbe(config);
		require(read.readAttempts == 1U && !read.attempt.readSucceeded, "read failure: probe was not one-shot");
		DatabaseOutageRecoveryEvidence readTracker({ 2, 3, 500ms });
		(void)readTracker.begin(0ms);
		require(readTracker.recordProbe(read.attempt, 10ms).reason == DatabaseRecoveryEvidenceReason::ReadFailed, "read failure: tracker reason mismatch");

		const auto begin = failedBeginProbe(config, "begin-failure");
		require(begin.readAttempts == 1U && begin.beginAttempts == 1U, "begin failure: operation attempt count mismatch");
		require(begin.attempt.readSucceeded && !begin.attempt.transactionBeginSucceeded, "begin failure: injected result mismatch");
		DatabaseOutageRecoveryEvidence beginTracker({ 2, 3, 500ms });
		(void)beginTracker.begin(0ms);
		require(beginTracker.recordProbe(begin.attempt, 10ms).reason == DatabaseRecoveryEvidenceReason::TransactionBeginFailed, "begin failure: tracker reason mismatch");

		const auto write = failedWriteProbe(config, "write-failure");
		require(write.readAttempts == 1U && write.beginAttempts == 1U && write.writeAttempts == 1U && write.rollbackAttempts == 1U, "write failure: operation attempt count mismatch");
		require(!write.attempt.transactionWriteSucceeded && write.attempt.transactionRollbackSucceeded, "write failure: injected result mismatch");
		require(write.attempt.probeObjectUnchanged, "write failure: disposable probe object changed");
		DatabaseOutageRecoveryEvidence writeTracker({ 2, 3, 500ms });
		(void)writeTracker.begin(0ms);
		require(writeTracker.recordProbe(write.attempt, 10ms).reason == DatabaseRecoveryEvidenceReason::TransactionWriteFailed, "write failure: tracker reason mismatch");

		const auto rollback = failedRollbackProbe(config, "rollback-failure");
		require(rollback.readAttempts == 1U && rollback.beginAttempts == 1U && rollback.writeAttempts == 1U && rollback.rollbackAttempts == 1U, "rollback failure: operation attempt count mismatch");
		require(!rollback.attempt.transactionRollbackSucceeded, "rollback failure: rollback unexpectedly succeeded");
		require(rollback.attempt.probeObjectUnchanged, "rollback failure: killed transaction persisted a row");
		DatabaseOutageRecoveryEvidence rollbackTracker({ 2, 3, 500ms });
		(void)rollbackTracker.begin(0ms);
		require(rollbackTracker.recordProbe(rollback.attempt, 10ms).reason == DatabaseRecoveryEvidenceReason::TransactionRollbackFailed, "rollback failure: tracker reason mismatch");
	}

	void verifyActualWindowAndNoReplay(const DatabaseConfig &config) {
		const auto gameplay = failedGameplayCommit(config, "unknown-gameplay");
		require(gameplay.mutationAttempts == 1U, "unknown outcome: gameplay mutation was replayed");
		require(gameplay.commitAttempts == 1U, "unknown outcome: commit was attempted more than once");
		require(gameplay.commitError == CR_SERVER_LOST || gameplay.commitError == CR_SERVER_GONE_ERROR, "unknown outcome: expected connection failure");
		require(gameplay.persistedRows == 0U, "unknown outcome: killed transaction persisted a row");

		DatabaseOutageStateMachine stateOwner({ 100ms, 100ms });
		const auto outage = stateOwner.runtimeFailure(
			1,
			DatabaseOutageFailureReason::TransactionCommitFailed,
			DatabaseOutageCommitOutcome::Unknown,
			0ms
		);
		require(outage.after.state == DatabaseOutageState::Draining, "unknown outcome: state owner did not enter draining");
		const auto maintenance = stateOwner.operatorEnterMaintenance(2, 10ms);
		require(maintenance.after.state == DatabaseOutageState::Maintenance, "unknown outcome: maintenance transition failed");

		DatabaseOutageRecoveryEvidence singleSuccess({ 3, 5, 500ms });
		(void)singleSuccess.begin(20ms);
		const auto one = successfulProbe(config, "ordinary-success");
		require(one.readAttempts == 1U && one.beginAttempts == 1U && one.writeAttempts == 1U && one.rollbackAttempts == 1U, "ordinary success: operation attempt count mismatch");
		require(one.attempt.probeObjectUnchanged, "ordinary success: rollback changed probe object");
		const auto oneDecision = singleSuccess.recordProbe(one.attempt, 30ms);
		require(oneDecision.action == DatabaseRecoveryEvidenceAction::Continue, "ordinary success: one successful query/window attempt was sufficient");
		require(!singleSuccess.publishIfReady(stateOwner, 3, 40ms).has_value(), "ordinary success: incomplete window published evidence");

		DatabaseOutageRecoveryEvidence resetWindow({ 2, 4, 500ms });
		const auto resetStart = resetWindow.begin(50ms);
		const auto resetFirst = successfulProbe(config, "reset-first");
		(void)resetWindow.recordProbe(resetFirst.attempt, 60ms);
		const auto resetFailure = failedWriteProbe(config, "reset-write-failure");
		const auto resetDecision = resetWindow.recordProbe(resetFailure.attempt, 70ms);
		require(resetDecision.consecutiveSuccesses == 0U, "reset window: failure did not reset successes");
		require(resetDecision.deadline == resetStart.deadline, "reset window: failure extended deadline");
		const auto resetSecond = successfulProbe(config, "reset-second");
		const auto resetThird = successfulProbe(config, "reset-third");
		(void)resetWindow.recordProbe(resetSecond.attempt, 80ms);
		const auto resetReady = resetWindow.recordProbe(resetThird.attempt, 90ms);
		require(resetReady.action == DatabaseRecoveryEvidenceAction::PublishRecoveryEvidenceAccepted, "reset window: bounded replacement successes did not complete");

		DatabaseOutageRecoveryEvidence window({ 3, 5, 500ms });
		(void)window.begin(100ms);
		const auto first = successfulProbe(config, "window-first");
		const auto second = successfulProbe(config, "window-second");
		const auto third = successfulProbe(config, "window-third");
		require(first.attempt.probeObjectUnchanged && second.attempt.probeObjectUnchanged && third.attempt.probeObjectUnchanged, "success window: rollback left probe data");
		require(window.recordProbe(first.attempt, 110ms).action == DatabaseRecoveryEvidenceAction::Continue, "success window: first attempt completed window");
		require(window.recordProbe(second.attempt, 120ms).action == DatabaseRecoveryEvidenceAction::Continue, "success window: second attempt completed window");
		require(window.recordProbe(third.attempt, 130ms).action == DatabaseRecoveryEvidenceAction::PublishRecoveryEvidenceAccepted, "success window: third attempt did not complete window");
		const auto publication = window.publishIfReady(stateOwner, 3, 140ms);
		require(publication.has_value(), "success window: accepted evidence was not published");
		require(publication->disposition == DatabaseOutageEventDisposition::AcceptedNoStateChange, "success window: state owner rejected evidence");
		require(publication->after.state == DatabaseOutageState::Maintenance, "success window: evidence auto-resumed maintenance");
		require(publication->after.recoveryEvidenceAccepted, "success window: evidence flag missing");
		require(!window.publishIfReady(stateOwner, 4, 150ms).has_value(), "success window: evidence published more than once");

		(void)window.qualifyingFailure();
		const auto laterFailure = stateOwner.runtimeFailure(
			4,
			DatabaseOutageFailureReason::RecoveryProbeFailed,
			DatabaseOutageCommitOutcome::KnownNotCommitted,
			160ms
		);
		require(laterFailure.after.state == DatabaseOutageState::Maintenance, "later failure: maintenance state changed unexpectedly");
		require(!laterFailure.after.recoveryEvidenceAccepted, "later failure: accepted evidence was not invalidated");
		require(!window.summary().evidenceAccepted, "later failure: tracker evidence was not invalidated");
	}

	void runEvidence(const DatabaseConfig &config) {
		verifyFiniteTrackerContract();
		verifySyntheticFailureReasons();
		verifyStateOwnerContract();
		prepareDisposableSchema(config);
		verifyActualFailureEvidence(config);
		verifyActualWindowAndNoReplay(config);
		Connection finalAudit(config);
		require(scalarUnsigned(finalAudit.get(), "SELECT COUNT(*) FROM prs003e_b_recovery_probe") == 0U, "final audit: disposable probe table is not empty");
	}
} // namespace

int main() {
	bool libraryInitialized = false;
	try {
		if (mysql_library_init(0, nullptr, nullptr) != 0) {
			throw std::runtime_error("mysql_library_init failed");
		}
		libraryInitialized = true;
		runEvidence(readConfig());
		mysql_library_end();
		libraryInitialized = false;
		std::cout << "PRS-003E-B bounded recovery evidence: PASS\n";
		return 0;
	} catch (const std::exception &exception) {
		if (libraryInitialized) {
			mysql_library_end();
		}
		std::cerr << "PRS-003E-B bounded recovery evidence: FAIL: " << exception.what() << '\n';
		return 1;
	}
}
