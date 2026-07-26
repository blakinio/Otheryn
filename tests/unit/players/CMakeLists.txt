target_sources(
    canary_ut
    PRIVATE player_item_batch_test.cpp reward_iteration_test.cpp
)

add_subdirectory(components)
add_subdirectory(condition)
add_subdirectory(imbuements)

target_compile_definitions(
    canary_ut
    PRIVATE OAM051_SOURCE_DIR="${PROJECT_SOURCE_DIR}"
)

target_sources(
    canary_ut
    PRIVATE character_progression_test.cpp
            forge_effect_policy_test.cpp
            forge_test.cpp
            forge_transaction_test.cpp
            oam_020_exaltation_forge_adapt_test.cpp
            oam_051_wheel_safety_adapt_test.cpp
            oam_051b_task_shop_adapt_test.cpp
            party_test.cpp
            vocation_test.cpp
)
