target_sources(
    canary_ut
    PRIVATE player_item_batch_test.cpp reward_iteration_test.cpp
)

add_subdirectory(components)
add_subdirectory(condition)
add_subdirectory(imbuements)

target_sources(
    canary_ut
    PRIVATE character_progression_test.cpp
            forge_effect_policy_test.cpp
            forge_test.cpp
            forge_transaction_test.cpp
            party_test.cpp
            vocation_test.cpp
)
