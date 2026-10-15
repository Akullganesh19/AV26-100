from __future__ import annotations

import json
import joblib
import pandas as pd
import numpy as np
import asyncio
import logging
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import UUID

import shap
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.config import settings
from app.ml.features import FeatureBuilder, FEATURE_NAMES
from app.models.prediction import Prediction, RiskTier
from app.schemas.prediction import PredictionResponse
from app.tasks.alerts import send_alert_notification

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).parent.parent.parent / "models"
MANIFEST_PATH = MODELS_DIR / "latest.json"

TIER_LABELS = {0: RiskTier.LOW, 1: RiskTier.MEDIUM, 2: RiskTier.HIGH, 3: RiskTier.CRITICAL}


def to_python(val: Any) -> Any:
    """Cast numpy scalars to native Python types. Pydantic v2 rejects numpy types."""
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, np.ndarray):
        return val.tolist()
    return val


def get_latest_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        raise RuntimeError(
            f"Model manifest not found at {MANIFEST_PATH}. "
            "Run train.py before starting the server."
        )
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    required_keys = {"version", "pipeline", "regressor", "classifier", "explainer", "feature_bounds"}
    missing = required_keys - set(manifest.keys())
    if missing:
        raise RuntimeError(f"Manifest missing required keys: {missing}")

    return manifest


def load_artifacts() -> dict:
    """
    Load all ML artifacts from disk. Called once at app startup.
    Raises RuntimeError if any artifact is missing or corrupt — this is intentional.
    A server without models must not start silently.
    """
    manifest = get_latest_manifest()

    artifacts = {"manifest": manifest}
    for key in ("pipeline", "regressor", "classifier", "explainer"):
        path = MODELS_DIR / manifest[key]
        if not Path(path).exists():
            raise RuntimeError(f"Artifact not found: {path}")
        logger.info(f"Loading {key} from {path}")
        artifacts[key] = joblib.load(path)

    logger.info(f"ML artifacts loaded. Model version: {manifest['version']}")
    return artifacts


# Module-level state — populated by lifespan, shared across all requests
ml_state: dict = {}
background_tasks = set()


class PredictionService:
    """
    Single entry point for all inference — both on-demand (/api/v1/predict)
    and scheduled batch runs. Never instantiate per-request; share the module-level
    ml_state artifacts across all calls.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.pipeline = ml_state["pipeline"]
        self.regressor = ml_state["regressor"]
        self.classifier = ml_state["classifier"]
        self.explainer = ml_state["explainer"]
        self.manifest = ml_state["manifest"]
        self.feature_builder = FeatureBuilder(db)
        self._db_lock = asyncio.Lock() # Protect non-concurrent-safe AsyncSession

    async def predict_single(
        self,
        district_id: UUID,
        disease: str,
        as_of_date: date,
        overrides: dict[str, float] | None = None,
    ) -> PredictionResponse:
        overrides = overrides or {}

        # Step 1: extract real feature vector from DB
        async with self._db_lock:
            feature_df = await self.feature_builder.build(district_id, disease, as_of_date)

        if feature_df is None or feature_df.empty:
            raise ValueError(
                f"No historical data found for district {district_id} / {disease}. "
                "Cannot generate a prediction with zero history."
            )

        X_real = feature_df[FEATURE_NAMES].copy()

        # Step 2: apply overrides for what-if simulation
        X_sim = X_real.copy()
        if overrides:
            for feat, val in overrides.items():
                X_sim[feat] = val

        # Step 3: check for out-of-distribution features (warn, never block)
        extrapolation_warning, ood_features = self._check_distribution(X_sim)

        # Step 4: transform + inference — all CPU-bound work goes to thread pool
        loop = asyncio.get_event_loop()

        X_sim_t = await loop.run_in_executor(
            None, self.pipeline.transform, X_sim
        )

        raw_score = await loop.run_in_executor(
            None, self._run_regressor, X_sim_t
        )

        risk_tier = await loop.run_in_executor(
            None, self._run_classifier, X_sim_t, raw_score
        )

        shap_dict = await loop.run_in_executor(
            None, self._compute_shap, X_sim_t
        )

        # Step 5: baseline score (no overrides) for delta display
        baseline_score = None
        delta = None
        if overrides:
            X_real_t = await loop.run_in_executor(
                None, self.pipeline.transform, X_real
            )
            baseline_score = to_python(
                np.clip(self.regressor.predict(X_real_t), 0, 100)[0]
            )
            delta = round(raw_score - baseline_score, 2)

        # Step 6: persist to DB (idempotent)
        async with self._db_lock:
            prediction_id = await self._persist(
                district_id=district_id,
                disease=disease,
                prediction_date=as_of_date,
                risk_score=raw_score,
                risk_tier=risk_tier,
                feature_snapshot=X_sim.iloc[0].to_dict(),
                shap_values=shap_dict,
                extrapolation_warning=extrapolation_warning,
            )

        if extrapolation_warning:
            logger.warning(
                "Out-of-distribution features detected",
                extra={
                    "district_id": str(district_id),
                    "disease": disease,
                    "ood_features": ood_features,
                    "prediction_id": str(prediction_id),
                },
            )

        # Step 7: Trigger Asynchronous Alerts if high risk
        if risk_tier in [RiskTier.HIGH, RiskTier.CRITICAL]:
            task = asyncio.create_task(send_alert_notification(
                alert_id=str(prediction_id),
                district_name="Jurisdiction Monitor", # In production, fetch from District model
                disease=disease,
                risk_score=float(raw_score)
            ))
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)

        return PredictionResponse(
            prediction_id=prediction_id,
            district_id=district_id,
            disease=disease,
            prediction_date=as_of_date,
            risk_score=round(raw_score, 2),
            risk_tier=risk_tier,
            baseline_score=round(baseline_score, 2) if baseline_score else None,
            delta=delta,
            shap_values=shap_dict,
            model_version=self.manifest["version"],
            extrapolation_warning=extrapolation_warning,
        )

    async def predict_batch(
        self,
        district_ids: list[UUID],
        disease: str,
        as_of_date: date,
        concurrency: int = 5
    ) -> list[PredictionResponse]:
        """
        Optimized batch inference using asyncio.gather for concurrency.
        Uses a semaphore to prevent overwhelming the database connection pool or CPU.
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def _predict_with_sem(d_id: UUID):
            async with semaphore:
                try:
                    return await self.predict_single(d_id, disease, as_of_date)
                except ValueError as exc:
                    logger.warning(f"Skipping district {d_id}: {exc}")
                    return None
                except Exception as exc:
                    logger.error(
                        f"Unexpected error for district {d_id}: {exc}",
                        exc_info=True,
                    )
                    return None

        tasks = [_predict_with_sem(d_id) for d_id in district_ids]
        results = await asyncio.gather(*tasks)

        # Filter out skipped districts (None)
        return [r for r in results if r is not None]

    # ── private methods ──────────────────────────────────────────────────────

    def _run_regressor(self, X_t: np.ndarray) -> float:
        raw = self.regressor.predict(X_t)
        return float(np.clip(raw, 0, 100)[0])

    def _run_classifier(self, X_t: np.ndarray, risk_score: float) -> RiskTier:
        X_stacked = np.append(X_t, [[risk_score]], axis=1)
        tier_idx = int(self.classifier.predict(X_stacked)[0])
        return TIER_LABELS.get(tier_idx, RiskTier.LOW) # Default to LOW if unknown

    def _compute_shap(self, X_t: np.ndarray) -> dict[str, float]:
        shap_vals = self.explainer.shap_values(X_t)[0]
        result = {
            FEATURE_NAMES[i]: round(float(v), 4)
            for i, v in enumerate(shap_vals)
        }
        result["_base_value"] = round(float(self.explainer.expected_value), 4)
        return result

    def _check_distribution(
        self, X: pd.DataFrame
    ) -> tuple[bool, list[str]]:
        bounds = self.manifest.get("feature_bounds", {})
        ood = []
        for feat in FEATURE_NAMES:
            if feat not in bounds:
                continue
            val = float(X[feat].iloc[0])
            lo = bounds[feat]["p01"]
            hi = bounds[feat]["p99"]
            if val < lo or val > hi:
                ood.append(feat)
        return (len(ood) > 0, ood)

    async def _persist(
        self,
        district_id: UUID,
        disease: str,
        prediction_date: date,
        risk_score: float,
        risk_tier: RiskTier,
        feature_snapshot: dict,
        shap_values: dict,
        extrapolation_warning: bool,
    ) -> UUID:

        stmt = (
            pg_insert(Prediction)
            .values(
                district_id=district_id,
                disease=disease,
                prediction_date=prediction_date,
                risk_score=risk_score,
                risk_tier=risk_tier,
                model_version=self.manifest["version"],
                feature_snapshot=feature_snapshot,
                shap_values=shap_values,
                extrapolation_warning=extrapolation_warning,
                pipeline_run_id=None,  # set by scheduled pipeline, None for on-demand
            )
            .on_conflict_do_nothing(
                index_elements=["district_id", "disease", "prediction_date", "model_version"]
            )
            .returning(Prediction.id)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        row = result.fetchone()
        if row is None:
            # Row already existed — fetch the existing id
            existing = await self.db.execute(
                Prediction.__table__.select().where(
                    Prediction.district_id == district_id,
                    Prediction.disease == disease,
                    Prediction.prediction_date == prediction_date,
                    Prediction.model_version == self.manifest["version"],
                )
            )
            existing_row = existing.fetchone()
            if existing_row:
                return existing_row.id
            else:
                # This case should ideally not happen if on_conflict_do_nothing worked as expected
                # but as a fallback, raise an error or log
                raise RuntimeError("Failed to retrieve existing prediction ID after conflict.")
        return row[0]
