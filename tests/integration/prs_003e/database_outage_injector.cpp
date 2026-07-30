#include <errmsg.h>
#include <mysql.h>

#include "database/database_failure_classification.hpp"

#include <atomic>
#include <chrono>
#include <cstdlib>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <utility>

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
		const auto portText = requiredEnvironment("PRS003E_DB_PORT");
		const auto parsedPort = std::stoul(portText);
		if (parsedPort == 0 || parsedPort > 65535) {
			throw std::runtime_error("PRS003E_DB_PORT is outside the TCP port range");
		}
		return DatabaseConfig {
			.host = requiredEnvironment("PRS003E_DB_HOST"),
			.user = requiredEnvironment("PRS003E_DB_USER"),
			.password = requiredEnvironment("PRS003E_DB_PASSWORD"),
			.database = requiredEnvironment("PRS003E_DB_NAME"),
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

			bool reconnect = false;
			if (mysql_options(handle_, MYSQL_OPT_RECONNECT, &reconnect) != 0) {
				const std::string message = mysql_error(handle_);
				mysql_close(handle_);
				handle_ = nullptr;
				throw std::runtime_error("cannot disable MYSQL_OPT_RECONNECT: " + message);
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
		unsigned int attempts = 0;
	};

	[[nodiscard]] OperationEvidence executeOnce(MYSQL* handle, std::string_view sql) {
		OperationEvidence evidence;
		++evidence.attempts;
		evidence.succeeded = mysql_real_query(handle, sql.data(), sql.size()) == 0;
		evidence.nativeError = evidence.succeeded ? 0U : mysql_errno(handle);
		return evidence;
	}

	void executeRequired(MYSQL* handle, std::string_view sql) {
		const auto evidence = executeOnce(handle, sql);
		if (!evidence.succeeded) {
			throw std::runtime_error(
				"required SQL failed with native error " + std::to_string(evidence.nativeError) + ": " + mysql_error(handle)
			);
		}
	}

	[[nodiscard]] uint64_t scalarUnsigned(MYSQL* handle, std::string_view sql) {
		executeRequired(handle, sql);
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

	[[nodiscard]] DatabaseNativeErrorKind classifyNativeError(unsigned int nativeError) {
		if (nativeError == CR_SERVER_LOST) {
			return DatabaseNativeErrorKind::ConnectionLost;
		}
		if (nativeError == CR_SERVER_GONE_ERROR) {
			return DatabaseNativeErrorKind::ServerGone;
		}
		return nativeError == 0 ? DatabaseNativeErrorKind::None : DatabaseNativeErrorKind::Other;
	}

	[[nodiscard]] DatabaseOutageEventReason expectedInitialEventReason(DatabaseRuntimeResultKind result) {
		return result == DatabaseRuntimeResultKind::FailureUnknownCommitOutcome
			? DatabaseOutageEventReason::UnknownCommitOutcome
			: DatabaseOutageEventReason::FirstRuntimeFailure;
	}

	void verifyPublishedFailure(
		DatabaseRuntimeOperation operation,
		unsigned int nativeError,
		DatabaseRuntimeResultKind expectedResult,
		DatabaseOutageFailureReason expectedFailureReason,
		DatabaseOutageCommitOutcome expectedOutcome,
		std::string_view label
	) {
		const auto classification = classifyDatabaseRuntimeResult(operation, false, classifyNativeError(nativeError));
		require(classification.result == expectedResult, std::string(label) + ": result classification mismatch");
		require(classification.failureReason == expectedFailureReason, std::string(label) + ": failure reason mismatch");
		require(classification.commitOutcome == expectedOutcome, std::string(label) + ": commit outcome mismatch");

		DatabaseOutageStateMachine eventState({ 100ms, 50ms });
		DatabaseOutageEventPublisher eventPublisher(eventState);
		const auto publication = eventPublisher.publish(classification, 100ms);
		require(publication.event.has_value(), std::string(label) + ": publication did not emit an event");
		require(publication.event->eventSequence == 1U, std::string(label) + ": first event sequence is not one");
		require(publication.event->eventTime == 100ms, std::string(label) + ": event time mismatch");
		require(publication.event->disposition == DatabaseOutageEventDisposition::Applied, std::string(label) + ": event was not applied");
		require(publication.event->reason == expectedInitialEventReason(expectedResult), std::string(label) + ": event reason mismatch");
		require(publication.event->after.lastFailureReason == expectedFailureReason, std::string(label) + ": snapshot reason mismatch");
		require(publication.event->after.lastFailureOutcome == expectedOutcome, std::string(label) + ": snapshot outcome mismatch");

		DatabaseOutageStateMachine callerState({ 100ms, 50ms });
		DatabaseOutageEventPublisher callerPublisher(callerState);
		const bool callerResult = callerPublisher.publishAndPreserve(false, classification, 100ms);
		require(!callerResult, std::string(label) + ": publication converted caller failure to success");
	}

	struct InterruptedConnectionEvidence final {
		unsigned int lostError = 0;
		unsigned int goneError = 0;
		unsigned int lostAttempts = 0;
		unsigned int goneAttempts = 0;
		std::exception_ptr workerFailure;
	};

	[[nodiscard]] InterruptedConnectionEvidence injectLostThenGone(const DatabaseConfig &config) {
		std::atomic<bool> connectionReady = false;
		std::atomic<bool> workerFailed = false;
		unsigned long connectionId = 0;
		InterruptedConnectionEvidence evidence;

		std::thread worker([&] {
			if (mysql_thread_init() != 0) {
				evidence.workerFailure = std::make_exception_ptr(std::runtime_error("mysql_thread_init failed"));
				workerFailed.store(true, std::memory_order_release);
				connectionReady.store(true, std::memory_order_release);
				return;
			}
			try {
				Connection primary(config);
				connectionId = mysql_thread_id(primary.get());
				connectionReady.store(true, std::memory_order_release);

				const auto lost = executeOnce(primary.get(), "SELECT SLEEP(30)");
				evidence.lostError = lost.nativeError;
				evidence.lostAttempts = lost.attempts;

				const auto gone = executeOnce(primary.get(), "SELECT 1");
				evidence.goneError = gone.nativeError;
				evidence.goneAttempts = gone.attempts;
			} catch (...) {
				evidence.workerFailure = std::current_exception();
				workerFailed.store(true, std::memory_order_release);
				connectionReady.store(true, std::memory_order_release);
			}
			mysql_thread_end();
		});

		while (!connectionReady.load(std::memory_order_acquire)) {
			std::this_thread::sleep_for(5ms);
		}
		if (!workerFailed.load(std::memory_order_acquire)) {
			Connection control(config);
			std::this_thread::sleep_for(250ms);
			killConnection(control.get(), connectionId);
		}
		worker.join();
		if (evidence.workerFailure != nullptr) {
			std::rethrow_exception(evidence.workerFailure);
		}
		return evidence;
	}

	[[nodiscard]] OperationEvidence injectBeginFailure(const DatabaseConfig &config) {
		Connection primary(config);
		Connection control(config);
		killConnection(control.get(), mysql_thread_id(primary.get()));
		return executeOnce(primary.get(), "START TRANSACTION");
	}

	struct TransactionFailureEvidence final {
		OperationEvidence terminalOperation;
		unsigned int mutationAttempts = 0;
		uint64_t persistedRows = 0;
	};

	[[nodiscard]] TransactionFailureEvidence injectCommitFailure(const DatabaseConfig &config) {
		Connection primary(config);
		Connection control(config);
		executeRequired(primary.get(), "START TRANSACTION");
		const auto mutation = executeOnce(primary.get(), "INSERT INTO prs003e_evidence(marker) VALUES ('commit-failure')");
		require(mutation.succeeded, "commit-failure: setup mutation did not execute");
		killConnection(control.get(), mysql_thread_id(primary.get()));
		const auto commit = executeOnce(primary.get(), "COMMIT");
		const auto persistedRows = scalarUnsigned(control.get(), "SELECT COUNT(*) FROM prs003e_evidence WHERE marker = 'commit-failure'");
		return TransactionFailureEvidence {
			.terminalOperation = commit,
			.mutationAttempts = mutation.attempts,
			.persistedRows = persistedRows,
		};
	}

	[[nodiscard]] TransactionFailureEvidence injectRollbackFailure(const DatabaseConfig &config) {
		Connection primary(config);
		Connection control(config);
		executeRequired(primary.get(), "START TRANSACTION");
		const auto mutation = executeOnce(primary.get(), "INSERT INTO prs003e_evidence(marker) VALUES ('rollback-failure')");
		require(mutation.succeeded, "rollback-failure: setup mutation did not execute");
		killConnection(control.get(), mysql_thread_id(primary.get()));
		const auto rollback = executeOnce(primary.get(), "ROLLBACK");
		const auto persistedRows = scalarUnsigned(control.get(), "SELECT COUNT(*) FROM prs003e_evidence WHERE marker = 'rollback-failure'");
		return TransactionFailureEvidence {
			.terminalOperation = rollback,
			.mutationAttempts = mutation.attempts,
			.persistedRows = persistedRows,
		};
	}

	void verifyMonotonicSequence() {
		DatabaseOutageStateMachine state({ 100ms, 50ms });
		DatabaseOutageEventPublisher publisher(state);
		const auto known = classifyDatabaseRuntimeResult(
			DatabaseRuntimeOperation::Query,
			false,
			DatabaseNativeErrorKind::Other
		);
		const auto unknown = classifyDatabaseRuntimeResult(
			DatabaseRuntimeOperation::TransactionCommit,
			false,
			DatabaseNativeErrorKind::ConnectionLost
		);
		const auto first = publisher.publish(known, 100ms);
		const auto second = publisher.publish(unknown, 110ms);
		require(first.event.has_value() && second.event.has_value(), "sequence: missing publication event");
		require(first.event->eventSequence == 1U, "sequence: first event is not one");
		require(second.event->eventSequence == 2U, "sequence: second event is not two");
		require(first.event->reason == DatabaseOutageEventReason::FirstRuntimeFailure, "sequence: first reason mismatch");
		require(second.event->reason == DatabaseOutageEventReason::UnknownCommitOutcome, "sequence: second reason mismatch");
		require(second.event->after.state == DatabaseOutageState::Draining, "sequence: unknown outcome did not fail closed into draining");
	}

	void prepareDisposableSchema(const DatabaseConfig &config) {
		Connection connection(config);
		executeRequired(
			connection.get(),
			"CREATE TABLE IF NOT EXISTS prs003e_evidence ("
			"id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, "
			"marker VARCHAR(64) NOT NULL UNIQUE"
			") ENGINE=InnoDB"
		);
		executeRequired(connection.get(), "TRUNCATE TABLE prs003e_evidence");
	}

	void runEvidence(const DatabaseConfig &config) {
		prepareDisposableSchema(config);

		Connection ordinaryFailure(config);
		const auto known = executeOnce(ordinaryFailure.get(), "SELECT * FROM prs003e_missing_table");
		require(!known.succeeded, "known-not-committed: missing-table query unexpectedly succeeded");
		require(known.attempts == 1U, "known-not-committed: query attempted more than once");
		verifyPublishedFailure(
			DatabaseRuntimeOperation::Query,
			known.nativeError,
			DatabaseRuntimeResultKind::FailureKnownNotCommitted,
			DatabaseOutageFailureReason::QueryFailed,
			DatabaseOutageCommitOutcome::KnownNotCommitted,
			"known-not-committed"
		);

		const auto interrupted = injectLostThenGone(config);
		require(interrupted.lostAttempts == 1U, "lost-connection: query attempted more than once");
		require(interrupted.goneAttempts == 1U, "server-gone: query attempted more than once");
		require(interrupted.lostError == CR_SERVER_LOST, "lost-connection: expected CR_SERVER_LOST");
		require(interrupted.goneError == CR_SERVER_GONE_ERROR, "server-gone: expected CR_SERVER_GONE_ERROR");
		verifyPublishedFailure(
			DatabaseRuntimeOperation::Query,
			interrupted.lostError,
			DatabaseRuntimeResultKind::FailureUnknownCommitOutcome,
			DatabaseOutageFailureReason::ConnectionLost,
			DatabaseOutageCommitOutcome::Unknown,
			"lost-connection"
		);
		verifyPublishedFailure(
			DatabaseRuntimeOperation::Query,
			interrupted.goneError,
			DatabaseRuntimeResultKind::FailureUnknownCommitOutcome,
			DatabaseOutageFailureReason::ServerGone,
			DatabaseOutageCommitOutcome::Unknown,
			"server-gone"
		);

		const auto begin = injectBeginFailure(config);
		require(!begin.succeeded, "begin-failure: START TRANSACTION unexpectedly succeeded");
		require(begin.attempts == 1U, "begin-failure: START TRANSACTION attempted more than once");
		verifyPublishedFailure(
			DatabaseRuntimeOperation::TransactionBegin,
			begin.nativeError,
			DatabaseRuntimeResultKind::FailureKnownNotCommitted,
			DatabaseOutageFailureReason::TransactionBeginFailed,
			DatabaseOutageCommitOutcome::KnownNotCommitted,
			"begin-failure"
		);

		const auto commit = injectCommitFailure(config);
		require(!commit.terminalOperation.succeeded, "commit-failure: COMMIT unexpectedly succeeded");
		require(commit.terminalOperation.attempts == 1U, "commit-failure: COMMIT attempted more than once");
		require(commit.mutationAttempts == 1U, "commit-failure: mutation was replayed");
		require(commit.persistedRows == 0U, "commit-failure: killed transaction left a persisted row");
		verifyPublishedFailure(
			DatabaseRuntimeOperation::TransactionCommit,
			commit.terminalOperation.nativeError,
			DatabaseRuntimeResultKind::FailureUnknownCommitOutcome,
			DatabaseOutageFailureReason::TransactionCommitFailed,
			DatabaseOutageCommitOutcome::Unknown,
			"commit-failure"
		);

		const auto rollback = injectRollbackFailure(config);
		require(!rollback.terminalOperation.succeeded, "rollback-failure: ROLLBACK unexpectedly succeeded");
		require(rollback.terminalOperation.attempts == 1U, "rollback-failure: ROLLBACK attempted more than once");
		require(rollback.mutationAttempts == 1U, "rollback-failure: mutation was replayed");
		require(rollback.persistedRows == 0U, "rollback-failure: killed transaction left a persisted row");
		verifyPublishedFailure(
			DatabaseRuntimeOperation::TransactionRollback,
			rollback.terminalOperation.nativeError,
			DatabaseRuntimeResultKind::FailureUnknownCommitOutcome,
			DatabaseOutageFailureReason::ConnectionLost,
			DatabaseOutageCommitOutcome::Unknown,
			"rollback-failure"
		);

		verifyMonotonicSequence();

		Connection finalAudit(config);
		require(scalarUnsigned(finalAudit.get(), "SELECT COUNT(*) FROM prs003e_evidence") == 0U, "no-replay: disposable evidence table is not empty");
	}
} // namespace

int main() {
	bool libraryInitialized = false;
	try {
		if (mysql_library_init(0, nullptr, nullptr) != 0) {
			throw std::runtime_error("mysql_library_init failed");
		}
		libraryInitialized = true;
		const auto config = readConfig();
		runEvidence(config);
		mysql_library_end();
		libraryInitialized = false;
		std::cout << "PRS-003E-A disposable MariaDB outage evidence: PASS\n";
		return 0;
	} catch (const std::exception &exception) {
		if (libraryInitialized) {
			mysql_library_end();
		}
		std::cerr << "PRS-003E-A disposable MariaDB outage evidence: FAIL: " << exception.what() << '\n';
		return 1;
	}
}
