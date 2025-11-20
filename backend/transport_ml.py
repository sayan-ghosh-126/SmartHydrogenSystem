import os
import math
import random
from typing import Dict, Any, Tuple

from joblib import dump, load
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'transport_model.joblib')


def _ensure_model_dir():
    d = os.path.dirname(MODEL_PATH)
    os.makedirs(d, exist_ok=True)


def _mode_score(mode: str) -> float:
    m = mode.lower()
    if m == 'truck':
        return 1.0
    if m == 'pipeline':
        return 0.5
    if m in ('cargo ship', 'ship', 'tanker'):
        return 0.8
    return 0.9


def _generate_synthetic(n: int = 2000) -> Tuple[np.ndarray, np.ndarray]:
    X = []
    y = []
    modes = ['truck', 'pipeline', 'cargo ship']
    rng = random.Random(42)
    for _ in range(n):
        distance_km = rng.uniform(5, 2000)
        traffic = max(0.0, min(1.0, rng.random()))
        weather = max(0.0, min(1.0, rng.random()))
        mode = rng.choice(modes)
        vs = _mode_score(mode)
        X.append([distance_km, traffic, weather, vs])
        base = 100.0
        penalty = min(distance_km / 25.0, 45.0) + traffic * 20.0 + weather * 15.0 + (1.2 - vs) * 12.0
        score = max(0.0, min(100.0, base - penalty + rng.uniform(-3, 3)))
        y.append(score)
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


def train_model() -> None:
    _ensure_model_dir()
    X, y = _generate_synthetic()
    try:
        model = RandomForestRegressor(n_estimators=60, random_state=0)
    except Exception:
        model = LinearRegression()
    model.fit(X, y)
    dump(model, MODEL_PATH)


def load_model():
    if not os.path.exists(MODEL_PATH):
        train_model()
    return load(MODEL_PATH)


_MODEL = None


def init_model():
    global _MODEL
    _MODEL = load_model()


def predict_efficiency(features: Dict[str, Any]) -> float:
    global _MODEL
    if _MODEL is None:
        init_model()
    distance_km = float(features.get('distance_km', 0.0))
    traffic = float(features.get('avg_traffic_score', 0.0))
    weather = float(features.get('weather_risk', 0.0))
    vs = _mode_score(str(features.get('mode', 'truck')))
    X = np.array([[distance_km, traffic, weather, vs]], dtype=np.float32)
    pred = float(_MODEL.predict(X)[0])
    return max(0.0, min(100.0, pred))


def recommend_action(efficiency_score: float, load: float, capacity: float) -> str:
    overloaded = load > capacity
    if overloaded:
        return 'load-balance'
    if efficiency_score < 45:
        return 'hold'
    if efficiency_score < 65:
        return 'reroute'
    return 'dispatch'