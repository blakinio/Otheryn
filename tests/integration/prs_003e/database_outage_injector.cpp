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
		const auto parsedPort = std::stoul(requiredEnvironment("PRS003E_DB_PORT"));
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

	[[nodiscard]] DatabaseOutageFailureReason nativeFailureReason(unsigned int nativeError) {
		return nativeError == CR_SERVER_GONE_ERROR
			? DatabaseOutageFailureReason::ServerGone
			: DatabaseOutageFailureReason::ConnectionLost;
	}

	[[nodiscard]] DatabaseOutageEventReason initialEventReason(DatabaseRuntimeResultKind result) {
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

		DatabaseOutageStateMachine state({ 100ms, 50ms });
		DatabaseOutageEventPublisher publisher(state);
		const auto publication = publisher.publish(classification, 100ms);
		require(publication.event.has_value(), std::string(label) + ": publication did not emit an event");
		require(publication.event->eventSequence == 1U, std::string(label) + ": first event sequence is not one");
		require(publication.event->eventTime == 100ms, std::string(label) + ": event time mismatch");
		require(publication.event->disposition == DatabaseOutageEventDisposition::Applied, std::string(label) + ": event was not applied");
		require(publication.event->reason == initialEventReason(expectedResult), std::string(label) + ": event reason mismatch");
		require(publication.event->after.lastFailureReason == expectedFailureReason, std::string(label) + ": snapshot reason mismatch");
		require(publication.event->after.lastFailureOutcome == expectedOutcome, std::string(label) + ": snapshot outcome mismatch");

		DatabaseOutageStateMachine callerState({ 100ms, 50ms });
		DatabaseOutageEventPublisher callerPublisher(callerState);
		require(!callerPublisher.publishAndPreserve(false, classification, 100ms), std::string(label) + ": caller failure became success");
	}

	struct InterruptedConnectionEvidence final {
		OperationEvidence lost;
		OperationEvidence gone;
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
				evidence.lost = executeOnce(primary.get(), "SELECT SLEEP(30)");
				evidence.gone = executeOnce(primary.get(), "SELECT 1");
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

	[[nodiscard]] TransactionFailureEvidence injectTransactionFailure(
		const DatabaseConfig &config,
		std::string_view marker,
		std::string_view terminalSql
	) {
		Connection primary(config);
		Connection control(config);
		executeRequired(primary.get(), "START TRANSACTION");
		const auto mutation = executeOnce(
			primary.get(),
			"INSERT INTO prs003e_evidence(marker) VALUES ('" + std::string(marker) + "')"
		);
		require(mutation.succeeded, std::string(marker) + ": setup mutation did not execute");
		killConnection(control.get(), mysql_thread_id(primary.get()));
		const auto terminal = executeOnce(primary.get(), terminalSql);
		const auto rows = scalarUnsigned(
			control.get(),
			"SELECT COUNT(*) FROM prs003e_evidence WHERE marker = '" + std::string(marker) + "'"
		);
		return TransactionFailureEvidence {
			.terminalOperation = terminal,
			.mutationAttempts = mutation.attempts,
			.persistedRows = rows,
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

	void verifyTransactionEvidence(const TransactionFailureEvidence &evidence, std::string_view label) {
		require(!evidence.terminalOperation.succeeded, std::string(label) + ": terminal operation unexpectedly succeeded");
		require(evidence.terminalOperation.attempts == 1U, std::string(label) + ": terminal operation attempted more than once");
		require(evidence.mutationAttempts == 1U, std::string(label) + ": mutation was replayed");
		require(evidence.persistedRows == 0U, std::string(label) + ": killed transaction left a persisted row");
	}

	void runEvidence(const DatabaseConfig &config) {
		prepareDisposableSchema(config);

		Connection ordinaryFailure(config);
		const auto known = executeOnce(ordinaryFailure.get(), "SELECT * FROM prs003e_missing_table");
		require(!known.succeeded && known.attempts == 1U, "known-not-committed: one-shot query evidence mismatch");
		verifyPublishedFailure(
			DatabaseRuntimeOperation::Query,
			known.nativeError,
			DatabaseRuntimeResultKind::FailureKnownNotCommitted,
			DatabaseOutageFailureReason::QueryFailed,
			DatabaseOutageCommitOutcome::KnownNotCommitted,
			"known-not-committed"
		);

		const auto interrupted = injectLostThenGone(config);
		require(interrupted.lost.attempts == 1U, "lost-connection: query attempted more than once");
		require(interrupted.gone.attempts == 1U, "server-gone: query attempted more than once");
		require(interrupted.lost.nativeError == CR_SERVER_LOST, "lost-connection: expected CR_SERVER_LOST");
		require(interrupted.gone.nativeError == CR_SERVER_GONE_ERROR, "server-gone: expected CR_SERVER_GONE_ERROR");
		verifyPublishedFailure(
			DatabaseRuntimeOperation::Query,
			interrupted.lost.nativeError,
			DatabaseRuntimeResultKind::FailureUnknownCommitOutcome,
			DatabaseOutageFailureReason::ConnectionLost,
			DatabaseOutageCommitOutcome::Unknown,
			"lost-connection"
		);
		verifyPublishedFailure(
			DatabaseRuntimeOperation::Query,
			interrupted.gone.nativeError,
			DatabaseRuntimeResultKind::FailureUnknownCommitOutcome,
			DatabaseOutageFailureReason::ServerGone,
			DatabaseOutageCommitOutcome::Unknown,
			"server-gone"
		);

		const auto begin = injectBeginFailure(config);
		require(!begin.succeeded && begin.attempts == 1U, "begin-failure: one-shot begin evidence mismatch");
		verifyPublishedFailure(
			DatabaseRuntimeOperation::TransactionBegin,
			begin.nativeError,
			DatabaseRuntimeResultKind::FailureKnownNotCommitted,
			DatabaseOutageFailureReason::TransactionBeginFailed,
			DatabaseOutageCommitOutcome::KnownNotCommitted,
			"begin-failure"
		);

		const auto commit = injectTransactionFailure(config, "commit-failure", "COMMIT");
		verifyTransactionEvidence(commit, "commit-failure");
		verifyPublishedFailure(
			DatabaseRuntimeOperation::TransactionCommit,
			commit.terminalOperation.nativeError,
			DatabaseRuntimeResultKind::FailureUnknownCommitOutcome,
			DatabaseOutageFailureReason::TransactionCommitFailed,
			DatabaseOutageCommitOutcome::Unknown,
			"commit-failure"
		);

		const auto rollback = injectTransactionFailure(config, "rollback-failure", "ROLLBACK");
		verifyTransactionEvidence(rollback, "rollback-failure");
		require(
			rollback.terminalOperation.nativeError == CR_SERVER_LOST || rollback.terminalOperation.nativeError == CR_SERVER_GONE_ERROR,
			"rollback-failure: expected a connection failure"
		);
		verifyPublishedFailure(
			DatabaseRuntimeOperation::TransactionRollback,
			rollback.terminalOperation.nativeError,
			DatabaseRuntimeResultKind::FailureUnknownCommitOutcome,
			nativeFailureReason(rollback.terminalOperation.nativeError),
			DatabaseOutageCommitOutcome::Unknown,
			"rollback-failure"
		);

		verifyMonotonicSequence();
		Connection finalAudit(config);
		require(scalarUnsigned(finalAudit.get(), "SELECT COUNT(*) FROM prs003e_evidence") == 0U, "no-replay: evidence table is not empty");
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
