import requests
from auth_validators import verify_jwt

def delete_uuid(access_token):
    try:
        payload = verify_jwt(access_token)
        if payload:
            user_id = payload.get("user_id")
            # Clear the active session in the database
            requests.put(
                f"http://databaseapi:8007/api/player/{user_id}/uuid",
                json={"uuid": None},
                headers={"Content-Type": "application/json"},
            )
    except Exception as e:
        print(f"⚠️ Error clearing session during logout: {str(e)}", flush=True)


def update_uuid(uuid, user_id, process):
    try:
        session_response = requests.put(
            f"http://databaseapi:8007/api/player/{user_id}/uuid",
            json={"uuid": uuid},
            headers={"Content-Type": "application/json"},
        )
        if session_response.status_code != 200:
            print(
                f"⚠️ Failed to update UUID during {process}: {session_response.status_code}",
                flush=True,
            )
    except Exception as e:
        print(f"⚠️ Error updating UUID during {process}: {str(e)}", flush=True)