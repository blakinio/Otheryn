target_sources(
    canary_ut
    PRIVATE network/message/networkmessage_test.cpp
            network/protocol/multiprotocol_test.cpp
            network/protocol/oam_044_protocol_compatibility_test.cpp
)
