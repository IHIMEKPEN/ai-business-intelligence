"""
Analyzer Agent

Responsible for data analysis, pattern recognition, and statistical processing:
- Data preprocessing and cleaning
- Statistical analysis
- Pattern recognition
- Trend analysis
- Anomaly detection
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import structlog
from datetime import datetime, timedelta
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import json

from core.agent_framework import BaseAgent, AgentType, Task, Message
from core.communication import communication_manager

logger = structlog.get_logger(__name__)


class AnalyzerAgent(BaseAgent):
    """
    Analyzer Agent for data processing and analysis
    
    Capabilities:
    - Data preprocessing and cleaning
    - Statistical analysis
    - Pattern recognition
    - Trend analysis
    - Anomaly detection
    - Time series analysis
    """
    
    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id=agent_id or f"analyzer_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            agent_type=AgentType.ANALYZER,
            name="Analyzer Agent"
        )
        
        self.capabilities = [
            "data_preprocessing",
            "statistical_analysis",
            "pattern_recognition",
            "trend_analysis",
            "anomaly_detection",
            "time_series_analysis",
            "clustering_analysis"
        ]
        
        self.analysis_cache = {}
        self.models = {}
        
        logger.info(
            "Analyzer Agent initialized",
            agent_id=self.agent_id,
            capabilities=self.capabilities
        )
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process analysis tasks"""
        task_type = task.name
        parameters = task.parameters
        
        logger.info(
            "Processing analysis task",
            task_id=task.id,
            task_type=task_type,
            parameters=parameters
        )
        
        try:
            if task_type == "analyze_trends":
                return await self._analyze_trends(parameters)
            elif task_type == "pattern_recognition":
                return await self._pattern_recognition(parameters)
            elif task_type == "anomaly_detection":
                return await self._anomaly_detection(parameters)
            elif task_type == "statistical_analysis":
                return await self._statistical_analysis(parameters)
            elif task_type == "clustering_analysis":
                return await self._clustering_analysis(parameters)
            elif task_type == "time_series_analysis":
                return await self._time_series_analysis(parameters)
            elif task_type == "analyze_stocks":
                return await self._analyze_stocks(parameters)
            elif task_type == "analyze_forex":
                return await self._analyze_forex(parameters)
            elif task_type == "analyze_crypto":
                return await self._analyze_crypto(parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            logger.error(
                "Task processing failed",
                task_id=task.id,
                task_type=task_type,
                error=str(e)
            )
            raise
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle incoming messages"""
        message_type = message.message_type
        
        if message_type == "analysis_request":
            return await self._handle_analysis_request(message)
        elif message_type == "data_update":
            return await self._handle_data_update(message)
        else:
            logger.warning(
                "Unknown message type",
                message_type=message_type,
                agent_id=self.agent_id
            )
            return None
    
    async def _analyze_trends(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends in time series data"""
        data = parameters.get("data")
        time_column = parameters.get("time_column", "timestamp")
        value_column = parameters.get("value_column", "value")
        trend_period = parameters.get("trend_period", 7)  # days
        
        if not data:
            raise ValueError("No data provided for trend analysis")
        
        try:
            # Convert to DataFrame if needed
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame([data])
            
            # Ensure time column is datetime
            df[time_column] = pd.to_datetime(df[time_column])
            df = df.sort_values(time_column)
            
            # Extract values for analysis
            values = df[value_column].values
            times = df[time_column].values
            
            # Calculate trend metrics
            trend_analysis = {
                "data_points": len(values),
                "time_range": {
                    "start": times[0].isoformat() if len(times) > 0 else None,
                    "end": times[-1].isoformat() if len(times) > 0 else None
                },
                "basic_stats": {
                    "mean": float(np.mean(values)),
                    "median": float(np.median(values)),
                    "std": float(np.std(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values))
                }
            }
            
            # Linear trend analysis
            if len(values) > 1:
                x = np.arange(len(values))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
                
                trend_analysis["linear_trend"] = {
                    "slope": float(slope),
                    "intercept": float(intercept),
                    "r_squared": float(r_value ** 2),
                    "p_value": float(p_value),
                    "trend_direction": "increasing" if slope > 0 else "decreasing",
                    "trend_strength": "strong" if abs(r_value) > 0.7 else "moderate" if abs(r_value) > 0.3 else "weak"
                }
            
            # Moving average analysis
            if len(values) >= trend_period:
                ma = pd.Series(values).rolling(window=trend_period).mean()
                trend_analysis["moving_average"] = {
                    "period": trend_period,
                    "current_ma": float(ma.iloc[-1]) if not pd.isna(ma.iloc[-1]) else None,
                    "ma_values": ma.dropna().tolist()
                }
            
            # Volatility analysis
            if len(values) > 1:
                returns = np.diff(values) / values[:-1]
                trend_analysis["volatility"] = {
                    "volatility": float(np.std(returns)),
                    "returns_mean": float(np.mean(returns)),
                    "returns_std": float(np.std(returns))
                }
            
            logger.info(
                "Trend analysis completed",
                data_points=len(values),
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "analyze_trends",
                "trend_analysis": trend_analysis,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Trend analysis failed",
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _pattern_recognition(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Recognize patterns in data"""
        data = parameters.get("data")
        pattern_type = parameters.get("pattern_type", "general")
        
        if not data:
            raise ValueError("No data provided for pattern recognition")
        
        try:
            # Convert to DataFrame if needed
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame([data])
            
            patterns = {
                "data_shape": df.shape,
                "data_types": df.dtypes.to_dict(),
                "missing_values": df.isnull().sum().to_dict(),
                "unique_values": {col: df[col].nunique() for col in df.columns}
            }
            
            # Numerical pattern analysis
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                patterns["numerical_patterns"] = {}
                
                for col in numeric_columns:
                    values = df[col].dropna()
                    if len(values) > 0:
                        patterns["numerical_patterns"][col] = {
                            "distribution": self._analyze_distribution(values),
                            "outliers": self._detect_outliers(values),
                            "correlations": self._calculate_correlations(df, col)
                        }
            
            # Categorical pattern analysis
            categorical_columns = df.select_dtypes(include=['object']).columns
            if len(categorical_columns) > 0:
                patterns["categorical_patterns"] = {}
                
                for col in categorical_columns:
                    patterns["categorical_patterns"][col] = {
                        "value_counts": df[col].value_counts().to_dict(),
                        "most_common": df[col].mode().tolist() if len(df[col].mode()) > 0 else []
                    }
            
            # Time-based patterns (if time column exists)
            time_columns = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
            if time_columns:
                patterns["temporal_patterns"] = {}
                for col in time_columns:
                    try:
                        df[col] = pd.to_datetime(df[col])
                        patterns["temporal_patterns"][col] = {
                            "time_range": {
                                "start": df[col].min().isoformat(),
                                "end": df[col].max().isoformat()
                            },
                            "frequency": self._analyze_time_frequency(df[col])
                        }
                    except:
                        continue
            
            logger.info(
                "Pattern recognition completed",
                patterns_found=len(patterns),
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "pattern_recognition",
                "patterns": patterns,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Pattern recognition failed",
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _anomaly_detection(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in data"""
        data = parameters.get("data")
        method = parameters.get("method", "zscore")
        threshold = parameters.get("threshold", 3.0)
        
        if not data:
            raise ValueError("No data provided for anomaly detection")
        
        try:
            # Convert to DataFrame if needed
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame([data])
            
            anomalies = {}
            
            # Detect anomalies in numerical columns
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_columns:
                values = df[col].dropna()
                if len(values) > 0:
                    if method == "zscore":
                        anomalies[col] = self._zscore_anomaly_detection(values, threshold)
                    elif method == "iqr":
                        anomalies[col] = self._iqr_anomaly_detection(values)
                    elif method == "isolation_forest":
                        anomalies[col] = self._isolation_forest_anomaly_detection(values)
            
            # Summary statistics
            total_anomalies = sum(len(anomaly_list) for anomaly_list in anomalies.values())
            
            logger.info(
                "Anomaly detection completed",
                total_anomalies=total_anomalies,
                method=method,
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "anomaly_detection",
                "method": method,
                "threshold": threshold,
                "anomalies": anomalies,
                "total_anomalies": total_anomalies,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Anomaly detection failed",
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _statistical_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive statistical analysis"""
        data = parameters.get("data")
        analysis_type = parameters.get("analysis_type", "comprehensive")
        
        if not data:
            raise ValueError("No data provided for statistical analysis")
        
        try:
            # Convert to DataFrame if needed
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame([data])
            
            stats_analysis = {
                "data_overview": {
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "memory_usage": df.memory_usage(deep=True).sum()
                },
                "descriptive_stats": df.describe().to_dict(),
                "missing_data": {
                    "total_missing": df.isnull().sum().sum(),
                    "missing_percentage": (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100,
                    "missing_by_column": df.isnull().sum().to_dict()
                }
            }
            
            # Correlation analysis for numerical data
            numeric_df = df.select_dtypes(include=[np.number])
            if numeric_df.shape[1] > 1:
                correlation_matrix = numeric_df.corr()
                stats_analysis["correlations"] = {
                    "matrix": correlation_matrix.to_dict(),
                    "strong_correlations": self._find_strong_correlations(correlation_matrix, threshold=0.7)
                }
            
            # Distribution analysis
            if len(numeric_df.columns) > 0:
                stats_analysis["distributions"] = {}
                for col in numeric_df.columns:
                    values = numeric_df[col].dropna()
                    if len(values) > 0:
                        stats_analysis["distributions"][col] = {
                            "skewness": float(stats.skew(values)),
                            "kurtosis": float(stats.kurtosis(values)),
                            "normality_test": self._test_normality(values)
                        }
            
            logger.info(
                "Statistical analysis completed",
                analysis_type=analysis_type,
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "statistical_analysis",
                "analysis_type": analysis_type,
                "statistics": stats_analysis,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Statistical analysis failed",
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _clustering_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform clustering analysis on data"""
        data = parameters.get("data")
        n_clusters = parameters.get("n_clusters", 3)
        features = parameters.get("features", [])
        
        if not data:
            raise ValueError("No data provided for clustering analysis")
        
        try:
            # Convert to DataFrame if needed
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame([data])
            
            # Select features for clustering
            if features:
                df_cluster = df[features]
            else:
                # Use all numerical columns
                df_cluster = df.select_dtypes(include=[np.number])
            
            if df_cluster.shape[1] < 2:
                raise ValueError("Need at least 2 features for clustering")
            
            # Handle missing values
            df_cluster = df_cluster.dropna()
            
            if len(df_cluster) < n_clusters:
                raise ValueError(f"Not enough data points ({len(df_cluster)}) for {n_clusters} clusters")
            
            # Standardize features
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(df_cluster)
            
            # Perform K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(scaled_features)
            
            # Analyze clusters
            cluster_analysis = {
                "n_clusters": n_clusters,
                "n_samples": len(df_cluster),
                "features_used": list(df_cluster.columns),
                "cluster_sizes": np.bincount(cluster_labels).tolist(),
                "cluster_centers": kmeans.cluster_centers_.tolist(),
                "inertia": float(kmeans.inertia_),
                "silhouette_score": float(self._calculate_silhouette_score(scaled_features, cluster_labels))
            }
            
            # Add cluster assignments to original data
            df_cluster_with_labels = df_cluster.copy()
            df_cluster_with_labels['cluster'] = cluster_labels
            
            cluster_analysis["cluster_summaries"] = {}
            for i in range(n_clusters):
                cluster_data = df_cluster_with_labels[df_cluster_with_labels['cluster'] == i]
                cluster_analysis["cluster_summaries"][f"cluster_{i}"] = {
                    "size": len(cluster_data),
                    "mean_values": cluster_data.drop('cluster', axis=1).mean().to_dict(),
                    "std_values": cluster_data.drop('cluster', axis=1).std().to_dict()
                }
            
            logger.info(
                "Clustering analysis completed",
                n_clusters=n_clusters,
                n_samples=len(df_cluster),
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "clustering_analysis",
                "clustering_results": cluster_analysis,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Clustering analysis failed",
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _time_series_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform time series analysis"""
        data = parameters.get("data")
        time_column = parameters.get("time_column", "timestamp")
        value_column = parameters.get("value_column", "value")
        
        if not data:
            raise ValueError("No data provided for time series analysis")
        
        try:
            # Convert to DataFrame if needed
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame([data])
            
            # Ensure time column is datetime
            df[time_column] = pd.to_datetime(df[time_column])
            df = df.sort_values(time_column)
            
            # Set time as index
            df_ts = df.set_index(time_column)
            
            time_series_analysis = {
                "data_points": len(df_ts),
                "time_range": {
                    "start": df_ts.index.min().isoformat(),
                    "end": df_ts.index.max().isoformat(),
                    "duration_days": (df_ts.index.max() - df_ts.index.min()).days
                },
                "frequency_analysis": self._analyze_time_frequency(df_ts.index),
                "seasonality": self._detect_seasonality(df_ts[value_column]),
                "stationarity": self._test_stationarity(df_ts[value_column])
            }
            
            # Autocorrelation analysis
            if len(df_ts) > 10:
                time_series_analysis["autocorrelation"] = self._calculate_autocorrelation(df_ts[value_column])
            
            logger.info(
                "Time series analysis completed",
                data_points=len(df_ts),
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "time_series_analysis",
                "time_series_results": time_series_analysis,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Time series analysis failed",
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    # Helper methods for analysis
    def _analyze_distribution(self, values: np.ndarray) -> Dict[str, Any]:
        """Analyze the distribution of values"""
        return {
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "std": float(np.std(values)),
            "skewness": float(stats.skew(values)),
            "kurtosis": float(stats.kurtosis(values))
        }
    
    def _detect_outliers(self, values: np.ndarray, method: str = "iqr") -> List[int]:
        """Detect outliers in data"""
        if method == "iqr":
            Q1 = np.percentile(values, 25)
            Q3 = np.percentile(values, 75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = np.where((values < lower_bound) | (values > upper_bound))[0]
        else:  # zscore
            z_scores = np.abs(stats.zscore(values))
            outliers = np.where(z_scores > 3)[0]
        
        return outliers.tolist()
    
    def _calculate_correlations(self, df: pd.DataFrame, column: str) -> Dict[str, float]:
        """Calculate correlations with a specific column"""
        correlations = {}
        for col in df.select_dtypes(include=[np.number]).columns:
            if col != column:
                corr = df[column].corr(df[col])
                if not pd.isna(corr):
                    correlations[col] = float(corr)
        return correlations
    
    def _analyze_time_frequency(self, time_index: pd.DatetimeIndex) -> Dict[str, Any]:
        """Analyze the frequency of time series data"""
        if len(time_index) < 2:
            return {"frequency": "unknown", "regular": False}
        
        # Calculate time differences
        time_diffs = time_index.to_series().diff().dropna()
        
        if len(time_diffs) == 0:
            return {"frequency": "unknown", "regular": False}
        
        # Find most common time difference
        most_common_diff = time_diffs.mode().iloc[0] if len(time_diffs.mode()) > 0 else time_diffs.iloc[0]
        
        # Check if frequency is regular
        std_diff = time_diffs.std()
        mean_diff = time_diffs.mean()
        regularity = std_diff / mean_diff if mean_diff.total_seconds() > 0 else float('inf')
        
        return {
            "most_common_interval": str(most_common_diff),
            "mean_interval": str(mean_diff),
            "std_interval": str(std_diff),
            "regular": regularity < 0.1,  # Less than 10% variation
            "frequency": self._get_frequency_name(most_common_diff)
        }
    
    def _get_frequency_name(self, timedelta_obj: pd.Timedelta) -> str:
        """Convert timedelta to frequency name"""
        seconds = timedelta_obj.total_seconds()
        
        if seconds < 60:
            return "seconds"
        elif seconds < 3600:
            return "minutes"
        elif seconds < 86400:
            return "hours"
        elif seconds < 604800:
            return "days"
        elif seconds < 2592000:
            return "weeks"
        elif seconds < 31536000:
            return "months"
        else:
            return "years"
    
    def _zscore_anomaly_detection(self, values: np.ndarray, threshold: float = 3.0) -> List[int]:
        """Detect anomalies using Z-score method"""
        z_scores = np.abs(stats.zscore(values))
        return np.where(z_scores > threshold)[0].tolist()
    
    def _iqr_anomaly_detection(self, values: np.ndarray) -> List[int]:
        """Detect anomalies using IQR method"""
        Q1 = np.percentile(values, 25)
        Q3 = np.percentile(values, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return np.where((values < lower_bound) | (values > upper_bound))[0].tolist()
    
    def _isolation_forest_anomaly_detection(self, values: np.ndarray) -> List[int]:
        """Detect anomalies using Isolation Forest (placeholder)"""
        # This would require sklearn.ensemble.IsolationForest
        # For now, return empty list
        return []
    
    def _find_strong_correlations(self, correlation_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find strong correlations in correlation matrix"""
        strong_correlations = []
        
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) >= threshold:
                    strong_correlations.append({
                        "feature1": correlation_matrix.columns[i],
                        "feature2": correlation_matrix.columns[j],
                        "correlation": float(corr_value)
                    })
        
        return strong_correlations
    
    def _test_normality(self, values: np.ndarray) -> Dict[str, Any]:
        """Test for normality using Shapiro-Wilk test"""
        try:
            statistic, p_value = stats.shapiro(values)
            return {
                "statistic": float(statistic),
                "p_value": float(p_value),
                "is_normal": p_value > 0.05
            }
        except:
            return {"error": "Could not perform normality test"}
    
    def _calculate_silhouette_score(self, features: np.ndarray, labels: np.ndarray) -> float:
        """Calculate silhouette score for clustering quality"""
        try:
            from sklearn.metrics import silhouette_score
            return silhouette_score(features, labels)
        except:
            return 0.0
    
    def _detect_seasonality(self, series: pd.Series) -> Dict[str, Any]:
        """Detect seasonality in time series"""
        if len(series) < 12:
            return {"seasonality_detected": False, "reason": "Insufficient data"}
        
        # Simple seasonality detection using autocorrelation
        try:
            autocorr = series.autocorr(lag=1)
            return {
                "seasonality_detected": abs(autocorr) > 0.3,
                "autocorrelation_lag1": float(autocorr) if not pd.isna(autocorr) else 0.0
            }
        except:
            return {"seasonality_detected": False, "reason": "Could not calculate autocorrelation"}
    
    def _test_stationarity(self, series: pd.Series) -> Dict[str, Any]:
        """Test for stationarity using Augmented Dickey-Fuller test"""
        try:
            from statsmodels.tsa.stattools import adfuller
            result = adfuller(series.dropna())
            return {
                "statistic": float(result[0]),
                "p_value": float(result[1]),
                "is_stationary": result[1] < 0.05
            }
        except:
            return {"is_stationary": False, "reason": "Could not perform stationarity test"}
    
    def _calculate_autocorrelation(self, series: pd.Series, max_lag: int = 10) -> Dict[str, float]:
        """Calculate autocorrelation for different lags"""
        autocorr_dict = {}
        for lag in range(1, min(max_lag + 1, len(series) // 2)):
            try:
                autocorr = series.autocorr(lag=lag)
                if not pd.isna(autocorr):
                    autocorr_dict[f"lag_{lag}"] = float(autocorr)
            except:
                continue
        return autocorr_dict
    
    async def _analyze_stocks(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze stock market data"""
        # Check if we have stock data in the parameters
        # The new API passes stock data directly, while the old demo used hardcoded keys
        stock_data = {}
        
        # Look for stock data in various formats
        if "tesla" in parameters or "google" in parameters:
            # Legacy format from demo
            stock_data = parameters
        else:
            # New format - stock data is passed directly
            stock_data = parameters
        
        # Filter out non-stock data keys
        stock_data = {k: v for k, v in stock_data.items() 
                     if isinstance(v, dict) and "symbol" in v or "data" in v}
        
        if not stock_data:
            raise ValueError("No stock data provided for analysis")
        
        try:
            analysis_results = {
                "task_type": "analyze_stocks",
                "timestamp": datetime.utcnow().isoformat(),
                "stocks_analyzed": [],
                "market_overview": {},
                "trend_analysis": {},
                "volatility_analysis": {},
                "correlation_analysis": {}
            }
            
            # Analyze each stock
            for stock_key, data in stock_data.items():
                if not data:
                    continue
                    
                # Get stock name from data or use key
                stock_name = data.get("symbol", stock_key.upper())
                analysis_results["stocks_analyzed"].append(stock_name)
                
                # Extract price data
                historical_data = data.get("data", [])
                current_price = data.get("current_price", 0)
                volume = data.get("volume", 0)
                market_cap = data.get("market_cap", 0)
                
                if historical_data:
                    # Convert to DataFrame
                    df = pd.DataFrame(historical_data)
                    df['Date'] = pd.to_datetime(df['Date'])
                    df = df.sort_values('Date')
                    
                    # Price trend analysis
                    prices = df['Close'].values
                    returns = np.diff(prices) / prices[:-1]
                    
                    stock_analysis = {
                        "symbol": stock_name,
                        "current_price": float(current_price),
                        "volume": int(volume),
                        "market_cap": int(market_cap),
                        "price_trend": {
                            "mean_price": float(np.mean(prices)),
                            "price_volatility": float(np.std(returns)) if len(returns) > 0 else 0.0,
                            "price_change_30d": float((prices[-1] - prices[0]) / prices[0] * 100) if len(prices) > 0 else 0.0,
                            "trend_direction": "up" if prices[-1] > prices[0] else "down" if len(prices) > 0 else "stable"
                        },
                        "volume_analysis": {
                            "avg_volume": float(np.mean(df['Volume'].values)),
                            "volume_trend": "increasing" if df['Volume'].iloc[-1] > df['Volume'].iloc[0] else "decreasing" if len(df) > 0 else "stable"
                        }
                    }
                    
                    # Use stock name as key for analysis results
                    analysis_results[f"{stock_name.lower()}_analysis"] = stock_analysis
            
            # Market overview
            if len(analysis_results["stocks_analyzed"]) > 1:
                total_market_cap = sum([data.get("market_cap", 0) for data in stock_data.values()])
                analysis_results["market_overview"] = {
                    "total_market_cap": total_market_cap,
                    "stocks_analyzed": len(analysis_results["stocks_analyzed"]),
                    "market_sentiment": "bullish" if len(analysis_results["stocks_analyzed"]) > 0 else "neutral"
                }
            
            logger.info(
                "Stock analysis completed",
                stocks_analyzed=len(analysis_results["stocks_analyzed"]),
                agent_id=self.agent_id
            )
            
            return analysis_results
            
        except Exception as e:
            logger.error(
                "Stock analysis failed",
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _analyze_forex(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze forex market data"""
        forex_data = parameters.get("forex_data", {})
        pairs = parameters.get("pairs", [])
        
        if not forex_data:
            raise ValueError("No forex data provided for analysis")
        
        try:
            analysis_results = {
                "task_type": "analyze_forex",
                "timestamp": datetime.utcnow().isoformat(),
                "pairs_analyzed": [],
                "market_overview": {},
                "pair_analysis": {},
                "correlation_analysis": {}
            }
            
            # Analyze each currency pair
            for pair, data in forex_data.items():
                if not data:
                    continue
                    
                analysis_results["pairs_analyzed"].append(pair)
                
                current_rate = data.get("current_rate", 0)
                change_24h = data.get("change_24h", 0)
                change_percent = data.get("change_percent", 0)
                high_24h = data.get("high_24h", 0)
                low_24h = data.get("low_24h", 0)
                
                pair_analysis = {
                    "current_rate": float(current_rate),
                    "change_24h": float(change_24h),
                    "change_percent": float(change_percent),
                    "high_24h": float(high_24h),
                    "low_24h": float(low_24h),
                    "volatility": float((high_24h - low_24h) / current_rate * 100) if current_rate > 0 else 0.0,
                    "trend": "bullish" if change_percent > 0 else "bearish" if change_percent < 0 else "neutral"
                }
                
                analysis_results["pair_analysis"][pair] = pair_analysis
            
            # Market overview
            if len(analysis_results["pairs_analyzed"]) > 0:
                bullish_pairs = sum(1 for pair_data in analysis_results["pair_analysis"].values() 
                                  if pair_data["trend"] == "bullish")
                bearish_pairs = sum(1 for pair_data in analysis_results["pair_analysis"].values() 
                                  if pair_data["trend"] == "bearish")
                
                analysis_results["market_overview"] = {
                    "total_pairs": len(analysis_results["pairs_analyzed"]),
                    "bullish_pairs": bullish_pairs,
                    "bearish_pairs": bearish_pairs,
                    "neutral_pairs": len(analysis_results["pairs_analyzed"]) - bullish_pairs - bearish_pairs,
                    "market_sentiment": "bullish" if bullish_pairs > bearish_pairs else "bearish" if bearish_pairs > bullish_pairs else "neutral"
                }
            
            logger.info(
                "Forex analysis completed",
                pairs_analyzed=len(analysis_results["pairs_analyzed"]),
                agent_id=self.agent_id
            )
            
            return analysis_results
            
        except Exception as e:
            logger.error(
                "Forex analysis failed",
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _analyze_crypto(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cryptocurrency market data"""
        crypto_data = parameters.get("crypto_data", {})
        
        if not crypto_data:
            raise ValueError("No cryptocurrency data provided for analysis")
        
        try:
            analysis_results = {
                "task_type": "analyze_crypto",
                "timestamp": datetime.utcnow().isoformat(),
                "cryptos_analyzed": [],
                "market_overview": {},
                "crypto_analysis": {},
                "market_cap_analysis": {},
                "volatility_analysis": {}
            }
            
            total_market_cap = 0
            total_volume_24h = 0
            crypto_analyses = []
            
            # Analyze each cryptocurrency
            for symbol, data in crypto_data.items():
                if not data:
                    continue
                    
                analysis_results["cryptos_analyzed"].append(symbol)
                
                current_price = data.get("current_price", 0)
                volume_24h = data.get("volume_24h", 0)
                market_cap = data.get("market_cap", 0)
                price_change_24h = data.get("price_change_24h", 0)
                price_change_percent = data.get("price_change_percent", 0)
                high_24h = data.get("high_24h", 0)
                low_24h = data.get("low_24h", 0)
                historical_data = data.get("historical_data", [])
                
                total_market_cap += market_cap
                total_volume_24h += volume_24h
                
                crypto_analysis = {
                    "symbol": symbol,
                    "current_price": float(current_price),
                    "volume_24h": int(volume_24h),
                    "market_cap": int(market_cap),
                    "price_change_24h": float(price_change_24h),
                    "price_change_percent": float(price_change_percent),
                    "high_24h": float(high_24h),
                    "low_24h": float(low_24h),
                    "volatility": float((high_24h - low_24h) / current_price * 100) if current_price > 0 else 0.0,
                    "trend": "bullish" if price_change_percent > 0 else "bearish" if price_change_percent < 0 else "neutral"
                }
                
                # Historical analysis if available
                if historical_data:
                    df = pd.DataFrame(historical_data)
                    df['Date'] = pd.to_datetime(df['Date'])
                    df = df.sort_values('Date')
                    
                    prices = df['Close'].values
                    if len(prices) > 0:
                        returns = np.diff(prices) / prices[:-1]
                        crypto_analysis["historical_analysis"] = {
                            "price_range": {
                                "min": float(np.min(prices)),
                                "max": float(np.max(prices)),
                                "current": float(current_price)
                            },
                            "volatility_30d": float(np.std(returns)) if len(returns) > 0 else 0.0,
                            "price_change_30d": float((prices[-1] - prices[0]) / prices[0] * 100) if len(prices) > 0 else 0.0
                        }
                
                crypto_analyses.append(crypto_analysis)
                analysis_results["crypto_analysis"][symbol] = crypto_analysis
            
            # Market overview
            if len(analysis_results["cryptos_analyzed"]) > 0:
                bullish_cryptos = sum(1 for crypto_data in crypto_analyses if crypto_data["trend"] == "bullish")
                bearish_cryptos = sum(1 for crypto_data in crypto_analyses if crypto_data["trend"] == "bearish")
                
                analysis_results["market_overview"] = {
                    "total_cryptos": len(analysis_results["cryptos_analyzed"]),
                    "total_market_cap": int(total_market_cap),
                    "total_volume_24h": int(total_volume_24h),
                    "bullish_cryptos": bullish_cryptos,
                    "bearish_cryptos": bearish_cryptos,
                    "neutral_cryptos": len(analysis_results["cryptos_analyzed"]) - bullish_cryptos - bearish_cryptos,
                    "market_sentiment": "bullish" if bullish_cryptos > bearish_cryptos else "bearish" if bearish_cryptos > bullish_cryptos else "neutral"
                }
                
                # Volatility analysis
                volatilities = [crypto["volatility"] for crypto in crypto_analyses]
                analysis_results["volatility_analysis"] = {
                    "avg_volatility": float(np.mean(volatilities)) if volatilities else 0.0,
                    "max_volatility": float(np.max(volatilities)) if volatilities else 0.0,
                    "min_volatility": float(np.min(volatilities)) if volatilities else 0.0
                }
            
            logger.info(
                "Cryptocurrency analysis completed",
                cryptos_analyzed=len(analysis_results["cryptos_analyzed"]),
                agent_id=self.agent_id
            )
            
            return analysis_results
            
        except Exception as e:
            logger.error(
                "Cryptocurrency analysis failed",
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _handle_analysis_request(self, message: Message) -> Optional[Message]:
        """Handle analysis requests from other agents"""
        content = message.content
        analysis_type = content.get("analysis_type")
        parameters = content.get("parameters", {})
        
        try:
            if analysis_type == "trend_analysis":
                result = await self._analyze_trends(parameters)
            elif analysis_type == "pattern_recognition":
                result = await self._pattern_recognition(parameters)
            elif analysis_type == "anomaly_detection":
                result = await self._anomaly_detection(parameters)
            elif analysis_type == "statistical_analysis":
                result = await self._statistical_analysis(parameters)
            elif analysis_type == "clustering_analysis":
                result = await self._clustering_analysis(parameters)
            elif analysis_type == "time_series_analysis":
                result = await self._time_series_analysis(parameters)
            elif analysis_type == "analyze_stocks":
                result = await self._analyze_stocks(parameters)
            elif analysis_type == "analyze_forex":
                result = await self._analyze_forex(parameters)
            elif analysis_type == "analyze_crypto":
                result = await self._analyze_crypto(parameters)
            else:
                result = {"error": f"Unknown analysis type: {analysis_type}"}
            
            # Send response message
            response = Message(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="analysis_response",
                content=result,
                correlation_id=message.id
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Analysis request handling failed",
                analysis_type=analysis_type,
                error=str(e),
                agent_id=self.agent_id
            )
            
            response = Message(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="analysis_response",
                content={"error": str(e)},
                correlation_id=message.id
            )
            
            return response
    
    async def _handle_data_update(self, message: Message) -> Optional[Message]:
        """Handle data updates from other agents"""
        content = message.content
        data_id = content.get("data_id")
        
        # Clear relevant cache entries
        if data_id:
            cache_keys_to_clear = [key for key in self.analysis_cache.keys() if data_id in key]
            for key in cache_keys_to_clear:
                del self.analysis_cache[key]
        
        logger.info(
            "Data update handled",
            data_id=data_id,
            cache_cleared=len(cache_keys_to_clear) if data_id else 0,
            agent_id=self.agent_id
        )
        
        return None


# Factory function to create analyzer agent
def create_analyzer_agent(agent_id: str = None) -> AnalyzerAgent:
    """Create and return a new Analyzer Agent instance"""
    return AnalyzerAgent(agent_id) 