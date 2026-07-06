---
name: api-documentation
description: Document an API with endpoints, parameters, request/response examples, status codes, and error handling
---

# API Documentation Prompt

Document the following API:

## API Overview
- **Name**: [API name]
- **Purpose**: [What it does]
- **Base URL**: [Endpoint]
- **Authentication**: [Auth method]

## Endpoints to Document

For each endpoint:

### `METHOD /path`

**Description**: What this endpoint does

**Authentication**: Required? What type?

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| param1 | string | yes | Description |
| param2 | int | no | Description |

**Request Body** (if applicable):
```json
{
  "field1": "value",
  "field2": 123
}
```

**Response**:
```json
{
  "status": "success",
  "data": {}
}
```

**Status Codes**:
- `200`: Success
- `400`: Bad request
- `401`: Unauthorized
- `404`: Not found
- `500`: Server error

**Example**:
```bash
curl -X POST https://api.example.com/endpoint \
  -H "Authorization: Bearer token" \
  -d '{"field": "value"}'
```

**Error Handling**:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  }
}
```

## Deliverables

1. **Overview**: What the API does
2. **Authentication**: How to authenticate
3. **Endpoints**: Documented as above
4. **Error Codes**: All possible errors
5. **Rate Limits**: If applicable
6. **Changelog**: Recent changes

Use OpenAPI/Swagger format if appropriate.
