#!/usr/bin/env python3
"""
Example showing how to use the StrideDB converter system.
"""

from stride.stridedb import StrideDBService, create_database, save_activity
from stride.strava.main import get_strava_activities


def main():
    """Example usage of the StrideDB system."""

    # 1. Create database
    create_database()

    # 2. Get raw Strava data
    raw_activities = get_strava_activities(per_page=1, page=1)
    raw_activity = raw_activities[0]

    # Get streams for the activity (you'd implement this in your Strava module)
    # raw_streams = get_strava_activity_streams(raw_activity.id, [StravaStreamType.HEARTRATE])
    raw_streams = []  # Placeholder

    # 3. Use service to convert and process
    service = StrideDBService()
    unified_activity = service.process_strava_data(raw_activity, raw_streams)

    # 4. Save to database
    saved_activity = save_activity(unified_activity)

    print(f"Saved activity: {saved_activity.id} from {saved_activity.source}")
    print(f"Distance: {saved_activity.distance}m")
    print(f"Streams: {len(saved_activity.streams or [])}")


if __name__ == "__main__":
    main()
