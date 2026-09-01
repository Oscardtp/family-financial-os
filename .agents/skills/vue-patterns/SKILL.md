---
name: vue-patterns
description: Vue.js 3 Composition API patterns, component architecture, reactivity best practices, Pinia state management, Vue Router navigation, and Nuxt SSR patterns. Activates for Vue, Nuxt, Vite, or Pinia projects. Use when building or reviewing Vue 3, Nuxt, or Pinia code — Composition API, reactivity, or router navigation.
origin: ECC
---

# Vue.js Patterns and Best Practices

Comprehensive guide for Vue.js 3 development using Composition API (`<script setup>`).

## Component Architecture

### Single-File Component Order
```vue
<script setup lang="ts">
// 1. Imports
// 2. Props & Emits & Slots
// 3. Composables
// 4. Local state (ref/reactive)
// 5. Computed properties
// 6. Methods
// 7. Watchers
// 8. Lifecycle hooks
</script>
```

### Props Best Practices
```ts
interface Props {
  label: string;
  variant?: "primary" | "secondary";
  disabled?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  variant: "primary",
  disabled: false,
});
```

## Composables (Reusable Logic)

```ts
export function useDebounce<T>(value: MaybeRef<T>, delay: number): Ref<T> {
  const debounced = ref(toValue(value)) as Ref<T>;
  let timer: ReturnType<typeof setTimeout>;
  watch(() => toValue(value), (newVal) => {
    clearTimeout(timer);
    timer = setTimeout(() => { debounced.value = newVal; }, delay);
  });
  onUnmounted(() => clearTimeout(timer));
  return readonly(debounced);
}
```

## Pinia State Management (Setup Store Preferred)

```ts
export const useCartStore = defineStore("cart", () => {
  const items = ref<CartItem[]>([]);
  const totalPrice = computed(() => items.value.reduce((sum, i) => sum + i.price * i.quantity, 0));
  async function addItem(productId: string) { /* ... */ }
  return { items, totalPrice, addItem };
});
```

## Vue Router

```ts
const routes = [{
  path: "/users/:id",
  name: "user-detail",
  component: () => import("@/pages/UserDetail.vue"),
  props: true,
  meta: { requiresAuth: true },
}];
```

## Performance Techniques

| Technique | When to Use |
|-----------|-------------|
| `v-memo` | List items that rarely change |
| `shallowRef()` | Large data structures replaced wholesale |
| `v-show` over `v-if` | Frequent visibility toggles |
| Lazy routes | `() => import(...)` for non-critical routes |

## Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| `v-if` + `v-for` on same element | Use computed filtered array |
| `v-for` key = index | Use stable database IDs |
| Mutating props | Emit events or use `v-model` |
| `v-html` with user content | Sanitize with DOMPurify |
| Mixins in Vue 3 | Replace with composables |
| Options API in new Vue 3 code | Use `<script setup>` |
