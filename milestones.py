"""Milestone detection and tweeting system for Cuánto Le Falta bot."""
import datetime
import json
import os
from typing import Dict, List, Optional, Tuple


# Dry-run mode flag - set to True to test without posting
DRY_RUN = False

# Cooldown period in seconds (5 minutes)
COOLDOWN_SECONDS = 5 * 60

# Persistence file
PERSISTENCE_FILE = "milestones_tweeted.json"


class MilestoneChecker:
    """Detects and tweets milestone moments."""
    
    def __init__(self, client, start: datetime.datetime, end: datetime.datetime, timezone):
        self.client = client
        self.start = start
        self.end = end
        self.timezone = timezone
        
        # Previous check values (for crossing detection)
        self.prev_remaining_seconds: Optional[float] = None
        self.prev_elapsed_seconds: Optional[float] = None
        
        # Cooldown tracking
        self.last_milestone_tweet_time: Optional[datetime.datetime] = None
        
        # Load persistence
        self.tweeted_milestones = self._load_persistence()
        
        # Initialize with already-passed milestones
        self._seed_already_passed()
    
    def _load_persistence(self) -> set:
        """Load tweeted milestones from JSON file."""
        if not os.path.exists(PERSISTENCE_FILE):
            return set()
        
        try:
            with open(PERSISTENCE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tweeted = data.get('tweeted', [])
                # Create set of (unit, value) tuples for fast lookup
                return {(item['unit'], item['value']) for item in tweeted}
        except (json.JSONDecodeError, KeyError, IOError) as e:
            print(f"Warning: Could not load persistence file: {e}")
            return set()
    
    def _save_persistence(self, unit: str, value: float):
        """Save a tweeted milestone to JSON file."""
        milestone_entry = {
            'unit': unit,
            'value': value,
            'tweeted_at': datetime.datetime.now(self.timezone).isoformat()
        }
        
        # Load existing data
        if os.path.exists(PERSISTENCE_FILE):
            try:
                with open(PERSISTENCE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError):
                data = {'tweeted': []}
        else:
            data = {'tweeted': []}
        
        # Append new entry
        data['tweeted'].append(milestone_entry)
        
        # Save back
        try:
            with open(PERSISTENCE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save persistence file: {e}")
    
    def _seed_already_passed(self):
        """Pre-seed milestones that have already passed (as of ~Feb 22, 2026)."""
        already_passed = [
            ('days_remaining', 2000),
            ('seconds_remaining', 150000000),
            ('days_elapsed', 100),
            ('days_elapsed', 200),
            ('days_elapsed', 365),
            ('days_elapsed', 500),
            ('percentage', 5),
            ('percentage', 10),
            ('percentage', 15),
            ('percentage', 20),
        ]
        
        for unit, value in already_passed:
            if (unit, value) not in self.tweeted_milestones:
                self.tweeted_milestones.add((unit, value))
                # Also save to persistence
                self._save_persistence(unit, value)
    
    def _crossed_threshold(self, prev_value: Optional[float], curr_value: float, threshold: float, direction: str) -> bool:
        """Check if we crossed a threshold.
        
        Args:
            prev_value: Previous check value (None on first run)
            curr_value: Current check value
            threshold: Threshold to check
            direction: 'remaining' (countdown) or 'elapsed' (count-up)
        
        Returns:
            True if threshold was crossed this iteration
        """
        if prev_value is None:
            return False
        
        if direction == 'remaining':
            # Countdown: crossed when we go from above to at/below threshold
            return prev_value > threshold >= curr_value
        else:  # elapsed
            # Count-up: crossed when we go from below to at/above threshold
            return prev_value < threshold <= curr_value
    
    def _format_number(self, num: float) -> str:
        """Format number with commas for readability."""
        if num >= 1000:
            return f"{int(num):,}"
        return str(int(num))
    
    def _format_percentage(self, pct: float) -> str:
        """Format percentage to 3 decimal places."""
        return f"{pct:.3f}"
    
    def _generate_progress_bar_10(self, percentage: float) -> str:
        """Generate 10-block progress bar."""
        filled = round(percentage / 10)
        filled = max(0, min(10, filled))  # Clamp to 0-10
        return '🟩' * filled + '⬜' * (10 - filled)
    
    def _generate_progress_bar_10x10(self, percentage: float) -> str:
        """Generate 10x10 grid progress bar (100 blocks total)."""
        filled = round(percentage)
        filled = max(0, min(100, filled))  # Clamp to 0-100
        
        lines = []
        for row in range(10):
            row_start = row * 10
            row_end = min(row_start + 10, filled)
            row_filled = max(0, row_end - row_start)
            row_empty = 10 - row_filled
            lines.append('🟩' * row_filled + '⬜' * row_empty)
        
        return '\n'.join(lines)
    
    def _format_tweet(self, milestone_type: str, value: float, remaining_seconds: float, elapsed_seconds: float, elapsed_percentage: float) -> str:
        """Format a milestone tweet."""
        
        if milestone_type == 'days_remaining':
            if value == 1:
                return "Ultimo dia."
            elif value == 100:
                return "Ultimos 100 dias."
            elif value == 365:
                return "Ya son menos de 365 dias. Falta menos de un ano."
            else:
                return f"Faltan {self._format_number(value)} dias."
        
        elif milestone_type == 'hours_remaining':
            return f"Faltan {self._format_number(value)} horas."
        
        elif milestone_type == 'minutes_remaining':
            return f"Faltan {self._format_number(value)} de minutos."
        
        elif milestone_type == 'seconds_remaining':
            if value == 66666666:
                return f"Faltan {self._format_number(value)} segundos. 😈"
            else:
                return f"Faltan {self._format_number(value)} segundos."
        
        elif milestone_type == 'years_remaining':
            return f"Faltan exactamente {int(value)} anos."
        
        elif milestone_type == 'days_elapsed':
            return f"Ya van {self._format_number(value)} dias."
        
        elif milestone_type == 'percentage':
            pct_str = self._format_percentage(value)
            
            # Special fraction cases
            if abs(value - 33.333) < 0.1:
                return f"Ya paso un tercio del sexenio.\n✅🔲🔲"
            elif abs(value - 66.666) < 0.1:
                return f"Ya pasaron dos tercios del sexenio.\n✅✅🔲"
            
            # Check if it's a multiple of 5 (major milestone)
            is_major = (value % 5 == 0)
            
            if value == 50:
                base = "Ya paso la mitad del sexenio."
            else:
                base = f"Ya paso {pct_str}% del sexenio."
            
            if is_major:
                # 10x10 grid for major milestones
                bar = self._generate_progress_bar_10x10(value)
                return f"{base}\n{bar}"
            else:
                # 10-block bar for regular milestones
                bar = self._generate_progress_bar_10(value)
                return f"{base}\n{bar}"
        
        elif milestone_type.startswith('approaching_'):
            # Approaching tweets
            base_type = milestone_type.replace('approaching_', '')
            
            if base_type == 'days_remaining':
                return f"Manana faltan {self._format_number(value)} dias."
            elif base_type == 'percentage':
                if value == 50:
                    return "Manana se cumple la mitad del sexenio."
                else:
                    return f"Manana ya paso {int(value)}% del sexenio."
            elif base_type == 'years_remaining':
                return f"Manana faltan exactamente {int(value)} anos."
            elif base_type == 'seconds_remaining':
                return f"Manana faltan {self._format_number(value)} de segundos."
            else:
                return f"Manana faltan {self._format_number(value)}."
        
        return f"Milestone: {milestone_type} = {value}"
    
    def _get_milestone_registry(self) -> List[Tuple[str, float, str]]:
        """Return list of (milestone_type, threshold_value, direction) tuples."""
        milestones = []
        
        # Remaining (countdown)
        days_remaining = [1500, 1000, 750, 500, 365, 300, 200, 100, 50, 30, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        for d in days_remaining:
            milestones.append(('days_remaining', d, 'remaining'))
        
        hours_remaining = [40000, 30000, 20000, 10000, 5000, 1000, 500, 100, 48, 24, 12]
        for h in hours_remaining:
            milestones.append(('hours_remaining', h, 'remaining'))
        
        minutes_remaining = [2000000, 1500000, 1000000, 500000, 100000, 10000, 1000]
        for m in minutes_remaining:
            milestones.append(('minutes_remaining', m, 'remaining'))
        
        # Seconds - every 10M
        seconds_10m = [100000000, 90000000, 80000000, 70000000, 60000000, 50000000, 40000000, 30000000, 20000000, 10000000]
        for s in seconds_10m:
            milestones.append(('seconds_remaining', s, 'remaining'))
        
        # Seconds - repeated digits
        seconds_repeated = [88888888, 77777777, 66666666, 55555555, 44444444, 33333333, 22222222, 11111111]
        for s in seconds_repeated:
            milestones.append(('seconds_remaining', s, 'remaining'))
        
        # Seconds - fun sequences
        seconds_fun = [123456789, 87654321, 12345678, 1234567]
        for s in seconds_fun:
            milestones.append(('seconds_remaining', s, 'remaining'))
        
        # Seconds - final millions
        seconds_final = [9000000, 8000000, 7000000, 6000000, 5000000, 4000000, 3000000, 2000000, 1000000]
        for s in seconds_final:
            milestones.append(('seconds_remaining', s, 'remaining'))
        
        years_remaining = [4, 3, 2, 1]
        for y in years_remaining:
            milestones.append(('years_remaining', y, 'remaining'))
        
        # Elapsed (count-up)
        days_elapsed = [100, 200, 365, 500, 730, 1000, 1500, 2000]
        for d in days_elapsed:
            milestones.append(('days_elapsed', d, 'elapsed'))
        
        # Percentage - major (multiples of 5)
        percentage_major = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]
        for p in percentage_major:
            milestones.append(('percentage', p, 'elapsed'))
        
        # Percentage - regular (every other integer 1-99, excluding multiples of 5)
        percentage_regular = [i for i in range(1, 100) if i % 5 != 0]
        # Also add 99
        if 99 not in percentage_regular:
            percentage_regular.append(99)
        for p in percentage_regular:
            milestones.append(('percentage', p, 'elapsed'))
        
        # Percentage - special fractions
        milestones.append(('percentage', 33.333, 'elapsed'))
        milestones.append(('percentage', 66.666, 'elapsed'))
        
        # Approaching tweets for major milestones
        # Days approaching
        for d in [1000, 500, 365, 100]:
            milestones.append(('approaching_days_remaining', d, 'remaining'))
        
        # Percentage approaching (all multiples of 5)
        for p in percentage_major:
            milestones.append(('approaching_percentage', p, 'elapsed'))
        
        # Years approaching
        for y in years_remaining:
            milestones.append(('approaching_years_remaining', y, 'remaining'))
        
        # Seconds approaching
        milestones.append(('approaching_seconds_remaining', 100000000, 'remaining'))
        
        return milestones
    
    def _convert_to_seconds(self, milestone_type: str, value: float, direction: str, remaining_seconds: float, elapsed_seconds: float) -> float:
        """Convert milestone value to seconds for comparison.
        
        For approaching tweets, add 1 day (86400 seconds) to the threshold.
        """
        if milestone_type.startswith('approaching_'):
            base_type = milestone_type.replace('approaching_', '')
            # Approaching tweets fire ~24h before, so add 1 day
            if base_type == 'days_remaining':
                return value * 86400 + 86400  # Add 1 day
            elif base_type == 'hours_remaining':
                return value * 3600 + 86400
            elif base_type == 'minutes_remaining':
                return value * 60 + 86400
            elif base_type == 'seconds_remaining':
                return value + 86400
            elif base_type == 'years_remaining':
                # Approximate: add 1 day to the year threshold
                return value * 365.25 * 86400 + 86400
            elif base_type == 'percentage':
                # Convert percentage to remaining seconds, subtract 1 day worth
                total_seconds = (self.end - self.start).total_seconds()
                elapsed_at_milestone = (value / 100) * total_seconds
                remaining_at_milestone = total_seconds - elapsed_at_milestone
                # Approaching fires 1 day before, so add 1 day to remaining
                return remaining_at_milestone + 86400
            else:
                return value + 86400
        
        # Regular milestones
        if milestone_type == 'days_remaining':
            return value * 86400
        elif milestone_type == 'hours_remaining':
            return value * 3600
        elif milestone_type == 'minutes_remaining':
            return value * 60
        elif milestone_type == 'seconds_remaining':
            return value
        elif milestone_type == 'years_remaining':
            return value * 365.25 * 86400  # Approximate
        elif milestone_type == 'days_elapsed':
            total_seconds = (self.end - self.start).total_seconds()
            return total_seconds - (value * 86400)  # Convert to remaining
        elif milestone_type == 'percentage':
            total_seconds = (self.end - self.start).total_seconds()
            return total_seconds - ((value / 100) * total_seconds)  # Convert to remaining
        else:
            return value
    
    def check_and_tweet(self, now: datetime.datetime):
        """Check for milestone crossings and tweet if any detected."""
        
        # Check cooldown
        if self.last_milestone_tweet_time is not None:
            time_since_last = (now - self.last_milestone_tweet_time).total_seconds()
            if time_since_last < COOLDOWN_SECONDS:
                return  # Still in cooldown
        
        # Calculate current values
        diff_time = self.end - now
        remaining_seconds = diff_time.total_seconds()
        
        elapsed_time = now - self.start
        elapsed_seconds = elapsed_time.total_seconds()
        
        total_sexenio_seconds = (self.end - self.start).total_seconds()
        elapsed_percentage = (elapsed_seconds / total_sexenio_seconds) * 100
        
        # Get all milestones
        milestones = self._get_milestone_registry()
        
        # Check each milestone
        for milestone_type, threshold_value, direction in milestones:
            # Check if already tweeted
            if (milestone_type, threshold_value) in self.tweeted_milestones:
                continue
            
            # Convert threshold to seconds for comparison
            threshold_seconds = self._convert_to_seconds(
                milestone_type, threshold_value, direction,
                remaining_seconds, elapsed_seconds
            )
            
            # All thresholds are converted to remaining_seconds for comparison
            # (elapsed milestones are converted to remaining in _convert_to_seconds)
            compare_value = remaining_seconds
            prev_compare_value = self.prev_remaining_seconds
            
            # For elapsed milestones, we still compare remaining_seconds (which decreases as elapsed increases)
            # The threshold_seconds already accounts for this conversion
            
            # Check if crossed
            if self._crossed_threshold(prev_compare_value, compare_value, threshold_seconds, direction):
                # Format and tweet
                tweet_text = self._format_tweet(
                    milestone_type, threshold_value,
                    remaining_seconds, elapsed_seconds, elapsed_percentage
                )
                
                # Log
                print(f"[MILESTONE] {milestone_type} = {threshold_value} at {now.isoformat()}")
                print(f"[TWEET] {tweet_text}")
                
                # Tweet (unless dry-run)
                if not DRY_RUN:
                    try:
                        self.client.create_tweet(text=tweet_text)
                        print(f"[SUCCESS] Tweeted milestone: {milestone_type} = {threshold_value}")
                    except Exception as e:
                        print(f"[ERROR] Failed to tweet: {e}")
                
                # Mark as tweeted
                self.tweeted_milestones.add((milestone_type, threshold_value))
                self._save_persistence(milestone_type, threshold_value)
                
                # Update cooldown
                self.last_milestone_tweet_time = now
                
                # Break to avoid multiple tweets in same iteration (cooldown will handle rest)
                break
        
        # Update previous values for next iteration
        self.prev_remaining_seconds = remaining_seconds
        self.prev_elapsed_seconds = elapsed_seconds
