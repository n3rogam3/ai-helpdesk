# AI Helpdesk

Jednoducha sitova sluzba s AI endpointem.

## Autor
David Pantucek

## Popis
Aplikace obsahuje tri endpointy:

- `GET /ping` - vrati text `pong`
- `GET /status` - vrati JSON se stavem aplikace
- `POST /ai` - odesle prompt do AI modelu a vrati odpoved

## Pouzite technologie
- Python
- Flask
- Docker
- OpenAI-compatible API
- model `gemma3:27b`

## Endpointy

### GET /ping
Otestuje, jestli aplikace bezi.

Odpoved:
```text
pong