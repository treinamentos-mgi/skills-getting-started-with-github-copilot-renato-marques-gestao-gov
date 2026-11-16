def test_get_activities_returns_available_activities(client, isolated_activities):
    # Arrange
    expected_activities = isolated_activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_get_root_redirects_to_activity_page(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_signup_adds_participant(client, isolated_activities):
    # Arrange
    activity_name = "Drama Club"
    email = "new-student@example.com"
    participants = isolated_activities[activity_name]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert participants == [email]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_participant(client, isolated_activities):
    # Arrange
    activity_name = "Drama Club"
    email = "already-signed-up@example.com"
    participants = isolated_activities[activity_name]["participants"]
    participants.append(email)

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert participants == [email]


def test_signup_rejects_full_activity(client, isolated_activities):
    # Arrange
    activity_name = "Drama Club"
    activity = isolated_activities[activity_name]
    activity["participants"] = [
        f"student-{number}@example.com"
        for number in range(activity["max_participants"])
    ]
    email = "new-student@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"
    assert len(activity["participants"]) == activity["max_participants"]
    assert email not in activity["participants"]


def test_signup_requires_email(client):
    # Arrange
    activity_name = "Drama Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422


def test_cancel_signup_removes_participant(client, isolated_activities):
    # Arrange
    activity_name = "Drama Club"
    email = "student@example.com"
    other_email = "another-student@example.com"
    participants = isolated_activities[activity_name]["participants"]
    participants.extend([email, other_email])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Canceled signup for {email} in {activity_name}"
    }
    assert participants == [other_email]


def test_cancel_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_cancel_signup_returns_not_found_for_unregistered_participant(
    client, isolated_activities
):
    # Arrange
    activity_name = "Drama Club"
    email = "not-signed-up@example.com"
    participants = isolated_activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert participants == []


def test_cancel_signup_requires_email(client):
    # Arrange
    activity_name = "Drama Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422