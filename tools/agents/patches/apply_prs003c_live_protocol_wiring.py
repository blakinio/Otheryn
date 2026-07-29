from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


login_path = Path("src/server/network/protocol/protocollogin.cpp")
login = login_path.read_text(encoding="utf-8")
login = replace_once(
    login,
    '#include "server/network/protocol/login_protocol_wire.hpp"\n#include "server/network/protocol/protocol_port_utils.hpp"',
    '#include "server/network/protocol/login_protocol_wire.hpp"\n#include "server/network/protocol/database_outage_protocol_admission.hpp"\n#include "server/network/protocol/protocol_port_utils.hpp"',
    "ProtocolLogin include",
)
login = replace_once(
    login,
    '\tif (g_game().getGameState() == GAME_STATE_MAINTAIN) {\n\t\tdisconnectClient("Gameworld is under maintenance.\\nPlease re-connect in a while.");\n\t\treturn;\n\t}\n\n\tBanInfo banInfo;',
    '\tif (g_game().getGameState() == GAME_STATE_MAINTAIN) {\n\t\tdisconnectClient("Gameworld is under maintenance.\\nPlease re-connect in a while.");\n\t\treturn;\n\t}\n\n\tconst auto outageAdmission = DatabaseOutageProtocolAdmission::evaluateAccountLogin(g_game().getGameState());\n\tif (outageAdmission.rejected()) {\n\t\tdisconnectClient(std::string(outageAdmission.message));\n\t\treturn;\n\t}\n\n\tBanInfo banInfo;',
    "ProtocolLogin account admission",
)
login_path.write_text(login, encoding="utf-8")


game_path = Path("src/server/network/protocol/protocolgame.cpp")
game = game_path.read_text(encoding="utf-8")
game = replace_once(
    game,
    '#include "server/network/message/outputmessage.hpp"\n#include "server/network/protocol/protocol_port_utils.hpp"',
    '#include "server/network/message/outputmessage.hpp"\n#include "server/network/protocol/database_outage_protocol_admission.hpp"\n#include "server/network/protocol/protocol_port_utils.hpp"',
    "ProtocolGame include",
)
helper = '''\t[[nodiscard]] std::string getDatabaseOutageAdmissionMessage(const DatabaseOutageProtocolAdmissionResult &admission) {
\t\tif (admission.decision.reason == DatabaseOutageAdmissionReason::LifecycleClosed) {
\t\t\tauto maintainMessage = g_configManager().getString(MAINTAIN_MODE_MESSAGE);
\t\t\tif (!maintainMessage.empty()) {
\t\t\t\treturn maintainMessage;
\t\t\t}
\t\t\treturn std::string(DatabaseOutageProtocolAdmission::ClosedMessage);
\t\t}

\t\treturn std::string(admission.message);
\t}

'''
game = replace_once(
    game,
    '\t[[nodiscard]] bool usesLegacyInnerLength(const ProtocolProfile* profile) {',
    helper + '\t[[nodiscard]] bool usesLegacyInnerLength(const ProtocolProfile* profile) {',
    "ProtocolGame message helper",
)
game = replace_once(
    game,
    '\tg_logger().debug("Player logging in in version \'{}\' and oldProtocol \'{}\'", getVersion(), oldProtocol);\n\n\t// dispatcher thread',
    '\tg_logger().debug("Player logging in in version \'{}\' and oldProtocol \'{}\'", getVersion(), oldProtocol);\n\n\tconst auto gameAdmission = DatabaseOutageProtocolAdmission::evaluateGameLogin(g_game().getGameState());\n\tif (gameAdmission.rejected()) {\n\t\tdisconnectClient(getDatabaseOutageAdmissionMessage(gameAdmission));\n\t\treturn;\n\t}\n\n\t// dispatcher thread',
    "ProtocolGame dispatched login admission",
)
game = replace_once(
    game,
    '\t\tif (foundPlayer->client) {\n\t\t\tfoundPlayer->disconnect();',
    '\t\tif (foundPlayer->client) {\n\t\t\tconst auto handoffAdmission = DatabaseOutageProtocolAdmission::evaluateChannelHandoff(\n\t\t\t\tg_game().getGameState(), foundPlayer->hasFlag(PlayerFlags_t::CanAlwaysLogin)\n\t\t\t);\n\t\t\tif (handoffAdmission.rejected()) {\n\t\t\t\tdisconnectClient(getDatabaseOutageAdmissionMessage(handoffAdmission));\n\t\t\t\treturn;\n\t\t\t}\n\n\t\t\tfoundPlayer->disconnect();',
    "ProtocolGame pre-disconnect handoff admission",
)
game = replace_once(
    game,
    '\tif (isConnectionExpired()) {\n\t\t// ProtocolGame::release() has been called at this point and the Connection object\n\t\t// no longer exists, so we return to prevent leakage of the Player.\n\t\treturn;\n\t}\n\n\tplayer = foundPlayer;',
    '\tif (isConnectionExpired()) {\n\t\t// ProtocolGame::release() has been called at this point and the Connection object\n\t\t// no longer exists, so we return to prevent leakage of the Player.\n\t\treturn;\n\t}\n\n\tconst auto handoffAdmission = DatabaseOutageProtocolAdmission::evaluateChannelHandoff(\n\t\tg_game().getGameState(), foundPlayer->hasFlag(PlayerFlags_t::CanAlwaysLogin)\n\t);\n\tif (handoffAdmission.rejected()) {\n\t\tfoundPlayer->isConnecting = false;\n\t\tdisconnectClient(getDatabaseOutageAdmissionMessage(handoffAdmission));\n\t\treturn;\n\t}\n\n\tplayer = foundPlayer;',
    "ProtocolGame pre-ownership handoff admission",
)
game = replace_once(
    game,
    '\tconst auto &onlinePlayer = g_game().getPlayerByName(characterName);\n\tconst auto &foundPlayer = !onlinePlayer ? g_game().getDeadPlayer(characterName) : onlinePlayer;\n\tif (foundPlayer && foundPlayer->client && accountDescriptor != "@livestream") {\n\t\tif (foundPlayer->isDead()) {',
    '\tconst auto &onlinePlayer = g_game().getPlayerByName(characterName);\n\tconst auto &foundPlayer = !onlinePlayer ? g_game().getDeadPlayer(characterName) : onlinePlayer;\n\tif (foundPlayer && foundPlayer->client && accountDescriptor != "@livestream") {\n\t\tconst auto handoffAdmission = DatabaseOutageProtocolAdmission::evaluateChannelHandoff(\n\t\t\tg_game().getGameState(), foundPlayer->hasFlag(PlayerFlags_t::CanAlwaysLogin)\n\t\t);\n\t\tif (handoffAdmission.rejected()) {\n\t\t\tdisconnectClient(getDatabaseOutageAdmissionMessage(handoffAdmission));\n\t\t\treturn;\n\t\t}\n\n\t\tif (foundPlayer->isDead()) {',
    "ProtocolGame first-message handoff admission",
)
game = replace_once(
    game,
    '\tif (g_game().getGameState() == GAME_STATE_MAINTAIN) {\n\t\tdisconnectClient("Gameworld is under maintenance. Please re-connect in a while.");\n\t\treturn;\n\t}\n\n\tBanInfo banInfo;',
    '\tif (g_game().getGameState() == GAME_STATE_MAINTAIN) {\n\t\tdisconnectClient("Gameworld is under maintenance. Please re-connect in a while.");\n\t\treturn;\n\t}\n\n\tconst auto gameAdmission = DatabaseOutageProtocolAdmission::evaluateGameLogin(g_game().getGameState());\n\tif (gameAdmission.rejected()) {\n\t\tdisconnectClient(getDatabaseOutageAdmissionMessage(gameAdmission));\n\t\treturn;\n\t}\n\n\tBanInfo banInfo;',
    "ProtocolGame world-auth admission",
)
game_path.write_text(game, encoding="utf-8")
