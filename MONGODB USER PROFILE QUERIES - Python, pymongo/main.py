import os
from pymongo import MongoClient
from user_profiles import profiles
import datetime
import json

uri = os.environ["MONGODB_URI"]
client = MongoClient(uri)

db = client['SocialDB']
user_profiles = db['user_profiles']

for user in profiles:
    result = user_profiles.update_one(
        {"userId": user["userId"]},  
        {"$set": user}, 
        upsert=True
    )
    print(f"Processed userId {user['userId']}: Matched {result.matched_count}, Modified {result.modified_count}")

# Query 1: Retrieve all users 
print("All users:")
all_users = [
    user for user in user_profiles.find({}, {"_id": 0, "personalInfo.firstName": 1, "personalInfo.lastName": 1, "contactInfo.email": 1})
]
print(json.dumps(all_users, indent=4))

# Query 2: Find users in California 
print("\nUsers living in California:")
query = {"contactInfo.address.state": "CA"}
users_in_california = [
    user for user in user_profiles.find(query, {"_id": 0, "personalInfo.firstName": 1, "personalInfo.lastName": 1, "contactInfo.address.city": 1})
]
print(json.dumps(users_in_california, indent=4))

# Query 3: Find friends added in the last 4 weeks 
print("\nUsers with friends added in the last 4 weeks:")
weeks = 4
date_threshold = datetime.datetime.now() - datetime.timedelta(weeks=weeks)

query = {"activity.friends": {"$elemMatch": {"addedDate": {"$gt": date_threshold}}}}
projection = {"_id": 0, "personalInfo.firstName": 1, "activity.friends": 1}

recent_friends = [
    {
        "name": user["personalInfo"]["firstName"],
        "recentFriends": [
            friend for friend in user["activity"]["friends"] if friend["addedDate"] > date_threshold
        ]
    }
    for user in user_profiles.find(query, projection)
]
print(json.dumps(recent_friends, indent=4, default=str))

# Query 4: Find users with active subscriptions
print("\nUsers with active subscriptions:")
today = datetime.datetime.now().strftime("%Y-%m-%d")
query = {"subscriptions.endDate": {"$gte": today}}
active_subscriptions = [
    user for user in user_profiles.find(query, {"_id": 0, "personalInfo.firstName": 1, "subscriptions.endDate": 1})
]
print(json.dumps(active_subscriptions, indent=4))

# Query 5: Find users with posts having more than 30 likes 
print("\nUsers with posts having more than 30 likes:")
query = {"activity.posts.likes": {"$gt": 30}}
popular_posts = [
    {
        "name": user["personalInfo"]["firstName"],
        "popularPosts": [post for post in user["activity"]["posts"] if post["likes"] > 30]
    }
    for user in user_profiles.find(query, {"_id": 0, "personalInfo.firstName": 1, "activity.posts": 1})
]
print(json.dumps(popular_posts, indent=4))

# Query 6: Find users with Premium plan and over 2 friends
print("\nUsers with 'Premium' plan and more than 2 friends:")
query = {
    "subscriptions.plan": "Premium",
    "$expr": {"$gt": [{"$size": "$activity.friends"}, 2]}
}
premium_and_friends = [
    {
        "name": user["personalInfo"]["firstName"],
        "friendCount": len(user["activity"]["friends"])
    }
    for user in user_profiles.find(query, {"_id": 0, "personalInfo.firstName": 1, "activity.friends": 1})
]
print(json.dumps(premium_and_friends, indent=4))