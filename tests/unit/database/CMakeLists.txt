target_sources(
    canary_ut
    PRIVATE database_outage_state_test.cpp databasemanager_test.cpp
            session_revision_fence_test.cpp
)
