import { chromium } from '@playwright/test'

const BASE = 'http://localhost:5173'
const API = 'http://localhost:8000/api/v1'
const steps = []
let failed = false
let token = null

function step(name, ok, detail = '') {
  steps.push({ name, ok, detail })
  console.log(`${ok ? 'PASS' : 'FAIL'} | ${name}${detail ? ` | ${detail}` : ''}`)
  if (!ok) failed = true
}

async function section(label, fn) {
  try {
    await fn()
  } catch (e) {
    step(label, false, String(e && e.message ? e.message : e))
  }
}

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: 1280, height: 900 } })
const page = await context.newPage()
page.on('pageerror', e => console.log('PAGEERROR |', String(e.message).slice(0, 200)))

try {
  // ---------- setup: usuario + cuenta (via API, no UI) ----------
  const email = `hf4${Date.now()}@example.com`
  const password = 'password123'
  const reg = await fetch(`${API}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, name: 'HF4 Gate', password }),
  })
  const tokens = await reg.json()
  token = tokens.access_token
  step('setup: register usuario', reg.status === 201 && !!token, `status=${reg.status}`)

  const acc = await fetch(`${API}/accounts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ name: 'Cuenta HF4', type: 'bank', balance: 3000000 }),
  })
  step('setup: cuenta para pago programado', acc.status < 300, `status=${acc.status}`)

  // ---------- 1. LOGIN (UI) ----------
  await section('LOGIN: formulario completo', async () => {
    await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded' })
    await page.waitForSelector('#login-email', { timeout: 15000 })
    await page.fill('#login-email', email)
    await page.fill('#login-password', password)
    await page.click('form.login-form button[type="submit"]')
    await page.waitForURL(u => !String(u).includes('/login'), { timeout: 15000 })
    step('LOGIN: redirige a Resumen tras autenticar', page.url().replace(BASE, '') === '/', page.url())
    const hasErr = await page.locator('#login-error').count()
    step('LOGIN: sin mensaje de error', hasErr === 0, `errores=${hasErr}`)
  })

  // ---------- 2. DASHBOARD ----------
  await section('DASHBOARD: carga Resumen', async () => {
    await page.waitForSelector('.resumen-page', { timeout: 20000 })
    await page.waitForSelector('.budget-card', { timeout: 20000 })
    const title = await page.locator('.budget-card .bc-title').first().textContent().catch(() => '')
    step('DASHBOARD: BudgetCard visible', true, (title || '').trim())
  })

  // ---------- 3. CREAR DEUDA (UI) ----------
  await section('DEUDA: crear por UI', async () => {
    await page.goto(`${BASE}/debts`, { waitUntil: 'domcontentloaded' })
    const add = page.locator('button.btn-add')
    const addCount = await add.count()
    if (addCount) {
      await add.first().click()
    } else {
      await page.locator('button:has-text("Crear primera deuda")').first().click()
    }
    await page.waitForSelector('.modal-overlay', { timeout: 10000 })
    const nombre = `Deuda HF4 ${Date.now()}`
    await page.fill('#debt-name', nombre)
    await page.fill('#debt-creditor', 'Acreedor HF4')
    await page.fill('#debt-amount', '2500000')
    await page.fill('#debt-balance', '2500000')
    await page.fill('#debt-min-payment', '150000')
    await page.fill('#debt-interest-rate', '18.5')
    await page.click('form.debt-form button[type="submit"]')
    await page.waitForSelector('.debt-item', { timeout: 15000 })
    const found = await page.locator('.debt-item .debt-name', { hasText: nombre }).count()
    step('DEUDA: creada y visible en la lista', found > 0, `coincidencias=${found}`)

    const debts = await fetch(`${API}/debts`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json())
    step('DEUDA: persistida en API', Array.isArray(debts) && debts.length > 0, `count=${Array.isArray(debts) ? debts.length : 'n/a'}`)
  })

  // ---------- 4. CREAR PRESUPUESTO (UI, wizard) ----------
  await section('PRESUPUESTO: wizard por UI', async () => {
    await page.goto(`${BASE}/`, { waitUntil: 'domcontentloaded' })
    await page.waitForSelector('.budget-card', { timeout: 20000 })
    const empty = page.locator('.bc-empty-cta')
    if (await empty.count()) {
      await empty.first().click()
    } else {
      await page.locator('.bc-cta').first().click()
    }
    await page.waitForSelector('.bdm-modal', { timeout: 10000 })
    await page.waitForSelector('[data-testid="onboard-method"]', { timeout: 15000 })
    step('PRESUPUESTO: modal y hero abiertos', true)

    await page.click('[data-testid="onboard-method"]')
    await page.waitForSelector('[data-testid="recommended-methods"]', { timeout: 5000 })
    await page.locator('[data-testid="recommended-methods"] .bdm-method-card').first().click()
    await page.waitForSelector('#catalog-income', { timeout: 5000 })
    await page.fill('#catalog-income', '5000000')
    await page.click('[data-testid="preview-btn"]')
    await page.waitForSelector('[data-testid="method-preview"]', { timeout: 5000 })
    const sumOk = await page.locator('[data-testid="sum-display"]').textContent()
    step('PRESUPUESTO: preview 100%', (sumOk || '').includes('✓'), (sumOk || '').trim())
    await page.click('[data-testid="apply-method"]')
    await page.waitForSelector('[data-testid="cats-banner"]', { timeout: 5000 })
    const cont = page.locator('[data-testid="continue-btn"]').first()
    await cont.waitFor({ state: 'visible', timeout: 5000 })
    await cont.click()
    await page.waitForSelector('[data-testid="summary-budget-list"]', { timeout: 5000 })
    const createFinal = page.locator('[data-testid="create-budget-btn"]')
    await createFinal.waitFor({ state: 'visible', timeout: 5000 })
    step('PRESUPUESTO: botón Crear habilitado', !(await createFinal.isDisabled()))
    await createFinal.click()
    await page.waitForTimeout(1500)

    const budgets = await fetch(`${API}/budgets`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()).catch(() => [])
    step('PRESUPUESTO: persistido en API', Array.isArray(budgets) && budgets.length > 0, `count=${Array.isArray(budgets) ? budgets.length : 'n/a'}`)
    if (await page.locator('.bdm-close').count()) await page.locator('.bdm-close').click().catch(() => {})
  })

  // ---------- 5. PAGO PROGRAMADO (UI) ----------
  await section('PAGO PROGRAMADO: crear por UI', async () => {
    await page.goto(`${BASE}/`, { waitUntil: 'domcontentloaded' })
    await page.waitForSelector('.fab-button', { timeout: 15000 })
    await page.click('button.fab-button')
    await page.waitForSelector('.fab-modal', { timeout: 10000 })
    await page.click('button.type-btn.recurring')
    await page.waitForSelector('form.recurring-form', { timeout: 10000 })
    await page.fill('#recurring-amount', '120000')
    await page.fill('#recurring-name', `Netflix HF4 ${Date.now()}`)
    await page.click('button.submit-btn')
    await page.waitForSelector('.source-btn', { timeout: 10000 })
    await page.locator('.source-btn').first().click()
    await page.locator('button.confirm-btn').click()
    await page.waitForSelector('.done-confirmation', { timeout: 15000 })
    const done = await page.locator('.done-confirmation').textContent()
    step('PAGO PROGRAMADO: confirmación de activación', (done || '').includes('Listo'), (done || '').trim().slice(0, 80))

    const rec = await fetch(`${API}/recurring-payments`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()).catch(() => null)
    const n = Array.isArray(rec) ? rec.length : (rec && Array.isArray(rec.items) ? rec.items.length : 0)
    step('PAGO PROGRAMADO: persistido en API', n > 0, `count=${n}`)
  })
} catch (e) {
  step('E2E runtime error', false, String(e && e.message ? e.message : e))
  await page.screenshot({ path: 'e2e-gate-hf4-fail.png', fullPage: true }).catch(() => {})
} finally {
  await browser.close()
}

console.log('\n=== BROWSER GATE (HF4) SUMMARY ===')
console.log(`${steps.filter(s => s.ok).length}/${steps.length} pass`)
if (failed) process.exit(1)
