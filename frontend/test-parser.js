import { parseRequest } from './src/utils/parser.js'
const input = 'curl -X POST https://httpbin.org/post -H "Content-Type: application/json" -d \'{"name":"test"}\''
try {
  const r = parseRequest(input)
  console.log(JSON.stringify(r, null, 2))
} catch (e) {
  console.error('Error:', e.message)
}
