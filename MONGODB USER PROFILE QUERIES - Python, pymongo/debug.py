import os
from pymongo import MongoClient
from user_profiles import profiles
import datetime
import json

uri = os.environ["MONGODB_URI"]
client = MongoClient(uri)

db = client['SocialDB']
user_profiles = db['user_profiles']

def debug_dates():
    """Print all friends' addedDate values for direct verification."""
    print("\nAll users with friends' addedDate values:")
    for user in user_profiles.find({}, {"_id": 0, "personalInfo.firstName": 1, "activity.friends": 1}):
        print(json.dumps(user, indent=4, default=str))

def check_date_threshold():
    """Print and return the computed date threshold for last 4 weeks."""
    weeks = 4
    date_threshold = datetime.datetime.now() - datetime.timedelta(weeks=weeks)
    print("\nDate threshold for last 4 weeks:", date_threshold)
    return date_threshold

def test_query(date_threshold):
    """Run the query to find friends added recently and print results."""
    print("\nRunning the query...")
    query = {"activity.friends": {"$elemMatch": {"addedDate": {"$gt": date_threshold}}}}
    projection = {"_id": 0, "personalInfo.firstName": 1, "activity.friends": 1}

    results = []
    for user in user_profiles.find(query, projection):
        relevant_friends = [
            friend for friend in user["activity"]["friends"] if friend["addedDate"] > date_threshold
        ]
        results.append({
            "name": user["personalInfo"]["firstName"],
            "recentFriends": relevant_friends
        })

    print("\nResults:")
    print(json.dumps(results, indent=4, default=str))

def minimal_test_data():
    """Insert minimal test data into MongoDB for verification."""
    print("\nInserting minimal test data...")
    test_user = {
        "userId": "test",
        "personalInfo": {
            "firstName": "Test",
            "lastName": "User"
        },
        "activity": {
            "friends": [
                {"friendId": "1", "addedDate": datetime.datetime.now() - datetime.timedelta(days=10)},
                {"friendId": "2", "addedDate": datetime.datetime.now() - datetime.timedelta(days=50)}
            ]
        }
    }
    # Remove existing test user
    user_profiles.delete_one({"userId": "test"})
    # Insert the test user
    user_profiles.insert_one(test_user)
    print("Test user inserted.")

if __name__ == "__main__":
    # Step 1: Print all friends' addedDate values
    debug_dates()

    # Step 2: Compute the date threshold for 4 weeks
    date_threshold = check_date_threshold()

    # Step 3: Test the query with current data
    test_query(date_threshold)

    # Step 4: Insert minimal test data and rerun the query
    minimal_test_data()
    print("\nRerunning query with minimal test data...")
    test_query(date_threshold)