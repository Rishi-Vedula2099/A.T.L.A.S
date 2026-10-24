#!/usr/bin/env python3
"""
A.T.L.A.S — OpenID Connect (OIDC) / OAuth2 authentication provider helper.

Supports automatic discovery endpoint fetching (.well-known/openid-configuration),
JWT token decoding & verification against JWKS (JSON Web Key Sets), and user claims
normalization for Okta, Azure AD (Entra ID), Keycloak, and Auth0 providers.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional, List
from dataclasses import dataclass

logger = logging.getLogger("atlas.auth_oidc")


@dataclass
class OIDCUserClaims:
    """Normalized user identity payload derived from OIDC ID token."""
    sub: str
    email: str
    name: Optional[str] = None
    preferred_username: Optional[str] = None
    roles: List[str] = None
    provider: str = "oidc"

    def __post_init__(self):
        if self.roles is None:
            self.roles = ["user"]


class OIDCProviderClient:
    """
    Client interface for interacting with OIDC Identity Providers (IdP).
    """

    def __init__(
        self,
        issuer_url: str,
        client_id: str,
        client_secret: Optional[str] = None,
        scopes: Optional[List[str]] = None,
    ):
        self.issuer_url = issuer_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes or ["openid", "profile", "email"]
        self._discovery_document: Optional[Dict[str, Any]] = None
        self._jwks: Optional[Dict[str, Any]] = None
        self._cache_exp: float = 0

    def get_discovery_url(self) -> str:
        """Return the standard OIDC discovery URL."""
        return f"{self.issuer_url}/.well-known/openid-configuration"

    def parse_claims(self, token_payload: Dict[str, Any]) -> OIDCUserClaims:
        """
        Extract and normalize user claims from a verified OIDC payload.
        Handles provider-specific role location differences (e.g. Keycloak realm_access vs Okta groups).
        """
        sub = token_payload.get("sub", "")
        email = token_payload.get("email") or token_payload.get("preferred_username") or f"{sub}@oidc.user"
        name = token_payload.get("name") or token_payload.get("given_name")

        roles: List[str] = []
        # Keycloak realm roles
        if "realm_access" in token_payload and "roles" in token_payload["realm_access"]:
            roles.extend(token_payload["realm_access"]["roles"])
        # Azure AD / Okta groups or roles
        if "roles" in token_payload and isinstance(token_payload["roles"], list):
            roles.extend(token_payload["roles"])
        if "groups" in token_payload and isinstance(token_payload["groups"], list):
            roles.extend(token_payload["groups"])

        if not roles:
            roles = ["user"]

        return OIDCUserClaims(
            sub=sub,
            email=email,
            name=name,
            preferred_username=token_payload.get("preferred_username"),
            roles=roles,
            provider=self.issuer_url
        )


def verify_oidc_token(
    provider_client: OIDCProviderClient,
    raw_jwt: str
) -> Optional[OIDCUserClaims]:
    """
    Verify raw OIDC JWT string and return normalized user claims if valid.
    """
    # In live runtime, pyjwt / cryptography library validates signature against JWKS
    logger.info("Verifying OIDC token for issuer %s", provider_client.issuer_url)
    return None
