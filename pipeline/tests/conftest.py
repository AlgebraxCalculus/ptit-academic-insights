from __future__ import annotations

import pytest

import s1_ingest
import s2_clean
import s3_scope


@pytest.fixture(scope="session")
def raw_df():
    df, _warnings, _sha = s1_ingest.ingest()
    return df


@pytest.fixture(scope="session")
def clean_df(raw_df):
    return s2_clean.clean(raw_df)


@pytest.fixture(scope="session")
def scoped_df(clean_df):
    return s3_scope.scope_and_derive(clean_df)
