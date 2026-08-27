<template>
  <div class="household">
    <div
      v-if="loading"
      class="loading"
    >
      Cargando...
    </div>

    <template v-else>
      <div class="card">
        <h3>{{ household.name }}</h3>
        <p class="subtitle">
          {{ household.members?.length }} miembros
        </p>
      </div>

      <div class="card">
        <h3>Miembros</h3>
        <div class="members-list">
          <div
            v-for="m in household.members"
            :key="m.id"
            class="member-item"
          >
            <div class="member-info">
              <span class="member-name">{{ m.name }}</span>
              <span class="member-email">{{ m.email }}</span>
            </div>
            <div class="member-actions">
              <span
                class="role-badge"
                :class="'role-' + m.role"
              >{{ m.role }}</span>
              <select
                v-if="isOwner && m.id !== currentUserId"
                :value="m.role"
                class="role-select"
                @change="changeRole(m.id, $event.target.value)"
              >
                <option value="member">
                  Miembro
                </option>
                <option value="viewer">
                  Observador
                </option>
              </select>
              <button
                v-if="isOwner && m.id !== currentUserId"
                class="btn-sm btn-danger"
                @click="removeMember(m.id)"
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="isOwner"
        class="card"
      >
        <h3>Invitar Miembro</h3>
        <form
          class="invite-form"
          @submit.prevent="inviteMember"
        >
          <div class="form-row">
            <input
              v-model="inviteEmail"
              type="email"
              placeholder="Correo de la persona"
              required
            >
            <select v-model="inviteRole">
              <option value="member">
                Miembro
              </option>
              <option value="viewer">
                Observador
              </option>
            </select>
            <button
              type="submit"
              class="btn-primary"
              :disabled="inviting"
            >
              {{ inviting ? 'Invitando...' : 'Invitar' }}
            </button>
          </div>
          <p
            v-if="inviteError"
            class="error-text"
          >
            {{ inviteError }}
          </p>
          <p
            v-if="inviteSuccess"
            class="success-text"
          >
            {{ inviteSuccess }}
          </p>
        </form>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const auth = useAuthStore()
const loading = ref(true)
const household = ref({ name: '', members: [] })
const inviteEmail = ref('')
const inviteRole = ref('member')
const inviting = ref(false)
const inviteError = ref('')
const inviteSuccess = ref('')

const isOwner = computed(() => auth.user?.role === 'owner')
const currentUserId = computed(() => auth.user?.id)

async function loadHousehold() {
  loading.value = true
  try {
    const { data } = await api.get('/household')
    household.value = data
  } catch (e) { console.error(e) }
  loading.value = false
}

async function inviteMember() {
  inviting.value = true
  inviteError.value = ''
  inviteSuccess.value = ''
  try {
    const { data } = await api.post('/household/invite', {
      email: inviteEmail.value,
      role: inviteRole.value,
    })
    inviteSuccess.value = data.message
    inviteEmail.value = ''
    await loadHousehold()
  } catch (e) {
    inviteError.value = e.response?.data?.detail || 'No pudimos invitar. Intenta de nuevo.'
  }
  inviting.value = false
}

async function removeMember(userId) {
  if (!confirm('Eliminar este miembro del hogar?')) return
  try {
    await api.delete(`/household/members/${userId}`)
    await loadHousehold()
  } catch (e) {
    alert(e.response?.data?.detail || 'No pudimos eliminar. Intenta de nuevo.')
  }
}

async function changeRole(userId, role) {
  try {
    await api.put(`/household/members/${userId}/role`, { role })
    await loadHousehold()
  } catch (e) {
    alert(e.response?.data?.detail || 'No pudimos cambiar el rol. Intenta de nuevo.')
  }
}

onMounted(loadHousehold)
</script>

<style scoped>
.loading { text-align: center; padding: var(--space-2xl); color: var(--color-neutral-400); }
.card h3 { font-size: 0.95rem; font-weight: 600; color: var(--color-neutral-900); margin-bottom: var(--space-sm); }
.subtitle { font-size: 0.8rem; color: var(--color-neutral-500); }
.members-list { display: flex; flex-direction: column; gap: var(--space-sm); }
.member-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-sm) 0;
  border-bottom: 1px solid var(--color-neutral-100);
}
.member-name { font-size: 0.875rem; font-weight: 500; color: var(--color-neutral-800); display: block; }
.member-email { font-size: 0.75rem; color: var(--color-neutral-400); }
.member-actions { display: flex; align-items: center; gap: var(--space-sm); }
.role-badge {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-weight: 500;
  text-transform: capitalize;
}
.role-owner { background: var(--color-primary-100); color: var(--color-primary-700); }
.role-member { background: var(--color-neutral-100); color: var(--color-neutral-600); }
.role-viewer { background: var(--color-secondary-100); color: var(--color-secondary-700); }
.role-select {
  padding: 2px 6px;
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-sm);
  font-size: 0.7rem;
  background: var(--color-neutral-0);
  outline: none;
}
.role-select:focus { border-color: var(--color-primary-500); }
.btn-sm {
  font-size: 0.75rem;
  padding: 4px 10px;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
}
.btn-danger { background: var(--color-error-100); color: var(--color-error-600); }
.btn-danger:hover { background: var(--color-error-200); }
.invite-form { display: flex; flex-direction: column; gap: var(--space-sm); }
.form-row { display: flex; gap: var(--space-sm); }
.form-row input, .form-row select {
  padding: var(--space-sm) var(--space-md);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  outline: none;
  background: var(--color-neutral-0);
  color: var(--color-neutral-900);
}
.form-row input:focus, .form-row select:focus { border-color: var(--color-primary-500); }
.btn-primary {
  padding: var(--space-sm) var(--space-md);
  background: var(--color-primary-600);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  cursor: pointer;
  white-space: nowrap;
}
.btn-primary:hover { background: var(--color-primary-700); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.error-text { color: var(--color-error-500); font-size: 0.8rem; }
.success-text { color: var(--color-success-500); font-size: 0.8rem; }

@media (max-width: 640px) {
  .form-row {
    flex-direction: column;
  }
  .household {
    padding: 0;
  }
  .member-item {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-sm);
  }
  .member-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
