import httpx

async def fetch_random_users(count:int):
    
    url = f"https://randomuser.me/api/?results={count}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()  # Проверяет, что статус 2xx
            return response.json()
        except httpx.HTTPStatusError as exc:
            print(f"HTTP error occurred: {exc}")
    

def parse_user(user_data: dict) -> dict:
    return {
        "external_id": user_data.get("login", {}).get("uuid", "unknown"),
        "gender": user_data.get("gender", ""),
        "first_name": user_data.get("name", {}).get("first", ""),
        "last_name": user_data.get("name", {}).get("last", ""),
        "email": user_data.get("email", ""),
        "phone": user_data.get("phone", ""),
        "city": user_data.get("location", {}).get("city", ""),
        "country": user_data.get("location", {}).get("country", ""),
        "postcode": (user_data["location"]["postcode"]),
        "thumbnail": user_data.get("picture", {}).get("thumbnail", ""),
        'profile_url': f"/internal_user/{user_data['login']['uuid']}"
    }