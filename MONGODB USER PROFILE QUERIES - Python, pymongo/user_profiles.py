from datetime import datetime

profiles = [
    {
        "userId": "1",
        "personalInfo": {
            "firstName": "Alice",
            "lastName": "Smith",
            "dateOfBirth": datetime(1995, 5, 20),
            "gender": "Female",
            "bio": "Lover of nature, photography, and coding.",
            "profilePicture": "https://example.com/profile_pictures/alice.jpg"
        },
        "contactInfo": {
            "email": "alice.smith@example.com",
            "phone": "+1-555-123-4567",
            "address": {
                "street": "123 Elm Street",
                "city": "New York",
                "state": "NY",
                "country": "USA"
            }
        },
        "accountSettings": {
            "privacyLevel": "Friends Only",
            "notifications": {
                "email": True,
                "sms": False,
                "push": True
            }
        },
        "activity": {
            "posts": [
                {
                    "postId": "101",
                    "content": "Had a great day at the park!",
                    "timestamp": datetime(2023, 11, 15, 14, 30),
                    "likes": 25,
                    "comments": [
                        {
                            "commentId": "201",
                            "userId": "2",
                            "text": "Glad you had fun!",
                            "timestamp": datetime(2023, 11, 15, 15, 0)
                        }
                    ]
                }
            ],
            "friends": [
                {"friendId": "2", "addedDate": datetime(2023, 6, 1)},
                {"friendId": "3", "addedDate": datetime(2024, 3, 10)}
            ]
        },
        "subscriptions": [
            {
                "plan": "Premium",
                "startDate": datetime(2023, 1, 1),
                "endDate": datetime(2023, 12, 31)
            }
        ]
    },
    {
        "userId": "2",
        "personalInfo": {
            "firstName": "Bob",
            "lastName": "Johnson",
            "dateOfBirth": datetime(1990, 11, 10),
            "gender": "Male",
            "bio": "Tech enthusiast and travel lover.",
            "profilePicture": "https://example.com/profile_pictures/bob.jpg"
        },
        "contactInfo": {
            "email": "bob.johnson@example.com",
            "phone": "+1-555-234-5678",
            "address": {
                "street": "456 Maple Avenue",
                "city": "San Francisco",
                "state": "CA",
                "country": "USA"
            }
        },
        "accountSettings": {
            "privacyLevel": "Public",
            "notifications": {
                "email": True,
                "sms": True,
                "push": False
            }
        },
        "activity": {
            "posts": [
                {
                    "postId": "201",
                    "content": "Enjoying the sunny weather in SF!",
                    "timestamp": datetime(2024, 3, 1, 10, 0),
                    "likes": 15,
                    "comments": [
                        {
                            "commentId": "301",
                            "userId": "3",
                            "text": "Lucky you!",
                            "timestamp": datetime(2024, 3, 1, 11, 0)
                        }
                    ]
                }
            ],
            "friends": [
                {"friendId": "1", "addedDate": datetime(2023, 8, 15)},
                {"friendId": "4", "addedDate": datetime(2024, 2, 1)}
            ]
        },
        "subscriptions": [
            {
                "plan": "Basic",
                "startDate": datetime(2023, 1, 1),
                "endDate": datetime(2024, 1, 1)
            }
        ]
    },
    {
        "userId": "3",
        "personalInfo": {
            "firstName": "Charlie",
            "lastName": "Brown",
            "dateOfBirth": datetime(1988, 7, 15),
            "gender": "Non-Binary",
            "bio": "Aspiring developer and Python enthusiast.",
            "profilePicture": "https://example.com/profile_pictures/charlie.jpg"
        },
        "contactInfo": {
            "email": "charlie.brown@example.com",
            "phone": "+1-555-345-6789",
            "address": {
                "street": "789 Pine Lane",
                "city": "Los Angeles",
                "state": "CA",
                "country": "USA"
            }
        },
        "accountSettings": {
            "privacyLevel": "Only Me",
            "notifications": {
                "email": False,
                "sms": False,
                "push": True
            }
        },
        "activity": {
            "posts": [
                {
                    "postId": "301",
                    "content": "Just started learning Python, and I love it!",
                    "timestamp": datetime(2024, 5, 10, 18, 30),
                    "likes": 40,
                    "comments": [
                        {
                            "commentId": "401",
                            "userId": "1",
                            "text": "That’s awesome! Keep it up!",
                            "timestamp": datetime(2024, 5, 10, 19, 0)
                        }
                    ]
                }
            ],
            "friends": [
                {"friendId": "2", "addedDate": datetime(2023, 8, 10)}
            ]
        },
        "subscriptions": [
            {
                "plan": "Premium",
                "startDate": datetime(2023, 5, 1),
                "endDate": datetime(2025, 5, 1)
            }
        ]
    },
    {
        "userId": "4",
        "personalInfo": {
            "firstName": "Diana",
            "lastName": "Prince",
            "dateOfBirth": datetime(1992, 3, 21),
            "gender": "Female",
            "bio": "Coffee lover and avid traveler.",
            "profilePicture": "https://example.com/profile_pictures/diana.jpg"
        },
        "contactInfo": {
            "email": "diana.prince@example.com",
            "phone": "+1-555-456-7890",
            "address": {
                "street": "321 Oak Drive",
                "city": "Seattle",
                "state": "WA",
                "country": "USA"
            }
        },
        "accountSettings": {
            "privacyLevel": "Custom",
            "notifications": {
                "email": True,
                "sms": False,
                "push": True
            }
        },
        "activity": {
            "posts": [
                {
                    "postId": "401",
                    "content": "Loving the coffee culture here in Seattle.",
                    "timestamp": datetime(2024, 2, 14, 8, 0),
                    "likes": 35,
                    "comments": [
                        {
                            "commentId": "501",
                            "userId": "2",
                            "text": "Seattle does coffee best!",
                            "timestamp": datetime(2024, 2, 14, 9, 30)
                        }
                    ]
                }
            ],
            "friends": [
                {"friendId": "1", "addedDate": datetime(2023, 5, 10)},
                {"friendId": "3", "addedDate": datetime(2023, 12, 5)}
            ]
        },
        "subscriptions": [
            {
                "plan": "Standard",
                "startDate": datetime(2024, 1, 1),
                "endDate": datetime(2025, 1, 1)
            }
        ]
    },
    {
        "userId": "5",
        "personalInfo": {
            "firstName": "Ethan",
            "lastName": "Hunt",
            "dateOfBirth": datetime(1985, 12, 15),
            "gender": "Male",
            "bio": "Adventure seeker and action enthusiast.",
            "profilePicture": "https://example.com/profile_pictures/ethan.jpg"
        },
        "contactInfo": {
            "email": "ethan.hunt@example.com",
            "phone": "+1-555-567-8901",
            "address": {
                "street": "987 Mission Street",
                "city": "San Diego",
                "state": "CA",
                "country": "USA"
            }
        },
        "accountSettings": {
            "privacyLevel": "Friends Only",
            "notifications": {
                "email": True,
                "sms": True,
                "push": False
            }
        },
        "activity": {
            "posts": [
                {
                    "postId": "501",
                    "content": "Exploring the mountains today!",
                    "timestamp": datetime(2024, 1, 20, 7, 0),
                    "likes": 50,
                    "comments": []
                }
            ],
            "friends": [
                {"friendId": "4", "addedDate": datetime(2024, 1, 10)}
            ]
        },
        "subscriptions": [
            {
                "plan": "Premium",
                "startDate": datetime(2023, 1, 1),
                "endDate": datetime(2024, 1, 1)
            }
        ]
    },
    {
        "userId": "6",
        "personalInfo": {
            "firstName": "Fiona",
            "lastName": "Gallagher",
            "dateOfBirth": datetime(1993, 6, 10),
            "gender": "Female",
            "bio": "Entrepreneur and coffee enthusiast.",
            "profilePicture": "https://example.com/profile_pictures/fiona.jpg"
        },
        "contactInfo": {
            "email": "fiona.gallagher@example.com",
            "phone": "+1-555-678-1234",
            "address": {
                "street": "654 Willow Drive",
                "city": "Austin",
                "state": "TX",
                "country": "USA"
            }
        },
        "accountSettings": {
            "privacyLevel": "Custom",
            "notifications": {
                "email": False,
                "sms": True,
                "push": True
            }
        },
        "activity": {
            "posts": [
                {
                    "postId": "601",
                    "content": "Starting my new business venture today!",
                    "timestamp": datetime(2024, 4, 1, 12, 0),
                    "likes": 60,
                    "comments": []
                }
            ],
            "friends": [
                {"friendId": "5", "addedDate": datetime(2024, 2, 10)}
            ]
        },
        "subscriptions": [
            {
                "plan": "Basic",
                "startDate": datetime(2023, 3, 1),
                "endDate": datetime(2024, 3, 1)
            }
        ]
    },
    {
        "userId": "7",
        "personalInfo": {
            "firstName": "George",
            "lastName": "Miller",
            "dateOfBirth": datetime(1987, 4, 5),
            "gender": "Male",
            "bio": "Avid cyclist and environmental advocate.",
            "profilePicture": "https://example.com/profile_pictures/george.jpg"
        },
        "contactInfo": {
            "email": "george.miller@example.com",
            "phone": "+1-555-987-6543",
            "address": {
                "street": "432 Park Avenue",
                "city": "Los Angeles",
                "state": "CA",
                "country": "USA"
            }
        },
        "accountSettings": {
            "privacyLevel": "Friends Only",
            "notifications": {
                "email": False,
                "sms": True,
                "push": True
            }
        },
        "activity": {
            "posts": [],
            "friends": [
                {"friendId": "3", "addedDate": datetime(2024, 2, 15)},
                {"friendId": "4", "addedDate": datetime(2024, 2, 20)},
                {"friendId": "5", "addedDate": datetime(2024, 3, 1)}
            ]
        },
        "subscriptions": [
            {
                "plan": "Premium",
                "startDate": datetime(2023, 2, 1),
                "endDate": datetime(2024, 6, 1)
            }
        ]
    }
]
