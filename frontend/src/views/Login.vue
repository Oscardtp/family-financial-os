<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <h1>Family Financial OS</h1>
        <p>{{ isLogin ? 'Inicia sesión en tu cuenta' : 'Crea tu cuenta' }}</p>
      </div>

      <form
        class="login-form"
        @submit.prevent="handleSubmit"
      >
        <div
          v-if="!isLogin"
          class="form-group"
        >
          <label>Nombre</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="Tu nombre"
            required
          >
        </div>
        <div class="form-group">
          <label>Email</label>
          <input
            v-model="form.email"
            type="email"
            placeholder="correo@ejemplo.com"
            required
          >
        </div>
        <div class="form-group">
          <label>Contraseña</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="Mínimo 6 caracteres"
            required
            minlength="6"
          >
        </div>

        <p
          v-if="auth.error"
          class="error-text"
        >
          {{ auth.error }}
        </p>

        <button
          type="submit"
          class="btn-primary"
          :disabled="auth.loading"
        >
          {{ auth.loading ? 'Cargando...' : (isLogin ? 'Iniciar Sesión' : 'Crear Cuenta') }}
        </button>
      </form>

      <div class="login-footer">
        <button
          class="btn-text"
          @click="isLogin = !isLogin"
        >
          {{ isLogin ? '¿No tienes cuenta? Regístrate' : '¿Ya tienes cuenta? Inicia sesión' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const isLogin = ref(true)
const form = reactive({ name: '', email: '', password: '' })

async function handleSubmit() {
  let ok
  if (isLogin.value) {
    ok = await auth.login(form.email, form.password)
  } else {
    ok = await auth.register(form.email, form.name, form.password)
  }
  if (ok) router.push('/')
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-neutral-50);
}

[data-theme="dark"] .login-page {
  background: var(--color-neutral-0);
}
.login-card {
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: var(--space-2xl);
  width: 100%;
  max-width: 400px;
}
.login-header {
  text-align: center;
  margin-bottom: var(--space-xl);
}
.login-header h1 {
  font-size: 1.5rem;
  color: var(--color-neutral-900);
  margin-bottom: var(--space-xs);
}
.login-header p {
  color: var(--color-neutral-500);
  font-size: 0.875rem;
}
.form-group {
  margin-bottom: var(--space-md);
}
.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-neutral-700);
  margin-bottom: var(--space-xs);
}
.form-group input {
  width: 100%;
  padding: var(--space-sm) var(--space-md);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  outline: none;
  transition: border-color var(--transition-fast);
  background: var(--color-neutral-50);
  color: var(--color-neutral-900);
}
.form-group input:focus {
  border-color: var(--color-primary-500);
}
.btn-primary {
  width: 100%;
  padding: var(--space-sm) var(--space-md);
  background: var(--color-primary-600);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--transition-fast);
}
.btn-primary:hover { background: var(--color-primary-700); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.error-text {
  color: var(--color-error-500);
  font-size: 0.8rem;
  margin-bottom: var(--space-sm);
}
.login-footer {
  text-align: center;
  margin-top: var(--space-md);
}
.btn-text {
  background: none;
  border: none;
  color: var(--color-primary-600);
  font-size: 0.8rem;
  cursor: pointer;
}
.btn-text:hover { text-decoration: underline; }

@media (max-width: 480px) {
  .login-card {
    padding: var(--spacing-lg);
    margin: var(--spacing-md);
  }
}
</style>
