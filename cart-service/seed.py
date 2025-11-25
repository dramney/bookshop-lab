import redis

r = redis.Redis(host="cart-db", port=6379, decode_responses=True)

# Кошики для користувачів (user_id 1,2,3)
for user_id in [1,2,3]:
    r.hset(f"cart:{user_id}", mapping={"total": 0})

print("Cart DB seeded ✅")
