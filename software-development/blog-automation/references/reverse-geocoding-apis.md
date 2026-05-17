# Reverse Geocoding APIs for Photo Location Display

**Problem:** GPS coordinates shown in Telegram messages (e.g., "📍 37.6873, 127.1336") are not user-friendly. User expects "송파구 잠실동" or similar place names.

**Root cause (insung-blog):**
- `src/photo/topic_planner.py` has `enrich_with_location()` method with Kakao API integration
- BUT: `enrich_with_location()` is NOT called in pipeline.py
- `_format_topic_message()` shows raw GPS coordinates instead of place names

---

## OpenStreetMap Nominatim (Recommended for Development)

**Why:** Free, no API key required, works immediately, supports Korean.

**Usage:**
```bash
# Reverse geocode (coordinates → address)
curl -s "https://nominatim.openstreetmap.org/reverse?format=json&lat=37.6873&lon=127.1336&zoom=18&accept-language=ko"
```

**Response:**
```json
{
  "display_name": "송산로, 별내동, 별내면, 남양주시, 경기도, 12095, 대한민국",
  "address": {
    "road": "송산로",
    "quarter": "별내동",
    "town": "별내면",
    "city": "남양주시",
    "province": "경기도",
    "country": "대한민국"
  }
}
```

**Python integration:**
```python
import urllib.request
import json

def reverse_geocode_osm(lat: float, lng: float) -> str:
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&zoom=18&accept-language=ko"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            addr = data.get("address", {})
            # Construct place name: region_2depth + region_3depth
            city = addr.get("city", addr.get("town", ""))
            quarter = addr.get("quarter", "")
            return f"{city} {quarter}".strip()
    except Exception as e:
        logger.warning(f"OSM 역지오코딩 실패: {e}")
        return ""
```

**Rate limiting:** ~1 request/second (official policy). OK for sporadic photo pipeline usage.

---

## Kakao Maps API (Recommended for Production)

**Pros:** Korean data most accurate, fast, free with daily quota
**Cons:** Requires API key registration at developers.kakao.com

**Key in .env:** `KAKAO_REST_API_KEY`

**Endpoint:** `https://dapi.kakao.com/v2/local/geo/coord2address.json?x={lng}&y={lat}`

**Python pattern (existing in `src/photo/topic_planner.py:240-278`):**
```python
def enrich_with_location_kakao(lat: float, lng: float) -> str:
    kakao_key = os.environ.get("KAKAO_REST_API_KEY")
    if not kakao_key:
        return ""
    
    url = f"https://dapi.kakao.com/v2/local/geo/coord2address.json?x={lng}&y={lat}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"KakaoAK {kakao_key}")
    
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        docs = data.get("documents", [])
        if docs:
            addr = docs[0].get("address", {})
            region = addr.get("region_2depth_name", "")  # 구/군
            region3 = addr.get("region_3depth_name", "")  # 읍/면/동
            return f"{region} {region3}".strip()
    return ""
```

**Key mapping (Kakao address structure):**
- `region_1depth_name`: 시/도 (e.g., 서울, 경기)
- `region_2depth_name`: 구/군 (e.g., 송파구, 남양주시)
- `region_3depth_name`: 읍/면/동 (e.g., 잠실동, 별내면)

---

## VWorld (국토교통부)

**Pros:** Government-run, Korean data, free
**Cons:** Key registration required at vworld.kr, documentation complexity

**Key required:** Service key from vworld.kr registration

**Endpoint:** `https://api.vworld.kr/req/data?service=data&request=getFeature&data=LT_C_ADSIDO_INFO&key={KEY}&geomFilter=POINT({lng},{lat})`

**Use case:** When government data source is required (public sector projects).

---

## Naver Maps API

**Pros:** Naver ecosystem integration
**Cons:** Paid (credit-based), requires separate account

**Not recommended** for insung-blog unless Naver-specific features are needed.

---

## Implementation Pattern for insung-blog

**Current state (buggy):**
```python
# src/photo/pipeline.py:395-408 (WRONG)
def _format_topic_message(group: PhotoGroup, topics: list[TopicIdea]) -> str:
    ...
    if group.location:
        lat, lng = group.location
        lines.append(f"📍 <code>{lat:.4f}, {lng:.4f}</code>")  # ← Not user-friendly
```

**Fix:**
1. Call reverse geocoding when formatting message
2. Use OSM for immediate fix (no key)
3. Switch to Kakao for production after key registration

```python
# src/photo/pipeline.py (CORRECTED)
import urllib.request
import json

def _reverse_geocode(lat: float, lng: float) -> str:
    """Try OSM first (no key), fallback to raw coords"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&zoom=18&accept-language=ko"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            addr = data.get("address", {})
            city = addr.get("city", addr.get("town", ""))
            quarter = addr.get("quarter", "")
            place = f"{city} {quarter}".strip()
            if place:
                return place
    except Exception as e:
        logger.debug(f"역지오코딩 실패: {e}")
    return f"{lat:.4f}, {lng:.4f}"  # Fallback to coords

def _format_topic_message(group: PhotoGroup, topics: list[TopicIdea]) -> str:
    ...
    if group.location:
        lat, lng = group.location
        place_name = _reverse_geocode(lat, lng)
        lines.append(f"📍 <code>{html.escape(place_name)}</code>")
```

**Verification:**
```bash
# Test reverse geocoding with actual coordinates from photos
.venv/bin/python -c "
import urllib.request, json
lat, lng = 37.68730833333333, 127.13359166666667
url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&zoom=18&accept-language=ko'
with urllib.request.urlopen(url, timeout=5) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print(data.get('display_name', ''))
"
```

---

## API Comparison Table

| API | Cost | Key Required | Accuracy | Speed | Production Use |
|-----|-------|--------------|-----------|--------|---------------|
| **OpenStreetMap Nominatim** | Free | No | Good | Medium | ✅ Dev/Testing |
| **Kakao Maps** | Free (with quota) | Yes | **Best (Korea)** | Fast | ✅ **Production** |
| **VWorld** | Free | Yes | Good | Medium | Gov projects |
| **Naver Maps** | Paid | Yes | **Best (Korea)** | Fast | Naver ecosystem |

---

## Common Pitfalls

1. **Showing raw coordinates**: Users expect place names like "송파구 잠실동", not "37.6873, 127.1336". Always implement reverse geocoding before production.

2. **Not calling `enrich_with_location()`**: Method exists but unused. Check pipeline code for actual invocation.

3. **Rate limiting OSM**: OSM has ~1 req/sec limit. OK for daily photo pipeline but not for bulk processing.

4. **Kakao key not set**: Check `.env` has `KAKAO_REST_API_KEY` before production deployment.

5. **Language parameter missing**: Always add `accept-language=ko` for Korean addresses.

---

**Created:** 2026-05-14 (from user feedback on inaccurate location display)
