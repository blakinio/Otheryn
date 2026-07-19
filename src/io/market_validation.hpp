#pragma once

#ifndef USE_PRECOMPILED_HEADERS
	#include <charconv>
	#include <cstdint>
	#include <optional>
	#include <string_view>
#endif

namespace MarketValidation {

	[[nodiscard]] constexpr uint16_t offerCounter(uint32_t offerId) noexcept {
		return static_cast<uint16_t>((offerId ^ 0x00ABCDEFU) & 0xFFFFU);
	}

	[[nodiscard]] constexpr std::optional<uint32_t> offerCreatedAt(uint32_t clientTimestamp, int32_t offerDuration) noexcept {
		if (offerDuration < 0) {
			return std::nullopt;
		}

		const auto duration = static_cast<uint32_t>(offerDuration);
		if (clientTimestamp < duration) {
			return std::nullopt;
		}

		return clientTimestamp - duration;
	}

	[[nodiscard]] inline std::optional<uint8_t> parseTier(std::string_view value, int64_t maxTier) noexcept {
		if (value.empty() || maxTier < 0) {
			return std::nullopt;
		}

		uint32_t parsed = 0;
		const auto [ptr, error] = std::from_chars(value.data(), value.data() + value.size(), parsed);
		if (error != std::errc {} || ptr != value.data() + value.size()) {
			return std::nullopt;
		}

		if (parsed > UINT8_MAX || parsed > static_cast<uint64_t>(maxTier)) {
			return std::nullopt;
		}

		return static_cast<uint8_t>(parsed);
	}

} // namespace MarketValidation
