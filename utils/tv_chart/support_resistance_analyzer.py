
import numpy as np
from sklearn.cluster import KMeans

from collections import defaultdict
from functools import partial



class SupportResistanceAnalyzer:

    """
    """
    def __init__(self, df):
        self.df = df
        self.results = {}
    
    def fibonacci_levels(self):
        try:
            high = self.df['high'].max()
            low = self.df['low'].min()
            diff = high - low
            
            levels = {
                '0%': high,
                '23.6%': high - diff * 0.236,
                '38.2%': high - diff * 0.382,
                '50%': high - diff * 0.5,
                '61.8%': high - diff * 0.618,
                '100%': low
            }
            self.results['Fibonacci'] = levels
        except Exception as e:
            print(f"Error in fibonacci_levels: {str(e)}")
            self.results['Fibonacci'] = "N/A"
    
    def pivot_points(self, window=10, significance=3):
        try:
            if len(self.df) < window:
                raise ValueError("Insufficient data for pivot points")
                
            # 使用更平滑的极值检测
            self.df['local_max'] = self.df['high'].rolling(window=window, center=True).apply(
                lambda x: x.max() if (x.argmax() in [window//2-1, window//2]) else np.nan)
            self.df['local_min'] = self.df['low'].rolling(window=window, center=True).apply(
                lambda x: x.min() if (x.argmin() in [window//2-1, window//2]) else np.nan)
            
            # 筛选显著水平
            resistance = self.df['local_max'].dropna()
            support = self.df['local_min'].dropna()
            
            # 合并邻近水平（0.5%以内视为同一水平）
            resistance = self._cluster_levels(resistance, threshold=0.005)
            support = self._cluster_levels(support, threshold=0.005)
            
            self.results['Pivot Points'] = {
                'Support': support,
                'Resistance': resistance
            }
        except Exception as e:
            print(f"Error in pivot_points: {str(e)}")
            self.results['Pivot Points'] = "N/A"
    
    def _cluster_levels(self, levels, threshold=0.005):
        if len(levels) == 0:
            return []
            
        clustered = []
        mean_price = np.mean(levels)
        dynamic_threshold = mean_price * threshold
        
        for level in sorted(levels):
            if not clustered:
                clustered.append([level])
            else:
                last_group = clustered[-1]
                if abs(level - np.mean(last_group)) <= dynamic_threshold:
                    last_group.append(level)
                else:
                    clustered.append([level])
        return [round(np.mean(group), 2) for group in clustered]

    def bollinger_bands(self):
        try:
            window = 20
            if len(self.df) < window:
                raise ValueError("Insufficient data for Bollinger Bands")
                
            close = self.df['close']
            middle = close.rolling(window=window).mean()
            std = close.rolling(window=window).std()
            
            upper = middle + (std * 2)
            lower = middle - (std * 2)
            
            self.results['Bollinger Bands'] = {
                'Support': lower.iloc[-1],
                'Resistance': upper.iloc[-1]
            }
        except Exception as e:
            print(f"Error in bollinger_bands: {str(e)}")
            self.results['Bollinger Bands'] = "N/A"
    
    def kmeans_clusters(self, n_clusters=5):
        try:
            if len(self.df) < n_clusters:
                raise ValueError("Insufficient data for KMeans")
                
            prices = self.df[['close']].values
            kmeans = KMeans(n_clusters=n_clusters).fit(prices)
            levels = sorted([x[0] for x in kmeans.cluster_centers_])
            self.results['KMeans Clusters'] = levels
        except Exception as e:
            print(f"Error in kmeans_clusters: {str(e)}")
            self.results['KMeans Clusters'] = "N/A"
    
    def volume_profile(self, price_step=0.5):
        try:
            if len(self.df) < 20:
                raise ValueError("Insufficient data for Volume Profile")
                
            # 根据价格波动动态设定区间
            price_range = np.arange(
                np.floor(self.df['low'].min()),
                np.ceil(self.df['high'].max()) + price_step,
                price_step
            )
            
            volume_at_price = []
            for i in range(1, len(price_range)):
                mask = (self.df['high'] >= price_range[i-1]) & (self.df['low'] <= price_range[i])
                volume_at_price.append({
                    'price': (price_range[i-1] + price_range[i]) / 2,
                    'volume': self.df[mask]['volume'].sum()
                })
            
            # 寻找成交量显著高于平均的区间
            volumes = [x['volume'] for x in volume_at_price if x['volume'] > 0]
            if not volumes:
                self.results['Volume Profile'] = []
                return
                
            mean_vol = np.mean(volumes)
            std_vol = np.std(volumes)
            significant_levels = [
                x['price'] for x in volume_at_price
                if x['volume'] > mean_vol + std_vol
            ]
            
            self.results['Volume Profile'] = significant_levels
        except Exception as e:
            print(f"Error in volume_profile: {str(e)}")
            self.results['Volume Profile'] = "N/A"
            
    def trendlines(self, window=20, angle_threshold=5):
        try:
            if len(self.df) < window:
                raise ValueError("Insufficient data for Trendlines")
                
            valid_support = []
            valid_resistance = []
            
            # 使用随机采样提高性能
            sample_indices = np.random.choice(
                range(window, len(self.df)),
                size=min(50, len(self.df)-window),
                replace=False
            )
            
            for i in sample_indices:
                # 支撑趋势线
                recent_lows = self.df['low'].iloc[i-window:i]
                slope, intercept = self._robust_regression(recent_lows)
                angle = np.degrees(np.arctan(slope))
                
                if slope < 0 and abs(angle) > angle_threshold:
                    valid_support.append(intercept + slope*(window-1))
                
                # 阻力趋势线
                recent_highs = self.df['high'].iloc[i-window:i]
                slope, intercept = self._robust_regression(recent_highs)
                angle = np.degrees(np.arctan(slope))
                
                if slope > 0 and abs(angle) > angle_threshold:
                    valid_resistance.append(intercept + slope*(window-1))
            
            current_support = np.mean(valid_support[-3:]) if valid_support else None
            current_resistance = np.mean(valid_resistance[-3:]) if valid_resistance else None
                
            self.results['Trendlines'] = {
                'Current Support': current_support,
                'Current Resistance': current_resistance
            }
        except Exception as e:
            print(f"Error in trendlines: {str(e)}")
            self.results['Trendlines'] = "N/A"

    def _robust_regression(self, series):
        """使用改进的Theil-Sen算法"""
        x = np.arange(len(series))
        indices = np.random.choice(len(series), size=min(50, len(series)), replace=False)
        slopes = []
        for i in indices:
            for j in indices:
                if j > i:
                    slopes.append((series.iloc[j] - series.iloc[i]) / (j - i))
        slope = np.median(slopes)
        intercept = np.median(series - slope*x)
        return slope, intercept
        
    def run_all_analysis(self):
        methods = [
            ('Fibonacci', self.fibonacci_levels),
            ('Pivot Points', partial(self.pivot_points, window=10)),
            ('Bollinger Bands', self.bollinger_bands),
            ('KMeans Clusters', partial(self.kmeans_clusters, n_clusters=5)),
            ('Volume Profile', self.volume_profile),
            ('Trendlines', self.trendlines)
        ]
        
        for name, method in methods:
            try:
                method()
            except Exception as e:
                print(f"Method {name} failed: {str(e)}")
                self.results[name] = "N/A"
        
        return self.results

    def get_all_levels(self):
        """Return all support and resistance levels in a structured way"""
        support_levels = []
        resistance_levels = []
        
        # Extract levels from results
        for method, values in self.results.items():
            if values == "N/A":
                continue
                
            if isinstance(values, dict):
                # For methods that return a dict with 'Support' and 'Resistance' keys
                if 'Support' in values:
                    if isinstance(values['Support'], (float, int, np.floating)):
                        support_levels.append((method, values['Support']))
                    elif isinstance(values['Support'], (list, np.ndarray)):
                        for level in values['Support']:
                            support_levels.append((method, level))
                if 'Resistance' in values:
                    if isinstance(values['Resistance'], (float, int, np.floating)):
                        resistance_levels.append((method, values['Resistance']))
                    elif isinstance(values['Resistance'], (list, np.ndarray)):
                        for level in values['Resistance']:
                            resistance_levels.append((method, level))
                            
                # Special case for Fibonacci levels
                if method == 'Fibonacci':
                    for key, value in values.items():
                        if key in ['0%', '23.6%', '38.2%']:
                            resistance_levels.append((f"Fib {key}", value))
                        elif key in ['61.8%', '100%']:
                            support_levels.append((f"Fib {key}", value))
                        elif key == '50%':
                            resistance_levels.append((f"Fib {key}", value))
                            support_levels.append((f"Fib {key}", value))
            
            # For methods that return a list of levels (like KMeans)
            elif isinstance(values, list):
                if values:
                    support_levels.append((method, min(values)))
                    resistance_levels.append((method, max(values)))
                    
            # For methods that return a single value (like Volume Profile)
            elif isinstance(values, (float, int, np.floating)):
                support_levels.append((method, values))
                resistance_levels.append((method, values))
                
        # Calculate importance scores
        level_scores = defaultdict(float)
        current_price = self.df['close'].iloc[-1]
        
        method_weights = {
            'Volume Profile': 2.0,
            'Pivot Points': 1.5,
            'Trendlines': 1.2,
            'Fibonacci': 1.0,
            'Bollinger Bands': 0.8,
            'KMeans Clusters': 0.5
        }
        
        for level_type in ['Support', 'Resistance']:
            levels = support_levels if level_type == 'Support' else resistance_levels
            for method, value in levels:
                weight = method_weights.get(method, 1.0)
                proximity = 1.5 if abs(value - current_price)/current_price < 0.02 else 1.0
                level_scores[(level_type, value)] += weight * proximity
        
        # Merge nearby levels (within 0.5%)
        merged_levels = {'Support': [], 'Resistance': []}
        tolerance = current_price * 0.005
        
        for level_type in ['Support', 'Resistance']:
            levels = support_levels if level_type == 'Support' else resistance_levels
            sorted_levels = sorted(levels, key=lambda x: x[1])
            current_group = []
            
            for method, value in sorted_levels:
                if not current_group:
                    current_group.append((method, value))
                else:
                    last_value = current_group[-1][1]
                    if abs(value - last_value) <= tolerance:
                        current_group.append((method, value))
                    else:
                        # Merge group and keep the most significant
                        best_method = max(
                            [(m, level_scores[(level_type, v)]) for m, v in current_group],
                            key=lambda x: x[1]
                        )[0]
                        merged_value = np.mean([v for _, v in current_group])
                        merged_levels[level_type].append((best_method, round(merged_value, 2)))
                        current_group = [(method, value)]
            
            if current_group:
                best_method = max(
                    [(m, level_scores[(level_type, v)]) for m, v in current_group],
                    key=lambda x: x[1]
                )[0]
                merged_value = np.mean([v for _, v in current_group])
                merged_levels[level_type].append((best_method, round(merged_value, 2)))
        
        return merged_levels
    
    def print_result(self, symbol="N/A"):
        
        # 輸出支撐阻力分析報告
        print(f"\n📈 Support & Resistance Analysis Report for {symbol}")
        print("="*60)
        for method, values in self.results.items():
            if values == "N/A":
                print(f"\n🔍 {method}: Not available")
                continue
                
            print(f"\n🔍 {method}:")
            if isinstance(values, dict):
                for k, v in values.items():
                    if isinstance(v, (float, np.floating)):
                        print(f"  • {k}: {v:.2f}")
                    elif isinstance(v, (list, np.ndarray)):
                        print(f"  • {k}: {np.unique(np.array(v).round(2))}")
                    else:
                        print(f"  • {k}: {v}")
            elif isinstance(values, list):
                print(f"  • Levels: {np.unique(np.array(values).round(2))}")
            elif isinstance(values, (float, int, np.floating)):
                print(f"  • Value: {values:.2f}")

