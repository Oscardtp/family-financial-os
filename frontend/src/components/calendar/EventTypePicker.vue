<template>
  <div class="sheet-backdrop" @click.self="$emit('close')">
    <div class="sheet">
      <div class="drag-handle"></div>
      <button class="sheet-close" @click="$emit('close')" aria-label="Cerrar">
        <X :size="18" />
      </button>
      <h3 class="sheet-title">¿Qué quieres registrar?</h3>
      <div class="type-options">
        <button class="type-card type-card--expense" @click="$emit('select', 'expense')">
          <span class="type-icon-wrap type-icon-wrap--expense">
            <ArrowDownLeft :size="20" />
          </span>
          <span class="type-text">
            <span class="type-label">Gasto</span>
            <span class="type-desc">Lo que salió</span>
          </span>
        </button>
        <button class="type-card type-card--income" @click="$emit('select', 'income')">
          <span class="type-icon-wrap type-icon-wrap--income">
            <ArrowUpRight :size="20" />
          </span>
          <span class="type-text">
            <span class="type-label">Ingreso</span>
            <span class="type-desc">Lo que entró</span>
          </span>
        </button>
        <button class="type-card type-card--goal" @click="$emit('select', 'goal')">
          <span class="type-icon-wrap type-icon-wrap--goal">
            <Target :size="20" />
          </span>
          <span class="type-text">
            <span class="type-label">Meta</span>
            <span class="type-desc">Aportar a un objetivo</span>
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { X, ArrowDownLeft, ArrowUpRight, Target } from 'lucide-vue-next'
import './sheet-styles.css'

defineEmits(['select', 'close'])
</script>
