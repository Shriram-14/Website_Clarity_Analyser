"""Streamlit-specific helpers (keeps imported ``st.secrets`` out of domain modules)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


def streamlit_secrets_or_none() -> Mapping[str, Any] | None:
    """
    Return a plain mapping of secrets if Streamlit loaded ``secrets.toml``.

    Returning the raw ``st.secrets`` object is unsafe: operators like ``in`` lazy-load the
    file and raise ``StreamlitSecretNotFoundError`` when no secrets file exists, which
    would break setups that rely on ``.env`` only.
    """
    try:
        # Iteration/materialization triggers Streamlit's parse and fails cleanly without a file.
        return {key: st.secrets[key] for key in st.secrets}
    except StreamlitSecretNotFoundError:
        return None
    except KeyError:
        return None
    except Exception:
        return None
