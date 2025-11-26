#!/usr/bin/env python3
"""
CHIMERA NEXUS - Predictive Failure Prevention
Real LSTM-based time-series anomaly detection with TensorFlow/Keras.
"""
import asyncio
import time
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import logging
import json
import pickle
import os

# Real ML imports
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import IsolationForest
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("⚠️  TensorFlow not available. Install: pip install tensorflow scikit-learn")

logger = logging.getLogger("chimera.predictive")


@dataclass
class MetricSample:
    """A single metric measurement"""
    timestamp: float
    value: float
    metric_name: str
    source: str  # node_id or "system"


@dataclass
class Anomaly:
    """Detected anomaly"""
    metric_name: str
    timestamp: float
    expected_value: float
    actual_value: float
    severity: str  # "low", "medium", "high", "critical"
    confidence: float
    recommendation: str


@dataclass
class Prediction:
    """Resource prediction"""
    metric_name: str
    timestamp: float  # When prediction was made
    forecast_time: float  # Time being predicted
    predicted_value: float
    confidence_interval: Tuple[float, float]
    action_needed: Optional[str] = None


class TimeSeriesBuffer:
    """Circular buffer for time-series data"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.data: Dict[str, deque] = {}

    def add(self, metric_name: str, sample: MetricSample):
        """Add sample to buffer"""
        if metric_name not in self.data:
            self.data[metric_name] = deque(maxlen=self.max_size)

        self.data[metric_name].append(sample)

    def get_recent(self, metric_name: str, n: int = 100) -> List[MetricSample]:
        """Get recent n samples"""
        if metric_name not in self.data:
            return []

        return list(self.data[metric_name])[-n:]

    def get_values(self, metric_name: str, n: int = 100) -> np.ndarray:
        """Get recent values as numpy array"""
        samples = self.get_recent(metric_name, n)
        return np.array([s.value for s in samples])

    def get_timestamps(self, metric_name: str, n: int = 100) -> np.ndarray:
        """Get recent timestamps"""
        samples = self.get_recent(metric_name, n)
        return np.array([s.timestamp for s in samples])


class RealLSTM:
    """Real LSTM using TensorFlow/Keras"""

    def __init__(self, input_size: int = 10, hidden_size: int = 64, model_path: str = None):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.trained = False

        if not TF_AVAILABLE:
            logger.warning(
                "TensorFlow not available - predictions will be limited")
            return

        # Build LSTM model
        self.model = keras.Sequential([
            layers.LSTM(hidden_size, return_sequences=True,
                        input_shape=(input_size, 1)),
            layers.Dropout(0.2),
            layers.LSTM(hidden_size // 2, return_sequences=False),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(1)
        ])

        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )

        # Load existing model if available
        if model_path and os.path.exists(model_path):
            try:
                self.model = keras.models.load_model(model_path)
                scaler_path = model_path.replace('.h5', '_scaler.pkl')
                if os.path.exists(scaler_path):
                    with open(scaler_path, 'rb') as f:
                        self.scaler = pickle.load(f)
                self.trained = True
                logger.info(f"Loaded trained model from {model_path}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 50, batch_size: int = 32):
        """Train LSTM on data"""
        if not TF_AVAILABLE or self.model is None:
            return

        if len(X) < 20:
            logger.warning(f"Insufficient data for training: {len(X)} samples")
            return

        try:
            # Normalize data
            y_scaled = self.scaler.fit_transform(y.reshape(-1, 1)).flatten()

            # Prepare sequences
            X_train, y_train = self._prepare_sequences(X, y_scaled)

            if len(X_train) < 10:
                return

            # Train with validation split
            history = self.model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=0.2,
                verbose=0,
                callbacks=[
                    keras.callbacks.EarlyStopping(
                        patience=10, restore_best_weights=True),
                    keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5)
                ]
            )

            self.trained = True

            # Save model
            if self.model_path:
                self.model.save(self.model_path)
                scaler_path = self.model_path.replace('.h5', '_scaler.pkl')
                with open(scaler_path, 'wb') as f:
                    pickle.dump(self.scaler, f)
                logger.info(f"Model saved to {self.model_path}")

            logger.info(
                f"Training complete - Loss: {history.history['loss'][-1]:.4f}")

        except Exception as e:
            logger.error(f"Training failed: {e}")

    def _prepare_sequences(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare LSTM input sequences"""
        X_seq, y_seq = [], []

        for i in range(len(y) - self.input_size):
            X_seq.append(y[i:i+self.input_size])
            y_seq.append(y[i+self.input_size])

        X_seq = np.array(X_seq).reshape(-1, self.input_size, 1)
        y_seq = np.array(y_seq)

        return X_seq, y_seq

    def predict(self, X: np.ndarray, steps: int = 1) -> np.ndarray:
        """Predict future values"""
        if not TF_AVAILABLE or self.model is None or not self.trained:
            # Fallback: simple moving average
            return np.full(steps, np.mean(X[-10:]))

        try:
            predictions = []
            last_sequence = X[-self.input_size:].copy()

            # Normalize
            last_sequence_scaled = self.scaler.transform(
                last_sequence.reshape(-1, 1)).flatten()

            for _ in range(steps):
                # Prepare input
                input_seq = last_sequence_scaled[-self.input_size:].reshape(
                    1, self.input_size, 1)

                # Predict
                pred_scaled = self.model.predict(input_seq, verbose=0)[0, 0]

                # Denormalize
                pred = self.scaler.inverse_transform([[pred_scaled]])[0, 0]
                predictions.append(pred)

                # Update sequence
                last_sequence_scaled = np.append(
                    last_sequence_scaled, pred_scaled)[-self.input_size:]

            return np.array(predictions)

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return np.full(steps, np.mean(X[-10:]))


class RealAnomalyDetector:
    """ML-based anomaly detection using Isolation Forest"""

    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.models: Dict[str, IsolationForest] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.baseline_stats: Dict[str, Dict[str, float]] = {}

        if not TF_AVAILABLE:
            logger.warning(
                "scikit-learn not available - using statistical detection")

    def update_baseline(self, metric_name: str, values: np.ndarray):
        """Train anomaly detection model"""
        if len(values) < 20:
            return

        # Statistical baseline
        self.baseline_stats[metric_name] = {
            'mean': np.mean(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'median': np.median(values),
            'q25': np.percentile(values, 25),
            'q75': np.percentile(values, 75)
        }

        if not TF_AVAILABLE:
            return

        try:
            # Train Isolation Forest
            scaler = StandardScaler()
            values_scaled = scaler.fit_transform(values.reshape(-1, 1))

            model = IsolationForest(
                contamination=self.contamination,
                random_state=42,
                n_estimators=100
            )
            model.fit(values_scaled)

            self.models[metric_name] = model
            self.scalers[metric_name] = scaler

            logger.debug(f"Trained anomaly detector for {metric_name}")

        except Exception as e:
            logger.error(f"Failed to train anomaly detector: {e}")

    def detect(self, metric_name: str, value: float, timestamp: float) -> Optional[Anomaly]:
        """Detect if value is anomalous using ML"""
        if metric_name not in self.baseline_stats:
            return None

        stats = self.baseline_stats[metric_name]

        # ML-based detection if available
        if TF_AVAILABLE and metric_name in self.models:
            try:
                scaler = self.scalers[metric_name]
                model = self.models[metric_name]

                value_scaled = scaler.transform([[value]])
                prediction = model.predict(value_scaled)[0]
                anomaly_score = -model.score_samples(value_scaled)[0]

                if prediction == -1:  # Anomaly detected
                    # Calculate severity based on anomaly score
                    if anomaly_score > 0.7:
                        severity = "critical"
                    elif anomaly_score > 0.6:
                        severity = "high"
                    elif anomaly_score > 0.5:
                        severity = "medium"
                    else:
                        severity = "low"

                    # Generate recommendation
                    mean = stats['mean']
                    std = stats['std']
                    z_score = abs((value - mean) / std) if std > 0 else 0

                    if value > mean:
                        recommendation = f"{metric_name} anomaly detected: {value:.2f} (expected ~{mean:.2f}). Anomaly score: {anomaly_score:.3f}. Consider scaling up."
                    else:
                        recommendation = f"{metric_name} anomaly detected: {value:.2f} (expected ~{mean:.2f}). Anomaly score: {anomaly_score:.3f}. Investigate issues."

                    return Anomaly(
                        metric_name=metric_name,
                        timestamp=timestamp,
                        expected_value=mean,
                        actual_value=value,
                        severity=severity,
                        confidence=min(anomaly_score, 1.0),
                        recommendation=recommendation
                    )

            except Exception as e:
                logger.error(f"ML detection failed: {e}")

        # Fallback to statistical detection
        mean = stats['mean']
        std = stats['std']

        if std == 0:
            return None

        z_score = abs((value - mean) / std)

        if z_score > 3.0:
            severity = "critical" if z_score > 5 else "high" if z_score > 4 else "medium"

            recommendation = f"{metric_name} is {z_score:.1f} std from normal ({value:.2f} vs {mean:.2f})"

            return Anomaly(
                metric_name=metric_name,
                timestamp=timestamp,
                expected_value=mean,
                actual_value=value,
                severity=severity,
                confidence=min(z_score / 5.0, 1.0),
                recommendation=recommendation
            )

        return None


class ResourceForecaster:
    """Forecast future resource usage"""

    def __init__(self):
        self.models: Dict[str, SimpleLSTM] = {}
        self.training_window = 100
        self.forecast_horizon = 10

    def train(self, metric_name: str, buffer: TimeSeriesBuffer):
        """Train forecasting model"""
        values = buffer.get_values(metric_name, self.training_window)

        if len(values) < 20:
            logger.debug(
                f"Insufficient data for {metric_name} ({len(values)} samples)")
            return

        # Prepare sequences
        X, y = self._create_sequences(values)

        if len(X) == 0:
            return

        # Train model
        if metric_name not in self.models:
            self.models[metric_name] = SimpleLSTM()

        self.models[metric_name].fit(X, y)
        logger.debug(f"Trained forecaster for {metric_name}")

    def _create_sequences(self, data: np.ndarray, seq_length: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """Create input sequences"""
        X, y = [], []

        for i in range(len(data) - seq_length):
            X.append(data[i:i+seq_length])
            y.append(data[i+seq_length])

        return np.array(X), np.array(y)

    def forecast(self, metric_name: str, buffer: TimeSeriesBuffer, steps: int = 5) -> List[Prediction]:
        """Forecast future values"""
        if metric_name not in self.models:
            return []

        values = buffer.get_values(metric_name, self.training_window)

        if len(values) < 10:
            return []

        # Make predictions
        predictions = self.models[metric_name].predict(values, steps)

        # Calculate confidence intervals (simplified)
        std = np.std(values[-20:]) if len(values) >= 20 else np.std(values)

        current_time = time.time()
        interval = 60.0  # 1 minute per step

        results = []
        for i, pred_value in enumerate(predictions):
            forecast_time = current_time + (i + 1) * interval

            # Confidence interval
            conf_lower = pred_value - 2 * std
            conf_upper = pred_value + 2 * std

            # Determine if action needed
            action = None
            current_mean = np.mean(values[-10:])

            if pred_value > current_mean * 1.5:
                action = f"Scale up: {metric_name} predicted to increase by {((pred_value/current_mean - 1) * 100):.0f}%"
            elif pred_value < current_mean * 0.5:
                action = f"Scale down: {metric_name} predicted to decrease by {((1 - pred_value/current_mean) * 100):.0f}%"

            results.append(Prediction(
                metric_name=metric_name,
                timestamp=current_time,
                forecast_time=forecast_time,
                predicted_value=pred_value,
                confidence_interval=(conf_lower, conf_upper),
                action_needed=action
            ))

        return results


class PredictiveMonitor:
    """Main predictive monitoring engine"""

    def __init__(self, heart_node=None):
        self.heart = heart_node
        self.buffer = TimeSeriesBuffer(max_size=2000)
        self.detector = AnomalyDetector(threshold_std=3.0)
        self.forecaster = ResourceForecaster()

        self.anomalies: List[Anomaly] = []
        self.predictions: Dict[str, List[Prediction]] = {}

        self.monitored_metrics = [
            'cpu_usage',
            'memory_usage',
            'network_latency',
            'task_queue_length',
            'error_rate',
            'throughput'
        ]

        self.monitoring_active = False
        self._monitor_task = None
        self._training_task = None

    async def start(self):
        """Start predictive monitoring"""
        self.monitoring_active = True

        # Start monitoring loop
        self._monitor_task = asyncio.create_task(self._monitoring_loop())

        # Start training loop
        self._training_task = asyncio.create_task(self._training_loop())

        logger.info("Predictive monitoring started")

    async def stop(self):
        """Stop monitoring"""
        self.monitoring_active = False

        if self._monitor_task:
            self._monitor_task.cancel()

        if self._training_task:
            self._training_task.cancel()

        logger.info("Predictive monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect metrics
                await self._collect_metrics()

                # Check for anomalies
                await self._check_anomalies()

                # Generate forecasts
                await self._generate_forecasts()

                # Sleep
                await asyncio.sleep(10)  # Every 10 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)

    async def _training_loop(self):
        """Periodic model training"""
        while self.monitoring_active:
            try:
                # Retrain models every 5 minutes
                await asyncio.sleep(300)

                for metric in self.monitored_metrics:
                    self.forecaster.train(metric, self.buffer)

                    # Update anomaly detection baseline
                    values = self.buffer.get_values(metric, 200)
                    if len(values) >= 20:
                        self.detector.update_baseline(metric, values)

                logger.info("Models retrained")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Training loop error: {e}")

    async def _collect_metrics(self):
        """Collect current metrics"""
        current_time = time.time()

        # Simulate metric collection (in real implementation, would query actual system)
        for metric in self.monitored_metrics:
            value = self._simulate_metric(metric, current_time)

            sample = MetricSample(
                timestamp=current_time,
                value=value,
                metric_name=metric,
                source="system"
            )

            self.buffer.add(metric, sample)

    def _simulate_metric(self, metric: str, timestamp: float) -> float:
        """Simulate metric value (for demo)"""
        # Base patterns
        t = timestamp / 60.0  # Minutes

        if metric == 'cpu_usage':
            # Sinusoidal with trend
            base = 50 + 20 * np.sin(t / 10)
            noise = np.random.normal(0, 5)
            spike = 30 if np.random.random() < 0.02 else 0  # 2% chance of spike
            return max(0, min(100, base + noise + spike))

        elif metric == 'memory_usage':
            # Gradual increase with resets
            base = 40 + (t % 100) * 0.3
            noise = np.random.normal(0, 3)
            return max(0, min(100, base + noise))

        elif metric == 'network_latency':
            # Low with occasional spikes
            base = 50
            noise = np.random.exponential(20)
            return max(0, base + noise)

        elif metric == 'task_queue_length':
            # Varying load
            base = 10 + 5 * np.sin(t / 5)
            noise = np.random.poisson(3)
            return max(0, base + noise)

        elif metric == 'error_rate':
            # Low with rare spikes
            base = 0.5
            spike = 5 if np.random.random() < 0.01 else 0
            noise = np.random.exponential(0.5)
            return max(0, base + noise + spike)

        elif metric == 'throughput':
            # Inverse of queue length
            base = 100 - (10 + 5 * np.sin(t / 5))
            noise = np.random.normal(0, 5)
            return max(0, base + noise)

        return 50.0

    async def _check_anomalies(self):
        """Check for anomalies in recent data"""
        for metric in self.monitored_metrics:
            recent = self.buffer.get_recent(metric, 1)

            if not recent:
                continue

            sample = recent[0]
            anomaly = self.detector.detect(
                metric, sample.value, sample.timestamp)

            if anomaly:
                self.anomalies.append(anomaly)
                logger.warning(
                    f"Anomaly detected: {anomaly.metric_name} - {anomaly.severity} - {anomaly.recommendation}")

                # Trigger preemptive action
                await self._handle_anomaly(anomaly)

        # Keep only recent anomalies
        cutoff = time.time() - 3600  # Last hour
        self.anomalies = [a for a in self.anomalies if a.timestamp >= cutoff]

    async def _generate_forecasts(self):
        """Generate resource forecasts"""
        for metric in self.monitored_metrics:
            predictions = self.forecaster.forecast(
                metric, self.buffer, steps=5)

            if predictions:
                self.predictions[metric] = predictions

                # Check if action needed
                for pred in predictions:
                    if pred.action_needed:
                        logger.info(f"Forecast: {pred.action_needed}")
                        await self._handle_prediction(pred)

    async def _handle_anomaly(self, anomaly: Anomaly):
        """Handle detected anomaly"""
        if anomaly.severity in ['high', 'critical']:
            logger.warning(f"CRITICAL: {anomaly.recommendation}")

            # Auto-scale if possible
            if 'cpu_usage' in anomaly.metric_name or 'memory_usage' in anomaly.metric_name:
                await self._auto_scale_up()

    async def _handle_prediction(self, prediction: Prediction):
        """Handle prediction that needs action"""
        if 'Scale up' in prediction.action_needed:
            logger.info(
                f"Preemptive scaling triggered: {prediction.action_needed}")
            await self._auto_scale_up()

    async def _auto_scale_up(self):
        """Auto-scale resources"""
        # In real implementation, would trigger actual scaling
        logger.info("Auto-scaling: Adding compute resources...")

    def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        recent_anomalies = [
            a for a in self.anomalies if a.timestamp >= time.time() - 300]

        return {
            'monitoring_active': self.monitoring_active,
            'monitored_metrics': len(self.monitored_metrics),
            'total_samples': sum(len(self.buffer.data[m]) for m in self.buffer.data),
            'anomalies_last_5min': len(recent_anomalies),
            'anomalies_by_severity': {
                severity: sum(
                    1 for a in recent_anomalies if a.severity == severity)
                for severity in ['low', 'medium', 'high', 'critical']
            },
            'forecasts_available': list(self.predictions.keys()),
            'recent_anomalies': [
                {
                    'metric': a.metric_name,
                    'severity': a.severity,
                    'time': a.timestamp,
                    'recommendation': a.recommendation
                }
                for a in recent_anomalies[-5:]
            ]
        }

    def get_forecast_report(self) -> Dict[str, Any]:
        """Get forecast report"""
        report = {}

        for metric, predictions in self.predictions.items():
            if predictions:
                latest = predictions[-1]
                report[metric] = {
                    'current': self.buffer.get_values(metric, 1)[0] if self.buffer.get_values(metric, 1).size > 0 else 0,
                    'predicted_5min': latest.predicted_value,
                    'confidence_interval': latest.confidence_interval,
                    'action_needed': latest.action_needed,
                    'forecast_time': latest.forecast_time
                }

        return report


# Integration with CHIMERA
class ChimeraPredictiveIntegration:
    """Integration layer for CHIMERA"""

    def __init__(self, heart_node):
        self.heart = heart_node
        self.monitor = PredictiveMonitor(heart_node)

    async def start(self):
        """Start predictive monitoring"""
        await self.monitor.start()
        logger.info("CHIMERA predictive monitoring enabled")

    async def stop(self):
        """Stop monitoring"""
        await self.monitor.stop()

    def get_health_status(self) -> Dict[str, Any]:
        """Get system health with predictions"""
        stats = self.monitor.get_stats()
        forecasts = self.monitor.get_forecast_report()

        return {
            'status': 'healthy' if stats['anomalies_last_5min'] == 0 else 'warning',
            'monitoring': stats,
            'forecasts': forecasts
        }
