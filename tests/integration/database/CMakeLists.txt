target_sources(
    canary_it
    PRIVATE database_migrations_it.cpp
            player_checkpoint_commit_before_ack_crash_it.cpp
            player_checkpoint_kv_post_commit_failure_it.cpp
            player_checkpoint_sql_failure_it.cpp
            sanctions_it.cpp
            world_persistence_it.cpp
)
