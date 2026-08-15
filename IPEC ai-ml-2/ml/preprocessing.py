import logging
from typing import List

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)


def build_preprocessor(num_cols: List[str], cat_cols: List[str]) -> ColumnTransformer:
    """
    Creates an efficient scikit-learn ColumnTransformer pipeline using OrdinalEncoder 
    for categorical features to prevent high-dimensional sparse array memory allocation.
    """
    num_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    cat_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, num_cols),
            ("cat", cat_transformer, cat_cols)
        ],
        remainder="drop"
    )

    return preprocessor


def get_feature_names(preprocessor: ColumnTransformer, num_cols: List[str], cat_cols: List[str]) -> List[str]:
    """
    Extracts transformed feature names.
    """
    return num_cols + cat_cols
