"""
Redis Lua scripts for atomic operations.

These scripts ensure thread-safety and prevent race conditions in critical
operations like rate limiting and credit consumption.
"""

from typing import Any, List


class LuaScriptCache:
    """Cache for Lua script SHAs with automatic reload on NOSCRIPT errors."""

    def __init__(self, script: str):
        self._script = script
        self._sha = None

    def execute(self, redis_client, num_keys: int, *args) -> List[Any]:
        """
        Execute the Lua script with automatic SHA caching and reload.

        Args:
            redis_client: Redis client instance
            num_keys: Number of keys in args
            *args: Keys followed by arguments

        Returns:
            Script result
        """
        if self._sha is None:
            self._sha = redis_client.script_load(self._script)

        try:
            return redis_client.evalsha(self._sha, num_keys, *args)
        except Exception as e:
            if "NOSCRIPT" in str(e):
                self._sha = redis_client.script_load(self._script)
                return redis_client.evalsha(self._sha, num_keys, *args)
            raise

    def reset(self) -> None:
        """Reset cached SHA (useful for testing)."""
        self._sha = None


# Sliding window rate limiting using sorted sets
# This provides more accurate rate limiting than fixed buckets
# Returns: [current_count, is_allowed (1 or 0), retry_after_seconds]
SLIDING_WINDOW_RATE_LIMIT = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window_seconds = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local request_id = ARGV[4]

local window_start = now - window_seconds

-- Remove expired entries outside the sliding window
redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)

-- Count current entries in window
local current_count = redis.call('ZCARD', key)

if current_count >= limit then
    -- Rate limit exceeded - calculate retry_after
    local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
    local retry_after = 0
    if oldest and #oldest >= 2 then
        retry_after = math.ceil(tonumber(oldest[2]) + window_seconds - now)
        if retry_after < 0 then retry_after = 0 end
    end
    return {current_count, 0, retry_after}
end

-- Add new entry with current timestamp as score
redis.call('ZADD', key, now, request_id)
-- Set expiration to clean up old keys
redis.call('EXPIRE', key, window_seconds + 60)

return {current_count + 1, 1, 0}
"""


# Atomic credit consumption
# Checks balance before decrementing to prevent overdraft
# Returns: [new_balance, success (1 or 0)]
CONSUME_CREDIT = """
local key = KEYS[1]
local field = ARGV[1]

local current = redis.call('HGET', key, field)
current = tonumber(current) or 0

if current <= 0 then
    return {current, 0}
end

local new_balance = redis.call('HINCRBY', key, field, -1)
return {new_balance, 1}
"""


# Combined API key validation + rate limiting + credit consumption
# Single atomic operation for all auth checks
# Returns: [status_code, credits_remaining, rate_count, retry_after]
# status_code: 0=success, 1=invalid_key, 2=inactive_key, 3=no_credits, 4=rate_limited
VALIDATE_AND_CONSUME = """
local api_key_hash = KEYS[1]
local rate_limit_key = KEYS[2]

local limit = tonumber(ARGV[1])
local window_seconds = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local request_id = ARGV[4]

-- Check API key exists
local is_active = redis.call('HGET', api_key_hash, 'is_active')
if not is_active then
    return {1, 0, 0, 0}  -- invalid_key
end

-- Check if active
if is_active ~= '1' then
    return {2, 0, 0, 0}  -- inactive_key
end

-- Check credits
local credits = tonumber(redis.call('HGET', api_key_hash, 'credits')) or 0
if credits <= 0 then
    return {3, credits, 0, 0}  -- no_credits
end

-- Rate limit check (sliding window)
local window_start = now - window_seconds
redis.call('ZREMRANGEBYSCORE', rate_limit_key, '-inf', window_start)
local current_count = redis.call('ZCARD', rate_limit_key)

if current_count >= limit then
    local oldest = redis.call('ZRANGE', rate_limit_key, 0, 0, 'WITHSCORES')
    local retry_after = 0
    if oldest and #oldest >= 2 then
        retry_after = math.ceil(tonumber(oldest[2]) + window_seconds - now)
        if retry_after < 0 then retry_after = 0 end
    end
    return {4, credits, current_count, retry_after}  -- rate_limited
end

-- All checks passed - consume credit and increment rate counter atomically
local new_credits = redis.call('HINCRBY', api_key_hash, 'credits', -1)
redis.call('ZADD', rate_limit_key, now, request_id)
redis.call('EXPIRE', rate_limit_key, window_seconds + 60)

return {0, new_credits, current_count + 1, 0}  -- success
"""


# Pre-configured script cache instances
sliding_window_script = LuaScriptCache(SLIDING_WINDOW_RATE_LIMIT)
consume_credit_script = LuaScriptCache(CONSUME_CREDIT)
validate_and_consume_script = LuaScriptCache(VALIDATE_AND_CONSUME)
