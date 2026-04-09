const input = `fetch('http://map.geoshare.com.cn:9080/kpi/devQualityDefect/page?page=1&pageSize=1&projectId=2029759625003290625&orderByField=updateTime&orderBy=desc', {
  "headers": {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "authorization": "Bearer eyJhbGciOiJIUzUxMiJ9...",
    "cache-control": "no-cache",
    "pragma": "no-cache"
  },
  "referrer": "http://map.geoshare.com.cn/",
  "body": null,
  "method": "GET",
  "mode": "cors",
  "credentials": "include"
})`;

function parseKeyValue(line) {
  const colonIdx = line.indexOf(':')
  if (colonIdx === -1) return null
  let key = line.substring(0, colonIdx).trim()
  let value = line.substring(colonIdx + 1).trim()
  if ((key.startsWith('"') && key.endsWith('"')) || (key.startsWith("'") && key.endsWith("'"))) {
    key = key.slice(1, -1)
  }
  if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
    value = value.slice(1, -1)
  }
  if ((value.endsWith('"') || value.endsWith("'")) && !value.startsWith('"') && !value.startsWith("'")) {
    value = value.slice(0, -1)
  }
  value = value.trim()
  if (!key) return null
  return { key, value }
}

const result = { method: 'GET', url: '', headers: {}, params: {}, body: null }

const urlMatch = input.match(/fetch\s*\(\s*['"]([^'"]+)['"]/)
if (urlMatch) result.url = urlMatch[1]
console.log('URL:', result.url)

const headersMatch = input.match(/"headers":\s*\{([\s\S]*?)\}(?:\s*,\s*|\s*\})/i)
if (headersMatch) {
  const headersBlock = headersMatch[1]
  const lines = headersBlock.split('\n')
  for (const rawLine of lines) {
    const line = rawLine.trim().replace(/,\s*$/, '')
    if (!line) continue
    const kv = parseKeyValue(line)
    if (kv) {
      result.headers[kv.key] = kv.value
    }
  }
}
console.log('Headers:', JSON.stringify(result.headers, null, 2))

if (result.url && result.url.includes('?')) {
  const [baseUrl, queryString] = result.url.split('?')
  result.url = baseUrl
  queryString.split('&').forEach(pair => {
    const [k, ...vParts] = pair.split('=')
    if (k) result.params[decodeURIComponent(k)] = decodeURIComponent(vParts.join('=') || '')
  })
}
console.log('After URL parse - url:', result.url)
console.log('Params:', JSON.stringify(result.params, null, 2))
