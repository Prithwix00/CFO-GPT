from typing import List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """Analyzes trends in financial data"""
    
    def __init__(self):
        self.moving_average_window = 3  # months
    
    def analyze_spending_trends(self, financial_data: List[Dict]) -> Dict[str, Any]:
        """Analyze spending trends over time"""
        
        if not financial_data:
            return {"error": "No financial data provided"}
        
        df = pd.DataFrame(financial_data)
        
        # Ensure required columns
        required_cols = ['period', 'actual_amount', 'department']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            return {"error": f"Missing required columns: {missing_cols}"}
        
        # Convert period to datetime
        df['period_date'] = pd.to_datetime(df['period'] + '-01', format='Y%-m%-%d', errors='coerce')
        df = df.sort_values('period_date')
        
        # Overall trends
        overall_trend = df.groupby('period_date').agg({
            'actual_amount': 'sum'
        }).reset_index()
        
        # Calculate moving average
        overall_trend['moving_average'] = overall_trend['actual_amount'].rolling(
            window=min(self.moving_average_window, len(overall_trend)),
            min_periods=1
        ).mean()
        
        # Department trends
        dept_trends = {}
        for dept in df['department'].unique():
            dept_data = df[df['department'] == dept]
            dept_trend = dept_data.groupby('period_date').agg({
                'actual_amount': 'sum'
            }).reset_index()
            
            if len(dept_trend) >= 2:
                dept_trend['growth_rate'] = dept_trend['actual_amount'].pct_change() * 100
                dept_trends[dept] = dept_trend.to_dict('records')
        
        # Seasonality analysis
        seasonality = self._analyze_seasonality(overall_trend)
        
        # Trend detection
        trend_detection = self._detect_trends(overall_trend)
        
        # Anomaly detection
        anomalies = self._detect_anomalies(overall_trend)
        
        return {
            'overall_trend': overall_trend.to_dict('records'),
            'department_trends': dept_trends,
            'seasonality_analysis': seasonality,
            'trend_detection': trend_detection,
            'anomalies': anomalies,
            'summary': self._generate_trend_summary(overall_trend, dept_trends, trend_detection)
        }
    
    def _analyze_seasonality(self, trend_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze seasonal patterns in spending"""
        
        if len(trend_data) < 12:  # Need at least 1 year of monthly data
            return {"warning": "Insufficient data for seasonality analysis"}
        
        # Extract month from period
        trend_data['month'] = trend_data['period_date'].dt.month
        
        # Calculate average by month
        monthly_avg = trend_data.groupby('month').agg({
            'actual_amount': 'mean'
        }).reset_index()
        
        # Calculate seasonal indices
        overall_avg = trend_data['actual_amount'].mean()
        monthly_avg['seasonal_index'] = (monthly_avg['actual_amount'] / overall_avg * 100)
        
        # Identify high and low seasons
        high_season = monthly_avg[monthly_avg['seasonal_index'] > 105]
        low_season = monthly_avg[monthly_avg['seasonal_index'] < 95]
        
        return {
            'monthly_patterns': monthly_avg.to_dict('records'),
            'high_season_months': high_season['month'].tolist(),
            'low_season_months': low_season['month'].tolist(),
            'seasonality_strength': self._calculate_seasonality_strength(monthly_avg['seasonal_index'])
        }
    
    def _calculate_seasonality_strength(self, seasonal_indices: pd.Series) -> float:
        """Calculate strength of seasonality"""
        # Coefficient of variation of seasonal indices
        mean = seasonal_indices.mean()
        std = seasonal_indices.std()
        
        if mean == 0:
            return 0.0
        
        return float((std / mean) * 100)
    
    def _detect_trends(self, trend_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect upward/downward trends"""
        
        if len(trend_data) < 2:
            return {"warning": "Insufficient data for trend detection"}
        
        # Linear regression
        x = np.arange(len(trend_data))
        y = trend_data['actual_amount'].values
        
        coeff = np.polyfit(x, y, 1)
        slope = coeff[0]
        
        # Calculate R-squared
        y_pred = coeff[0] * x + coeff[1]
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Determine trend direction and strength
        if slope > 0:
            direction = "upward"
            strength = "strong" if r_squared > 0.7 else "moderate" if r_squared > 0.3 else "weak"
        elif slope < 0:
            direction = "downward"
            strength = "strong" if r_squared > 0.7 else "moderate" if r_squared > 0.3 else "weak"
        else:
            direction = "stable"
            strength = "no trend"
        
        return {
            'direction': direction,
            'strength': strength,
            'slope': float(slope),
            'r_squared': float(r_squared),
            'monthly_growth_rate': float(slope / np.mean(y) * 100) if np.mean(y) != 0 else 0
        }
    
    def _detect_anomalies(self, trend_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies in spending patterns"""
        
        if len(trend_data) < 3:
            return []
        
        # Calculate z-scores
        mean = trend_data['actual_amount'].mean()
        std = trend_data['actual_amount'].std()
        
        anomalies = []
        
        if std > 0:
            trend_data['z_score'] = (trend_data['actual_amount'] - mean) / std
            
            # Identify anomalies (z-score > 2 or < -2)
            anomaly_mask = abs(trend_data['z_score']) > 2
            
            for _, row in trend_data[anomaly_mask].iterrows():
                anomalies.append({
                    'period': row['period_date'].strftime('%Y-%m'),
                    'amount': float(row['actual_amount']),
                    'z_score': float(row['z_score']),
                    'deviation': f"{abs(row['z_score']):.1f} standard deviations",
                    'direction': 'above' if row['z_score'] > 0 else 'below'
                })
        
        return anomalies
    
    def _generate_trend_summary(self, 
                               overall_trend: pd.DataFrame,
                               dept_trends: Dict[str, List],
                               trend_detection: Dict) -> str:
        """Generate summary of trend analysis"""
        
        summary_parts = []
        
        # Overall trend
        if trend_detection.get('direction') != 'stable':
            summary_parts.append(
                f"Overall spending shows a {trend_detection['strength']} {trend_detection['direction']} "
                f"trend with monthly growth rate of {trend_detection.get('monthly_growth_rate', 0):.1f}%."
            )
        else:
            summary_parts.append("Overall spending appears stable with no strong trend.")
        
        # Department trends
        if dept_trends:
            growing_depts = []
            declining_depts = []
            
            for dept, data in dept_trends.items():
                if len(data) >= 2:
                    first = data[0]['actual_amount']
                    last = data[-1]['actual_amount']
                    if first > 0:
                        growth = (last - first) / first * 100
                        if growth > 10:
                            growing_depts.append(f"{dept} (+{growth:.1f}%)")
                        elif growth < -10:
                            declining_depts.append(f"{dept} ({growth:.1f}%)")
            
            if growing_depts:
                summary_parts.append(f"Fastest growing departments: {', '.join(growing_depts[:3])}")
            if declining_depts:
                summary_parts.append(f"Departments with declining spend: {', '.join(declining_depts[:3])}")
        
        # Anomalies would be added here if detected
        
        return " ".join(summary_parts)
    
    def forecast_budget_requirements(self, 
                                    historical_data: List[Dict],
                                    forecast_periods: int = 6) -> Dict[str, Any]:
        """Forecast future budget requirements"""
        
        if not historical_data:
            return {"error": "No historical data provided"}
        
        df = pd.DataFrame(historical_data)
        
        # Ensure required columns
        if 'period' not in df.columns or 'actual_amount' not in df.columns:
            return {"error": "Required columns missing"}
        
        # Convert period to datetime and sort
        df['period_date'] = pd.to_datetime(df['period'] + '-01', format='%Y-%m-%d', errors='coerce')
        df = df.sort_values('period_date')
        
        # Group by period
        period_data = df.groupby('period_date').agg({
            'actual_amount': 'sum'
        }).reset_index()
        
        if len(period_data) < 2:
            return {"error": "Insufficient data for forecasting"}
        
        # Time series forecasting using simple methods
        forecasts = {}
        
        # Method 1: Simple moving average
        if len(period_data) >= 3:
            last_values = period_data['actual_amount'].tail(3).values
            ma_forecast = np.mean(last_values)
            forecasts['moving_average'] = {
                'method': '3-month moving average',
                'next_period': float(ma_forecast),
                'confidence': 0.7
            }
        
        # Method 2: Linear regression
        x = np.arange(len(period_data))
        y = period_data['actual_amount'].values
        
        coeff = np.polyfit(x, y, 1)
        lr_forecast = coeff[0] * len(period_data) + coeff[1]
        
        forecasts['linear_regression'] = {
            'method': 'Linear regression',
            'next_period': float(lr_forecast),
            'confidence': 0.8,
            'trend_strength': abs(coeff[0]) / np.mean(y) * 100 if np.mean(y) != 0 else 0
        }
        
        # Method 3: Seasonal adjustment (if enough data)
        if len(period_data) >= 12:
            # Simple seasonal adjustment
            period_data['month'] = period_data['period_date'].dt.month
            monthly_avg = period_data.groupby('month')['actual_amount'].mean()
            
            last_month = period_data['month'].iloc[-1]
            next_month = (last_month % 12) + 1
            
            seasonal_factor = monthly_avg[next_month] / monthly_avg.mean() if monthly_avg.mean() != 0 else 1
            
            # Use linear regression forecast with seasonal adjustment
            seasonal_forecast = lr_forecast * seasonal_factor
            
            forecasts['seasonal_adjusted'] = {
                'method': 'Seasonally adjusted regression',
                'next_period': float(seasonal_forecast),
                'confidence': 0.85,
                'seasonal_factor': float(seasonal_factor)
            }
        
        # Generate forecast for multiple periods
        multi_period_forecast = []
        last_date = period_data['period_date'].iloc[-1]
        
        for i in range(1, forecast_periods + 1):
            forecast_date = last_date + pd.DateOffset(months=i)
            
            # Simple projection using best method
            if 'seasonal_adjusted' in forecasts:
                base_forecast = forecasts['seasonal_adjusted']['next_period']
            elif 'linear_regression' in forecasts:
                base_forecast = forecasts['linear_regression']['next_period']
            else:
                base_forecast = forecasts['moving_average']['next_period']
            
            # Apply growth rate
            growth_rate = forecasts['linear_regression'].get('trend_strength', 0) / 100
            period_forecast = base_forecast * (1 + growth_rate) ** i
            
            multi_period_forecast.append({
                'period': forecast_date.strftime('%Y-%m'),
                'forecast_amount': float(period_forecast),
                'growth_rate': float(growth_rate * 100)
            })
        
        return {
            'historical_data': period_data.to_dict('records'),
            'forecasting_methods': forecasts,
            'recommended_forecast': forecasts.get('seasonal_adjusted', forecasts.get('linear_regression', {})),
            'multi_period_forecast': multi_period_forecast,
            'confidence_intervals': self._calculate_forecast_confidence(period_data['actual_amount'].values)
        }
    
    def _calculate_forecast_confidence(self, historical_values: np.ndarray) -> Dict[str, float]:
        """Calculate confidence intervals for forecasts"""
        
        if len(historical_values) < 2:
            return {'lower_95': 0, 'upper_95': 0, 'lower_68': 0, 'upper_68': 0}
        
        mean = np.mean(historical_values)
        std = np.std(historical_values)
        
        return {
            'lower_95': float(mean - 1.96 * std),
            'upper_95': float(mean + 1.96 * std),
            'lower_68': float(mean - std),
            'upper_68': float(mean + std)
        }