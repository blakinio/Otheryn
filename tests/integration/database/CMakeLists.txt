target_sources(
    canary_it
    PRIVATE ${CMAKE_SOURCE_DIR}/src/database/player_writer_fence_repository.cpp
  database_migrations_it.cpp
  player_checkpoint_commit_before_ack_crash_it.cpp
  player_checkpoint_kv_post_commit_failure_it.cpp
  player_checkpoint_sql_failure_it.cpp
  player_writer_fence_repository_it.cpp
  player_writer_fenced_save_it.cpp
  sanctions_it.cpp
  world_persistence_it.cpp
)
