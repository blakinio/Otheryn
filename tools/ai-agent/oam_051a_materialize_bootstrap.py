#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

script_path = Path("tools/ai-agent/oam_051a_materialize.py")
source = script_path.read_text(encoding="utf-8")
old = '''patch_path = Path("/tmp/oam-051a-selected.patch")
patch = subprocess.run(
    ["git", "diff", "--binary", parent, donor, "--", *SELECTED_DONOR_PATHS],
    check=True,
    stdout=subprocess.PIPE,
).stdout
patch_path.write_bytes(patch)
run("git", "apply", "--3way", str(patch_path))
'''
new = '''non_player_paths = [path for path in SELECTED_DONOR_PATHS if not path.endswith("player_wheel.cpp")]
patch_path = Path("/tmp/oam-051a-selected.patch")
patch = subprocess.run(
    ["git", "diff", "--binary", parent, donor, "--", *non_player_paths],
    check=True,
    stdout=subprocess.PIPE,
).stdout
patch_path.write_bytes(patch)
run("git", "apply", "--3way", str(patch_path))

player_patch_path = Path("/tmp/oam-051a-player-wheel.patch")
player_patch = subprocess.run(
    ["git", "diff", "--binary", parent, donor, "--", "src/creatures/players/components/wheel/player_wheel.cpp"],
    check=True,
    stdout=subprocess.PIPE,
).stdout
player_patch_path.write_bytes(player_patch)
player_apply = subprocess.run(
    ["git", "apply", "--reject", "--whitespace=nowarn", str(player_patch_path)],
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)
print(player_apply.stdout, end="")
if player_apply.returncode != 0:
    rejects = sorted(Path(".").rglob("*.rej"))
    expected_reject = Path("src/creatures/players/components/wheel/player_wheel.cpp.rej")
    if rejects != [expected_reject]:
        for reject in rejects:
            print(f"--- UNEXPECTED REJECT {reject} ---")
            print(reject.read_text(encoding="utf-8"))
        raise RuntimeError(f"unexpected selective patch rejects: {rejects}")

    reject_text = expected_reject.read_text(encoding="utf-8")
    if "void PlayerWheel::destroyGem" not in reject_text or "void PlayerWheel::setActiveGem" not in reject_text:
        raise RuntimeError("unexpected player_wheel.cpp rejected hunk content")

    replace_once(
        "src/creatures/players/components/wheel/player_wheel.cpp",
        """\tm_destroyedGems.emplace_back(gem);
\tm_revealedGems.erase(m_revealedGems.begin() + index);

\tconst auto totalLesserFragment = m_player.getItemTypeCount(ITEM_LESSER_FRAGMENT) + m_player.getStashItemCount(ITEM_LESSER_FRAGMENT);
\tconst auto totalGreaterFragment = m_player.getItemTypeCount(ITEM_GREATER_FRAGMENT) + m_player.getStashItemCount(ITEM_GREATER_FRAGMENT);

\tm_player.client->sendResourceBalance(RESOURCE_LESSER_FRAGMENT, totalLesserFragment);
\tm_player.client->sendResourceBalance(RESOURCE_GREATER_FRAGMENT, totalGreaterFragment);

\tsendOpenWheelWindow(m_player.getID());
}""",
        """\tconst auto destroyedGemUuid = gem.uuid;
\tm_destroyedGems.emplace_back(gem);
\tgem.remove(gemsKV());

\tbool removedActiveGem = false;
\tfor (const auto affinity : magic_enum::enum_values<WheelGemAffinity_t>()) {
\t\tconst auto affinityIndex = static_cast<uint8_t>(affinity);
\t\tconst auto &activeGem = m_activeGems[affinityIndex];
\t\tif (!activeGem || activeGem.uuid != destroyedGemUuid) {
\t\t\tcontinue;
\t\t}

\t\tremoveActiveGem(affinity);
\t\tgemsKV()->scoped("active")->remove(std::string(magic_enum::enum_name(affinity)));
\t\tremovedActiveGem = true;
\t}

\tm_revealedGems.erase(m_revealedGems.begin() + index);
\tif (removedActiveGem) {
\t\tloadPlayerBonusData();
\t}

\tconst auto totalLesserFragment = m_player.getItemTypeCount(ITEM_LESSER_FRAGMENT) + m_player.getStashItemCount(ITEM_LESSER_FRAGMENT);
\tconst auto totalGreaterFragment = m_player.getItemTypeCount(ITEM_GREATER_FRAGMENT) + m_player.getStashItemCount(ITEM_GREATER_FRAGMENT);

\tif (m_player.client) {
\t\tm_player.client->sendResourceBalance(RESOURCE_LESSER_FRAGMENT, totalLesserFragment);
\t\tm_player.client->sendResourceBalance(RESOURCE_GREATER_FRAGMENT, totalGreaterFragment);
\t}

\tsendOpenWheelWindow(m_player.getID());
}""",
    )
    replace_once(
        "src/creatures/players/components/wheel/player_wheel.cpp",
        """void PlayerWheel::switchGemDomain(uint16_t index) {
\tauto &gem = getGem(index);
\tif (!gem) {
\t\treturn;
\t}

\tif (gem.locked) {
\t\tg_logger().error("[{}] Player {} trying to destroy locked gem with index {}", __FUNCTION__, m_player.getName(), index);
\t\treturn;
\t}
\tauto goldCost = getGemRotateCost(gem.quality);
\tif (!g_game().removeMoney(m_player.getPlayer(), goldCost, 0, true)) {
\t\tg_logger().error("[{}] Failed to remove {} gold from player with name {}", __FUNCTION__, goldCost, m_player.getName());
\t\treturn;
\t}

\tauto gemAffinity = convertWheelGemAffinityToDomain(static_cast<uint8_t>(gem.affinity));
\tgem.affinity = static_cast<WheelGemAffinity_t>(gemAffinity);
\tsendOpenWheelWindow(m_player.getID());
}

void PlayerWheel::toggleGemLock(uint16_t index) {
\tauto &gem = getGem(index);
\tif (!gem) {
\t\treturn;
\t}
\tgem.locked = !gem.locked;
\tsendOpenWheelWindow(m_player.getID());
}""",
        """void PlayerWheel::switchGemDomain(uint16_t index) {
\tif (!canOpenWheel()) {
\t\treturn;
\t}

\tauto &gem = getGem(index);
\tif (!gem) {
\t\treturn;
\t}

\tif (gem.locked) {
\t\tg_logger().error("[{}] Player {} tried to rotate locked gem with index {}", __FUNCTION__, m_player.getName(), index);
\t\treturn;
\t}

\tconst uint64_t goldCost = getGemRotateCost(gem.quality);
\tif (goldCost == 0 || !g_game().removeMoney(m_player.getPlayer(), goldCost, 0, true)) {
\t\tg_logger().error("[{}] Failed to remove {} gold from player {}", __FUNCTION__, goldCost, m_player.getName());
\t\treturn;
\t}

\tbool removedActiveGem = false;
\tfor (const auto affinity : magic_enum::enum_values<WheelGemAffinity_t>()) {
\t\tconst auto affinityIndex = static_cast<uint8_t>(affinity);
\t\tconst auto &activeGem = m_activeGems[affinityIndex];
\t\tif (!activeGem || activeGem.uuid != gem.uuid) {
\t\t\tcontinue;
\t\t}

\t\tremoveActiveGem(affinity);
\t\tgemsKV()->scoped("active")->remove(std::string(magic_enum::enum_name(affinity)));
\t\tremovedActiveGem = true;
\t}

\tgem.affinity = static_cast<WheelGemAffinity_t>(convertWheelGemAffinityToDomain(static_cast<uint8_t>(gem.affinity)));
\tgem.save(gemsKV());
\tif (removedActiveGem) {
\t\tloadPlayerBonusData();
\t}

\tsendOpenWheelWindow(m_player.getID());
}

void PlayerWheel::toggleGemLock(uint16_t index) {
\tif (!canOpenWheel()) {
\t\treturn;
\t}

\tauto &gem = getGem(index);
\tif (!gem) {
\t\treturn;
\t}
\tgem.locked = !gem.locked;
\tsendOpenWheelWindow(m_player.getID());
}""",
    )
    # The second rejected donor hunk removes an unsafe state clear that Otheryn
    # already does not contain, so no target edit is required for that hunk.
    expected_reject.unlink()
'''
if source.count(old) != 1:
    raise RuntimeError(f"expected one materializer patch anchor, found {source.count(old)}")
modified = source.replace(old, new, 1)
exec(compile(modified, str(script_path), "exec"), {"__name__": "__main__", "__file__": str(script_path)})
