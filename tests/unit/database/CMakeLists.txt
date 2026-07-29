target_sources(
    canary_ut
    PRIVATE database_failure_classification_test.cpp
            database_outage_state_test.cpp
            databasemanager_test.cpp
            session_revision_fence_test.cpp
)

target_compile_definitions(
    canary_ut
    PRIVATE PRS003B_SOURCE_DIR="${PROJECT_SOURCE_DIR}"
)
