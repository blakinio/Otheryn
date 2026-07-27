target_sources(
    canary_ut
    PRIVATE network/message/networkmessage_test.cpp
            network/protocol/multiprotocol_test.cpp
            network/protocol/oam_044_protocol_compatibility_test.cpp
            network/protocol/oam_045_protocol_session_handoff_test.cpp
            network/protocol/oam_053_network_transport_test.cpp
            network/protocol/oam_054_login_protocol_test.cpp
)
