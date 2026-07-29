#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>
#include <string_view>

namespace {
	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(PRS003_SOURCE_DIR) + "/" + relativePath);
		EXPECT_TRUE(input.is_open()) << relativePath;
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}

	void expectContains(const std::string &source, std::string_view needle) {
		EXPECT_NE(source.find(needle), std::string::npos) << needle;
	}

	std::string_view functionBody(const std::string &source, std::string_view begin, std::string_view end) {
		const auto beginPosition = source.find(begin);
		EXPECT_NE(beginPosition, std::string::npos) << begin;
		if (beginPosition == std::string::npos) {
			return {};
		}

		const auto endPosition = source.find(end, beginPosition + begin.size());
		EXPECT_NE(endPosition, std::string::npos) << end;
		if (endPosition == std::string::npos) {
			return {};
		}

		return std::string_view(source).substr(beginPosition, endPosition - beginPosition);
	}

	void expectOrdered(std::string_view source, std::string_view first, std::string_view second) {
		const auto firstPosition = source.find(first);
		const auto secondPosition = source.find(second);
		EXPECT_NE(firstPosition, std::string_view::npos) << first;
		EXPECT_NE(secondPosition, std::string_view::npos) << second;
		if (firstPosition != std::string_view::npos && secondPosition != std::string_view::npos) {
			EXPECT_LT(firstPosition, secondPosition) << first << " must precede " << second;
		}
	}
} // namespace

TEST(Prs003DatabaseOutageContractTest, PreservesFailClosedDatabaseStartup) {
	const auto source = readSource("src/canary_server.cpp");
	const auto initializeDatabase = functionBody(source, "void CanaryServer::initializeDatabase()", "void CanaryServer::loadModules()");

	expectContains(std::string(initializeDatabase), "if (!Database::getInstance().connect())");
	expectContains(std::string(initializeDatabase), "throw FailedToInitializeCanary(\"Failed to connect to database!\")");
	expectContains(std::string(initializeDatabase), "if (!DatabaseManager::updateDatabase())");
	expectContains(std::string(initializeDatabase), "Database migration failed. Server startup aborted.");
}

TEST(Prs003DatabaseOutageContractTest, RecordsOneShotRuntimeFailureWithoutReconnectOrReplay) {
	const auto header = readSource("src/database/database.hpp");
	expectContains(header, "bool retryQuery(std::string_view query, int retries);");
	expectContains(header, "static bool isRecoverableError(unsigned int error);");

	const auto source = readSource("src/database/database.cpp");
	expectContains(source, "bool reconnect = false;");
	expectContains(source, "mysql_options(handle, MYSQL_OPT_RECONNECT, &reconnect);");

	const auto retryQuery = functionBody(source, "bool Database::retryQuery", "bool Database::executeQuery");
	expectContains(std::string(retryQuery), "(void)retries;");
	expectContains(std::string(retryQuery), "mysql_query(handle, query.data())");
	expectContains(std::string(retryQuery), "return false;");
	EXPECT_EQ(retryQuery.find("connect("), std::string_view::npos);
	EXPECT_EQ(retryQuery.find("setGameState"), std::string_view::npos);

	const auto executeQuery = functionBody(source, "bool Database::executeQuery", "DBResult_ptr Database::storeQuery");
	expectContains(std::string(executeQuery), "bool success = retryQuery(query, 10);");
	expectContains(std::string(executeQuery), "return success;");
	EXPECT_EQ(executeQuery.find("setGameState"), std::string_view::npos);

	const auto storeQuery = functionBody(source, "DBResult_ptr Database::storeQuery", "std::string Database::escapeString");
	expectContains(std::string(storeQuery), "MySQL error [{}]");
	expectContains(std::string(storeQuery), "return nullptr;");
	EXPECT_EQ(storeQuery.find("setGameState"), std::string_view::npos);
}

TEST(Prs003DatabaseOutageContractTest, RecordsAsyncDatabaseTasksWithoutCentralOutagePublication) {
	const auto source = readSource("src/database/databasetasks.cpp");
	expectContains(source, "bool success = db.executeQuery(query);");
	expectContains(source, "callback(nullptr, success)");
	expectContains(source, "DBResult_ptr result = db.storeQuery(query);");
	expectContains(source, "callback(result, true)");
	EXPECT_EQ(source.find("setGameState"), std::string::npos);
	EXPECT_EQ(source.find("DatabaseOutage"), std::string::npos);
}

TEST(Prs003DatabaseOutageContractTest, DistinguishesExistingGameLifecycleFromOutageState) {
	const auto definitions = readSource("src/game/game_definitions.hpp");
	expectContains(definitions, "GAME_STATE_NORMAL");
	expectContains(definitions, "GAME_STATE_CLOSED");
	expectContains(definitions, "GAME_STATE_CLOSING");
	expectContains(definitions, "GAME_STATE_MAINTAIN");
	EXPECT_EQ(definitions.find("GAME_STATE_DEGRADED"), std::string::npos);
	EXPECT_EQ(definitions.find("GAME_STATE_DRAINING"), std::string::npos);

	const auto source = readSource("src/game/game.cpp");
	const auto setGameState = functionBody(source, "void Game::setGameState", "void Game::loadItemsPrice");
	expectContains(std::string(setGameState), "case GAME_STATE_SHUTDOWN");
	expectContains(std::string(setGameState), "case GAME_STATE_CLOSED");
	EXPECT_EQ(setGameState.find("Database"), std::string_view::npos);
	EXPECT_EQ(setGameState.find("DEGRADED"), std::string_view::npos);
	EXPECT_EQ(setGameState.find("DRAINING"), std::string_view::npos);
}

TEST(Prs003DatabaseOutageContractTest, RecordsLiveLoginAndHandoffGatesWithoutLifecycleOverload) {
	const auto login = readSource("src/server/network/protocol/protocollogin.cpp");
	expectContains(login, "GAME_STATE_SHUTDOWN");
	expectContains(login, "GAME_STATE_STARTUP");
	expectContains(login, "GAME_STATE_MAINTAIN");
	expectContains(login, "DatabaseOutageProtocolAdmission::evaluateAccountLogin");
	EXPECT_EQ(login.find("GAME_STATE_DEGRADED"), std::string::npos);
	EXPECT_EQ(login.find("GAME_STATE_DRAINING"), std::string::npos);
	expectOrdered(login, "DatabaseOutageProtocolAdmission::evaluateAccountLogin", "IOBan::isIpBanned");
	expectOrdered(login, "DatabaseOutageProtocolAdmission::evaluateAccountLogin", "IOLoginData::authenticateAccount");

	const auto game = readSource("src/server/network/protocol/protocolgame.cpp");
	expectContains(game, "GAME_STATE_SHUTDOWN");
	expectContains(game, "GAME_STATE_STARTUP");
	expectContains(game, "GAME_STATE_MAINTAIN");
	expectContains(game, "GAME_STATE_CLOSING");
	expectContains(game, "GAME_STATE_CLOSED");
	expectContains(game, "DatabaseOutageProtocolAdmission::evaluateGameLogin");
	expectContains(game, "DatabaseOutageProtocolAdmission::evaluateChannelHandoff");
	EXPECT_EQ(game.find("GAME_STATE_DEGRADED"), std::string::npos);
	EXPECT_EQ(game.find("GAME_STATE_DRAINING"), std::string::npos);

	const auto firstMessage = functionBody(game, "void ProtocolGame::onRecvFirstMessage", "void ProtocolGame::sendLoginChallenge");
	expectOrdered(firstMessage, "DatabaseOutageProtocolAdmission::evaluateGameLogin", "IOBan::isIpBanned");
	expectOrdered(firstMessage, "DatabaseOutageProtocolAdmission::evaluateGameLogin", "IOLoginData::gameWorldAuthentication");

	const auto dispatchedLogin = functionBody(game, "void ProtocolGame::login", "void ProtocolGame::connect");
	expectOrdered(dispatchedLogin, "DatabaseOutageProtocolAdmission::evaluateGameLogin", "IOLoginData::preloadPlayer");
	expectOrdered(dispatchedLogin, "DatabaseOutageProtocolAdmission::evaluateChannelHandoff", "foundPlayer->disconnect()");

	const auto connect = functionBody(game, "void ProtocolGame::connect", "void ProtocolGame::onConnect");
	expectOrdered(connect, "DatabaseOutageProtocolAdmission::evaluateChannelHandoff", "player = foundPlayer");
}

TEST(Prs003DatabaseOutageContractTest, RecordsBoundedFailClosedTargetAndImplementationSequence) {
	const auto contract = readSource("docs/architecture/prs-003-database-outage-state-machine-contract.md");
	expectContains(contract, "HEALTHY");
	expectContains(contract, "DEGRADED");
	expectContains(contract, "DRAINING");
	expectContains(contract, "MAINTENANCE");
	expectContains(contract, "The first qualifying runtime persistence failure with a known-not-committed outcome enters `DEGRADED`");
	expectContains(contract, "A failure with unknown commit outcome enters `DRAINING` directly.");
	expectContains(contract, "repeated failures never extend or reset the original degraded deadline");
	expectContains(contract, "It cannot return directly to `HEALTHY`.");
	expectContains(contract, "A successful ordinary gameplay query is not a health probe.");
	expectContains(contract, "Slice A — pure state machine");
	expectContains(contract, "Do not wire it into `Database`, protocols or gameplay in the same slice.");
	expectContains(contract, "PRS-004 session/revision fencing");
	expectContains(contract, "automatic database promotion");
}
