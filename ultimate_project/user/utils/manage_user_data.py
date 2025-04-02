import httpx
from django.http import HttpRequest, JsonResponse


async def get_user_info_w_username(username):
    """
    Get user information by username from the database API
    """
    try:
        async with httpx.AsyncClient() as client:
            
            response = await client.get(
                f"http://ctn_api_gateway:8005/api-database/player/?username={username}"
            )

            response_text = response.text  # For plain text responses
            print("\n get_user_info_w_username response: ", response_text, "\n", flush=True) #rm

            if response.status_code == 200:
                data = response.json()
                # Check if response is a list (direct array)
                if isinstance(data, list) and len(data) > 0:
                    return data[0]
                # Check if response has 'results' field (paginated)
                elif (
                    isinstance(data, dict)
                    and data.get("results")
                    and len(data["results"]) > 0
                ):
                    return data["results"][0]
            return None
    except Exception as e:
        print(f"Error getting user by username: {str(e)}", flush=True)
        return None
  
  
async def get_if_user_auth_w_username(username):
    """
    Get user information by username from the database API
    """
    try:
        async with httpx.AsyncClient() as client:
            
            response = await client.get(
                f"http://ctn_api_gateway:8005/api-database/player/?username={username}"
            )

            response_text = response.text  # For plain text responses
            print("\n get_user_info_w_username response: ", response_text, "\n", flush=True) #rm

            if response.status_code == 200:
                data = response.json()
                # Check if response is a list (direct array)
                if isinstance(data, list) and len(data) > 0:
                    return data[0]
                # Check if response has 'results' field (paginated)
                elif (
                    isinstance(data, dict)
                    and data.get("results")
                    and len(data["results"]) > 0
                ):
                    return data["results"][0]
            return None
    except Exception as e:
        print(f"Error getting user by username: {str(e)}", flush=True)
        return None


async def update_user_w_user_id(user_id, data):
    """
    Update user information in the database API
    """
    try:
        print(f"Updating user {user_id} with data: {data}", flush=True)
        async with httpx.AsyncClient() as client:
            # Set content-type header to application/json
            headers = {"Content-Type": "application/json"}

            # Make the PATCH request
            
            # NEED MOD THIS GO THROUGH FAST API
            response = await client.patch(
                f"http://databaseapi:8007/api-database/player/{user_id}/",
                json=data,
                headers=headers,
            )

            print(f"Update response status: {response.status_code}", flush=True)
            print(f"Update response content: {response.text}", flush=True)

            if response.status_code == 200:
                # Try to parse JSON response if available
                try:
                    result = response.json()
                    print(f"User updated successfully: {result}", flush=True)
                    return result
                except ValueError:
                    # If response is not JSON, return True to indicate success
                    print("User updated successfully (non-JSON response)", flush=True)
                    return {"success": True}

            # Log error details
            print(
                f"Error updating user: HTTP {response.status_code} - {response.text}",
                flush=True,
            )
            return None
    except Exception as e:
        print(f"Exception in update_user: {str(e)}", flush=True)
        return None
