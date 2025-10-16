"""
security_dashboard.py
Simple dashboard to view security events.
"""

import os
from collections import Counter
from datetime import datetime, timedelta

def analyze_security_log():
    """Analyze security_log.txt and show stats."""
    
    if not os.path.exists("security_log.txt"):
        print("\n📊 No security log found yet.")
        print("Security events will be logged here as they occur.\n")
        return
    
    with open("security_log.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    if not lines:
        print("\n📊 Security log is empty.\n")
        return
    
    # Parse events
    events = []
    for line in lines:
        parts = line.strip().split(" | ")
        if len(parts) >= 3:
            timestamp, event_type, details = parts[0], parts[1], parts[2]
            events.append({
                'timestamp': timestamp,
                'type': event_type,
                'details': details
            })
    
    # Stats
    print("\n" + "="*70)
    print("🔒 SECURITY DASHBOARD")
    print("="*70 + "\n")
    
    print(f"📊 Total events logged: {len(events)}\n")
    
    # Event types
    event_types = Counter([e['type'] for e in events])
    print("📋 Event Types:")
    print("-" * 70)
    for event_type, count in event_types.most_common():
        percentage = (count / len(events)) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {event_type:30s} │ {count:3d} │ {bar} {percentage:.1f}%")
    
    # Time analysis
    print(f"\n\n📅 Timeline:")
    print("-" * 70)
    first_event = events[0]['timestamp']
    last_event = events[-1]['timestamp']
    print(f"  First event: {first_event}")
    print(f"  Last event:  {last_event}")
    
    # Recent events
    print(f"\n\n🕐 Recent Events (last 10):")
    print("-" * 70)
    for event in events[-10:]:
        timestamp = event['timestamp'].split('T')[1].split('.')[0] if 'T' in event['timestamp'] else event['timestamp']
        print(f"\n  ⏰ {timestamp}")
        print(f"     Type: {event['type']}")
        print(f"     Details: {event['details'][:80]}{'...' if len(event['details']) > 80 else ''}")
    
    # Security recommendations
    print("\n\n" + "="*70)
    print("💡 RECOMMENDATIONS")
    print("="*70)
    
    suspicious_count = sum(1 for e in events if 'INVALID' in e['type'] or 'INJECTION' in e['type'])
    if suspicious_count > 5:
        print("⚠️  HIGH: Multiple suspicious inputs detected")
        print("   → Review security_log.txt for patterns")
        print("   → Consider additional input validation")
    elif suspicious_count > 0:
        print("✓ MODERATE: Some suspicious inputs detected")
        print("   → Security measures are working as expected")
    else:
        print("✓ GOOD: No suspicious activity detected")
        print("   → Continue monitoring")
    
    rate_limit_hits = sum(1 for e in events if 'RATE_LIMIT' in e['type'])
    if rate_limit_hits > 0:
        print(f"\n⚠️  Rate limit hit {rate_limit_hits} time(s)")
        print("   → Consider adjusting limits if needed")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    try:
        analyze_security_log()
    except Exception as e:
        print(f"\n❌ Error analyzing security log: {e}\n")