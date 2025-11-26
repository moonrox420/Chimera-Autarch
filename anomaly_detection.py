#!/usr/bin/env python3
"""
CHIMERA AUTARCH - Time-Series Anomaly Detection Module
Predictive failure detection with ML-based anomaly detection
"""
import asyncio
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("chimera.anomaly")


@dataclass
class TimeSeriesPoint:
    """Single time series data point"""
    timestamp: float
    value: float
    metric_name: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Anomaly:
    """Detected anomaly"""
    metric_name: str
    timestamp: float
    expected_value: float
    actual_value: float
    severity: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    anomaly_type: str  # spike, drop, trend_change, pattern_break
    prediction: Optional[float] = None  # Predicted next value


class TimeSeriesBuffer:
    """Circular buffer for time series data with statistics"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.data: deque = deque(maxlen=max_size)
        self.metric_buffers: Dict[str, deque] = {}

    def add(self, point: TimeSeriesPoint):
        """Add data point to buffer"""
        self.data.append(point)

        # Maintain per-metric buffers
        if point.metric_name not in self.metric_buffers:
            self.metric_buffers[point.metric_name] = deque(
                maxlen=self.max_size)

        self.metric_buffers[point.metric_name].append(point)

    def get_metric_values(self, metric_name: str, last_n: Optional[int] = None) -> np.ndarray:
        """Get values for specific metric"""
        if metric_name not in self.metric_buffers:
            return np.array([])

        buffer = self.metric_buffers[metric_name]
        values = [p.value for p in buffer]

        if last_n:
            values = values[-last_n:]

        return np.array(values)

    def get_recent_window(self, metric_name: str, seconds: float) -> List[TimeSeriesPoint]:
        """Get data points within time window"""
        if metric_name not in self.metric_buffers:
            return []

        current_time = datetime.now().timestamp()
        cutoff_time = current_time - seconds

        return [p for p in self.metric_buffers[metric_name] if p.timestamp >= cutoff_time]


class StatisticalDetector:
    """Statistical anomaly detection using Z-score and moving averages"""

    def __init__(self, z_threshold: float = 3.0, window_size: int = 50):
        self.z_threshold = z_threshold
        self.window_size = window_size

    def detect(self, values: np.ndarray) -> Tuple[bool, float]:
        """Detect anomalies using Z-score

        Returns:
            (is_anomaly, severity)
        """
        if len(values) < 2:
            return False, 0.0

        # Calculate mean and std of historical data (excluding last point)
        historical = values[:-1]
        current = values[-1]

        if len(historical) < 2:
            return False, 0.0

        mean = np.mean(historical)
        std = np.std(historical)

        if std == 0:
            return False, 0.0

        # Z-score
        z_score = abs(current - mean) / std

        is_anomaly = z_score > self.z_threshold
        severity = min(z_score / (self.z_threshold * 2), 1.0)

        return is_anomaly, severity

    def detect_trend_change(self, values: np.ndarray, window: int = 20) -> Tuple[bool, float]:
        """Detect sudden trend changes"""
        if len(values) < window * 2:
            return False, 0.0

        # Compare slopes of two windows
        recent = values[-window:]
        previous = values[-window*2:-window]

        recent_slope = self._calculate_slope(recent)
        previous_slope = self._calculate_slope(previous)

        # Detect significant slope change
        if abs(previous_slope) < 0.001:  # Avoid division by zero
            return False, 0.0

        slope_change_ratio = abs(
            recent_slope - previous_slope) / abs(previous_slope)

        is_anomaly = slope_change_ratio > 2.0  # 200% change in slope
        severity = min(slope_change_ratio / 4.0, 1.0)

        return is_anomaly, severity

    def _calculate_slope(self, values: np.ndarray) -> float:
        """Calculate linear regression slope"""
        if len(values) < 2:
            return 0.0

        x = np.arange(len(values))
        coefficients = np.polyfit(x, values, 1)
        return coefficients[0]


class MovingAverageDetector:
    """Anomaly detection using Exponential Weighted Moving Average (EWMA)"""

    def __init__(self, alpha: float = 0.3, threshold: float = 3.0):
        self.alpha = alpha  # Smoothing factor
        self.threshold = threshold
        self.ewma: Dict[str, float] = {}
        self.ewmstd: Dict[str, float] = {}

    def detect(self, metric_name: str, value: float) -> Tuple[bool, float]:
        """Detect anomalies using EWMA

        Returns:
            (is_anomaly, severity)
        """
        # Initialize EWMA if first point
        if metric_name not in self.ewma:
            self.ewma[metric_name] = value
            self.ewmstd[metric_name] = 0.0
            return False, 0.0

        # Update EWMA
        prev_ewma = self.ewma[metric_name]
        self.ewma[metric_name] = self.alpha * \
            value + (1 - self.alpha) * prev_ewma

        # Update EWMA of standard deviation
        deviation = abs(value - prev_ewma)
        if metric_name not in self.ewmstd or self.ewmstd[metric_name] == 0:
            self.ewmstd[metric_name] = deviation
        else:
            self.ewmstd[metric_name] = self.alpha * deviation + \
                (1 - self.alpha) * self.ewmstd[metric_name]

        # Detect anomaly
        if self.ewmstd[metric_name] == 0:
            return False, 0.0

        z_score = abs(value - self.ewma[metric_name]
                      ) / self.ewmstd[metric_name]

        is_anomaly = z_score > self.threshold
        severity = min(z_score / (self.threshold * 2), 1.0)

        return is_anomaly, severity

    def predict_next(self, metric_name: str) -> Optional[float]:
        """Predict next value based on EWMA"""
        return self.ewma.get(metric_name)


class IsolationForestDetector:
    """Advanced anomaly detection using Isolation Forest (requires sklearn)"""

    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.available = False
        self.models: Dict[str, Any] = {}

        try:
            from sklearn.ensemble import IsolationForest
            self.IsolationForest = IsolationForest
            self.available = True
        except ImportError:
            logger.warning(
                "scikit-learn not available. Isolation Forest disabled.")

    def fit_and_detect(self, metric_name: str, values: np.ndarray) -> Tuple[bool, float]:
        """Fit model and detect anomaly in latest value"""
        if not self.available or len(values) < 10:
            return False, 0.0

        # Reshape for sklearn
        X = values.reshape(-1, 1)

        # Create or get model
        if metric_name not in self.models:
            self.models[metric_name] = self.IsolationForest(
                contamination=self.contamination,
                random_state=42
            )

        model = self.models[metric_name]

        # Fit on all data
        model.fit(X)

        # Predict on last point
        last_point = X[-1:]
        prediction = model.predict(last_point)[0]
        anomaly_score = model.score_samples(last_point)[0]

        is_anomaly = prediction == -1
        severity = abs(anomaly_score) if is_anomaly else 0.0

        return is_anomaly, severity


class ForecastEngine:
    """Time series forecasting for predictive anomaly detection"""

    def __init__(self, forecast_horizon: int = 10):
        self.forecast_horizon = forecast_horizon

    def forecast_arima(self, values: np.ndarray, steps: int = 5) -> np.ndarray:
        """Simple ARIMA-style forecast using autoregression"""
        if len(values) < 10:
            return np.array([values[-1]] * steps)

        # Simple AR(1) model - first order autoregression
        # Next value = mean + correlation * (last - mean)
        mean = np.mean(values)

        # Calculate lag-1 autocorrelation
        deviations = values - mean
        autocorr = np.corrcoef(deviations[:-1], deviations[1:])[0, 1]

        # Generate forecast
        forecast = []
        last_value = values[-1]

        for _ in range(steps):
            next_value = mean + autocorr * (last_value - mean)
            forecast.append(next_value)
            last_value = next_value

        return np.array(forecast)

    def forecast_ema(self, values: np.ndarray, alpha: float = 0.3, steps: int = 5) -> np.ndarray:
        """Exponential moving average forecast"""
        if len(values) == 0:
            return np.array([])

        # Calculate current EMA
        ema = values[0]
        for value in values[1:]:
            ema = alpha * value + (1 - alpha) * ema

        # Forecast (EMA stays constant in simple model)
        return np.array([ema] * steps)

    def detect_future_anomaly(
        self,
        values: np.ndarray,
        forecast_steps: int = 10
    ) -> Tuple[bool, float, np.ndarray]:
        """Predict if anomaly will occur in near future

        Returns:
            (will_anomaly_occur, confidence, forecast)
        """
        if len(values) < 20:
            return False, 0.0, np.array([])

        # Generate forecast
        forecast = self.forecast_arima(values, steps=forecast_steps)

        # Calculate historical statistics
        mean = np.mean(values)
        std = np.std(values)

        if std == 0:
            return False, 0.0, forecast

        # Check if any forecast point deviates significantly
        z_scores = np.abs((forecast - mean) / std)
        max_z = np.max(z_scores)

        will_anomaly = max_z > 2.5
        confidence = min(max_z / 5.0, 1.0)

        return will_anomaly, confidence, forecast


class AnomalyDetectionEngine:
    """Main anomaly detection engine with multiple detectors"""

    def __init__(self, buffer_size: int = 1000):
        self.buffer = TimeSeriesBuffer(max_size=buffer_size)
        self.statistical_detector = StatisticalDetector(z_threshold=3.0)
        self.ewma_detector = MovingAverageDetector(alpha=0.3)
        self.isolation_forest = IsolationForestDetector(contamination=0.1)
        self.forecast_engine = ForecastEngine()

        self.detected_anomalies: List[Anomaly] = []
        self.alert_cooldown: Dict[str, float] = {}
        self.cooldown_seconds = 60.0  # Don't alert same metric twice in 60s

    async def add_metric(
        self,
        metric_name: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add metric value and check for anomalies"""
        point = TimeSeriesPoint(
            timestamp=datetime.now().timestamp(),
            value=value,
            metric_name=metric_name,
            metadata=metadata or {}
        )

        self.buffer.add(point)

        # Run detection
        anomaly = await self.detect_anomaly(metric_name, value)

        if anomaly:
            self.detected_anomalies.append(anomaly)
            logger.warning(
                f"Anomaly detected: {metric_name}={value:.4f} "
                f"(expected={anomaly.expected_value:.4f}, "
                f"severity={anomaly.severity:.2f}, "
                f"type={anomaly.anomaly_type})"
            )

    async def detect_anomaly(
        self,
        metric_name: str,
        current_value: float
    ) -> Optional[Anomaly]:
        """Run multiple detectors and combine results"""

        # Check cooldown
        current_time = datetime.now().timestamp()
        if metric_name in self.alert_cooldown:
            if current_time - self.alert_cooldown[metric_name] < self.cooldown_seconds:
                return None

        values = self.buffer.get_metric_values(metric_name)

        if len(values) < 10:
            return None

        # Run detectors
        detections = []

        # Statistical detection
        is_anomaly_stat, severity_stat = self.statistical_detector.detect(
            values)
        if is_anomaly_stat:
            detections.append(("statistical", severity_stat, "spike" if current_value > np.mean(
                values[:-1]) else "drop"))

        # EWMA detection
        is_anomaly_ewma, severity_ewma = self.ewma_detector.detect(
            metric_name, current_value)
        if is_anomaly_ewma:
            predicted = self.ewma_detector.predict_next(metric_name)
            detections.append(("ewma", severity_ewma, "deviation"))

        # Trend change detection
        is_trend_change, trend_severity = self.statistical_detector.detect_trend_change(
            values)
        if is_trend_change:
            detections.append(("trend", trend_severity, "trend_change"))

        # Isolation Forest (if available)
        if self.isolation_forest.available:
            is_anomaly_if, severity_if = self.isolation_forest.fit_and_detect(
                metric_name, values)
            if is_anomaly_if:
                detections.append(
                    ("isolation_forest", severity_if, "pattern_break"))

        # If any detector triggered, create anomaly
        if detections:
            # Use highest severity detection
            detector, severity, anomaly_type = max(
                detections, key=lambda x: x[1])

            # Get expected value (EWMA prediction or mean)
            expected = self.ewma_detector.predict_next(
                metric_name) or np.mean(values[:-1])

            # Calculate confidence (based on agreement between detectors)
            # Normalize by number of detectors
            confidence = len(detections) / 3.0

            # Update cooldown
            self.alert_cooldown[metric_name] = current_time

            anomaly = Anomaly(
                metric_name=metric_name,
                timestamp=current_time,
                expected_value=expected,
                actual_value=current_value,
                severity=severity,
                confidence=min(confidence, 1.0),
                anomaly_type=anomaly_type
            )

            return anomaly

        return None

    async def predict_future_anomalies(
        self,
        metric_name: str,
        forecast_minutes: int = 10
    ) -> Tuple[bool, float, Optional[np.ndarray]]:
        """Predict if anomalies will occur in the future"""
        values = self.buffer.get_metric_values(metric_name)

        if len(values) < 20:
            return False, 0.0, None

        # Forecast steps (1 per minute)
        forecast_steps = forecast_minutes

        will_anomaly, confidence, forecast = self.forecast_engine.detect_future_anomaly(
            values,
            forecast_steps=forecast_steps
        )

        if will_anomaly:
            logger.warning(
                f"Predicted anomaly in {metric_name} within {forecast_minutes} minutes "
                f"(confidence={confidence:.2f})"
            )

        return will_anomaly, confidence, forecast

    def get_recent_anomalies(self, minutes: int = 60) -> List[Anomaly]:
        """Get anomalies detected in last N minutes"""
        cutoff_time = datetime.now().timestamp() - (minutes * 60)
        return [a for a in self.detected_anomalies if a.timestamp >= cutoff_time]

    def get_anomaly_stats(self) -> Dict[str, Any]:
        """Get anomaly detection statistics"""
        if not self.detected_anomalies:
            return {
                "total_anomalies": 0,
                "anomalies_last_hour": 0,
                "avg_severity": 0.0,
                "by_type": {},
                "by_metric": {}
            }

        recent = self.get_recent_anomalies(minutes=60)

        by_type = {}
        by_metric = {}

        for anomaly in self.detected_anomalies:
            by_type[anomaly.anomaly_type] = by_type.get(
                anomaly.anomaly_type, 0) + 1
            by_metric[anomaly.metric_name] = by_metric.get(
                anomaly.metric_name, 0) + 1

        return {
            "total_anomalies": len(self.detected_anomalies),
            "anomalies_last_hour": len(recent),
            "avg_severity": np.mean([a.severity for a in self.detected_anomalies]),
            "by_type": by_type,
            "by_metric": by_metric,
            "detectors": {
                "statistical": True,
                "ewma": True,
                "isolation_forest": self.isolation_forest.available
            }
        }
