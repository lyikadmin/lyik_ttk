import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Annotated
from typing_extensions import Doc

import apluggy as pluggy
import jwt
import jwt.exceptions
from lyikpluginmanager import (
    getProjectName,
    AuthProviderSpec,
    LyikTokenSpec,
    AuthorizationRequestModel,
    ContextModel,
    PluginException,
)
from lyikpluginmanager import invoke
from lyikpluginmanager.models import (
    IAMUserMetadata,
    IAMUserIdentifiers,
    PreAuthorizedInfoModel,
)
from lyikpluginmanager.annotation import RequiredEnv
import apluggy as pluggy
from typing import Dict, List, Optional, Any

import jwt
from jwt import PyJWKClient

from pydantic import BaseModel
from lyikpluginmanager import (
    getProjectName,
    AuthProviderSpec,
    ContextModel,
    PluginException,
)

impl = pluggy.HookimplMarker(getProjectName())

TTK_DEFAULT_DOMAIN = "https://auth.ttk.com/"  # e.g. https://auth.TTK.com
TTK_DEFAULT_AUDIENCE = (
    "https://lyik.com"  # LYIK audience / client‑id expected in TTK tokens
)
TTK_DEFAULT_ALGORITHMS = ["RS256"]  # supported signing algorithms
JWKS_PATH = "/.well-known/jwks.json"  # standard OIDC path


def _get_cfg_attr(cfg: Any, name: str, dflt: Any) -> Any:
    """Utility to pick attribute from config or fall back to default."""
    return getattr(cfg, name, dflt) if cfg is not None else dflt


def _get_jwk_client(domain: str) -> PyJWKClient:
    """Return an initialized PyJWKClient for the given domain."""
    return PyJWKClient(f"https://{domain}{JWKS_PATH}")


class TTKAuthProvider(AuthProviderSpec):
    """AuthProvider plugin implementation for TTK Customer SSO tokens.

    The plugin validates TTK-issued JWTs and converts them into LYIK-compatible
    information objects used for downstream authorization and token creation.
    """

    @impl
    async def isValidToken(
        self, 
        token: Annotated[str, Doc("Token to validate")]
        ) -> Annotated[
            bool, 
            Doc("Indicates if the token is valid")]:  # type: ignore[override]
        """Lightweight inspection (no signature verification) to decide if the
        token appears to come from TTK. Returns **False** if it clearly does not.
        """
        try:
            unverified: Dict = jwt.decode(
                token,
                options={"verify_signature": False},
                algorithms=["HS256", "RS256", "ES256"],
            )
            iss: str | None = unverified.get("iss")
            return bool(iss and TTK_DEFAULT_DOMAIN in iss)
        except Exception:
            return False

    @impl
    async def verifyToken(
        self,
        context: ContextModel | None,
        token: Annotated[str, Doc("Token to verify")],
    ) -> Annotated[
        dict,
        RequiredEnv(["LYIK_TOKEN_PUBLIC_KEY"]),
        Doc("Decoded jwt payload"),
    ]:
        """
        This function verifies token and returns payload
        """
        if context is None:
            raise PluginException("context must be provided")
        if context.config is None:
            raise PluginException("config must be provided in the context")

        lyik_public_key_pem = os.getenv("LYIK_TOKEN_PUBLIC_KEY")

        cfg = context.config
        algorithms = ["RS256"]
        domain = TTK_DEFAULT_DOMAIN
        audience = TTK_DEFAULT_AUDIENCE

        try:
            payload: Dict = jwt.decode(
                jwt=token,
                key=lyik_public_key_pem,
                algorithms=algorithms,
                audience=audience,
                issuer=domain,
            )
            return payload
        except jwt.exceptions.ImmatureSignatureError:
            payload: Dict = jwt.decode(
                jwt=token,
                key=lyik_public_key_pem,
                algorithms=algorithms,
                audience=audience,
                issuer=domain,
                options={"verify_iat": False, "verify_nbf": False},
            )
            return payload
        except Exception as ex:
            raise PluginException(f"Token verification failed - {ex}") from ex

    @impl
    async def getPreAuthorizedInformation(
        self,
        token: Annotated[str, Doc("Token to retrieve pre-authorized information from")],
    ) -> Annotated[
        PreAuthorizedInfoModel,
        Doc("Retrieve pre-authorized information from the token"),
    ]:
        """
        Decode the incoming SSO token, extract sub, roles, and governed_users,
        and return a PreAuthorizedInfoModel.
        """
        if not token:
            raise PluginException("No token provided")

        try:
            # Verify signature / audience / issuer
            public_key = os.getenv("LYIK_TOKEN_PUBLIC_KEY")
            payload = jwt.decode(
                token,
                key=public_key,
                algorithms=["RS256"],
                audience=[TTK_DEFAULT_AUDIENCE],
                issuer=TTK_DEFAULT_DOMAIN,
            )
        except Exception as e:
            raise PluginException(f"Invalid pre-auth token: {e}")

        # Pull out the fields you need
        user_id = payload.get("user_id")
        roles = payload.get("roles", [])
        governed_users = payload.get("relationship", [])
        user_name = payload.get("name")
        if not user_id:
            raise PluginException("No user_id found in token")

        # Build your Pydantic model
        return PreAuthorizedInfoModel(
            user_id=user_id,
            roles=roles,
            governed_users=governed_users,
            user_name=user_name,
        )

    @impl
    async def getSubject(self, payload: Dict):  # type: ignore[override]
        return payload.get("sub") or payload.get("user_id")

    @impl
    async def getUserId(self, payload: Dict):  # type: ignore[override]
        uid = payload.get("user_id") or payload.get("sub")
        return {"user_id": uid} if uid else None

    @impl
    async def isOwnerOf(self, payload: Dict):  # type: ignore[override]
        return bool(payload.get("relationship"))

    @impl
    async def getOwnerOf(self, payload: Dict):  # type: ignore[override]
        return payload.get("relationship", [])

    @impl
    async def getPhoneNumber(self, payload: Dict):  # type: ignore[override]
        phone = payload.get("phone_number")
        return {"phone_number": phone} if phone else None

    @impl
    async def getEmail(self, payload: Dict):  # type: ignore[override]
        email = payload.get("email")
        return {"email": email} if email else None
