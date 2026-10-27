# Laadt de modellen voor de Examencoach vooraf in Ollama (keep-alive = -1, dus ze blijven geladen).
# Draait bij het inloggen van abusa via de geplande taak "Ollama-Warmup".
$ErrorActionPreference = 'Stop'
$base = 'http://localhost:11434'

# Wacht tot Ollama (tray-app) bereikbaar is, max. 5 minuten
$ok = $false
for ($i = 0; $i -lt 60 -and -not $ok; $i++) {
    try { Invoke-RestMethod "$base/api/version" | Out-Null; $ok = $true } catch { Start-Sleep 5 }
}
if (-not $ok) { exit 1 }

$gen = @{ model = 'huggingface.co/unsloth/gemma-3-12b-it-GGUF:latest'; prompt = 'hoi'; stream = $false; keep_alive = -1; options = @{ num_predict = 1 } } | ConvertTo-Json
Invoke-RestMethod "$base/api/generate" -Method Post -Body $gen -ContentType 'application/json' -TimeoutSec 300 | Out-Null

$emb = @{ model = 'nomic-embed-text:latest'; input = 'warmup'; keep_alive = -1 } | ConvertTo-Json
Invoke-RestMethod "$base/api/embed" -Method Post -Body $emb -ContentType 'application/json' -TimeoutSec 300 | Out-Null
