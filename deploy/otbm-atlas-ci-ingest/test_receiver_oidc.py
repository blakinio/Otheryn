from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import time
import unittest


def _load_receiver():
    path = Path(__file__).with_name("receiver.py")
    spec = importlib.util.spec_from_file_location("atlas_ci_receiver_oidc", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


receiver = _load_receiver()
TEST_N = 25152013371876652663244609924042205891038912373879250290295657240716878938940913270469989163495973039061225143732137202915567998556115339430010726183448734836128414534936905856553766975007526742077497659005958575049268405640815090214592684574104699544693019998516033100230260811974787265239208818036853424402289817972989753212169791343891244767755948873549460978185350321545241197615310248071280594960224924502283690173560745081575724561241002623837375116127399916134268948396090836060731837561923427088065128646821050549226345247593598573148184928545923108747959737689199315297015565671767501385284009662011463084619
TEST_E = 65537
TEST_D = 1612849782494035931111974506092548793156400647744442823824213796086373861191375681205275332401419453082301580275787823599686810716573457954355861220164842884917369761860816742636483295122894412829099347116476813275623700729443297932874952422641790131323869211952997987453158842521385530039027954556965935518093443021710666783499558206676515912107925707582352672649545416253033219349820975501642316264788124319431054149521643195776459136670577813344944301439613015776937980006975830285433270401836028859602762165567294768449937865228797020891855950771972146020214984342271502449829564590792809852686302451275043720773


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _uint(value: int) -> str:
    return _b64(value.to_bytes((value.bit_length() + 7) // 8, "big"))


TEST_JWK = {"kid": "test-key", "kty": "RSA", "alg": "RS256", "n": _uint(TEST_N), "e": _uint(TEST_E)}


def _token(claims: dict[str, object]) -> str:
    header = _b64(json.dumps({"alg": "RS256", "kid": "test-key", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _b64(json.dumps(claims, separators=(",", ":")).encode())
    signing_input = f"{header}.{payload}".encode("ascii")
    digest_info = receiver.RSA_SHA256_DIGEST_INFO_PREFIX + hashlib.sha256(signing_input).digest()
    width = (TEST_N.bit_length() + 7) // 8
    encoded = b"\x00\x01" + b"\xff" * (width - len(digest_info) - 3) + b"\x00" + digest_info
    signature = pow(int.from_bytes(encoded, "big"), TEST_D, TEST_N).to_bytes(width, "big")
    return f"{header}.{payload}.{_b64(signature)}"


class GitHubOIDCAuthorizerTests(unittest.TestCase):
    def _authorizer(self):
        target = receiver.GitHubOIDCAuthorizer(
            "blakinio/Otheryn",
            "12345",
            "2",
            "ots-atlas-ci-ingest:12345:2",
            "pull_request",
        )
        target._jwk = lambda kid: TEST_JWK
        return target

    def _claims(self):
        now = int(time.time())
        return {
            "iss": receiver.OIDC_ISSUER,
            "aud": "ots-atlas-ci-ingest:12345:2",
            "iat": now - 2,
            "nbf": now - 2,
            "exp": now + 300,
            "repository": "blakinio/Otheryn",
            "run_id": "12345",
            "run_attempt": "2",
            "event_name": "pull_request",
            "runner_environment": "github-hosted",
        }

    def test_accepts_exact_signed_workflow_identity(self):
        self.assertTrue(self._authorizer().authorized(_token(self._claims())))

    def test_rejects_wrong_run_identity(self):
        claims = self._claims()
        claims["run_id"] = "99999"
        self.assertFalse(self._authorizer().authorized(_token(claims)))

    def test_rejects_wrong_runner_environment(self):
        claims = self._claims()
        claims["runner_environment"] = "self-hosted"
        self.assertFalse(self._authorizer().authorized(_token(claims)))

    def test_rejects_tampered_signature(self):
        token = _token(self._claims())
        header, payload, signature = token.split(".")
        raw = bytearray(receiver._b64url_decode(signature))
        raw[0] ^= 1
        bad = f"{header}.{payload}.{_b64(bytes(raw))}"
        self.assertFalse(self._authorizer().authorized(bad))


if __name__ == "__main__":
    unittest.main()
